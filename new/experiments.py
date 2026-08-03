

import numpy as np

from circuit import (
    create_parametrized_circuit,
    initialize_simulation_state,
    evolve_simulation,
    build_noise_schedule,
    split_circuit_into_layers,
    evolve_one_layer,
    EPS_EXACT,
)
from information import collect_information, collect_information_light
from densitymatrix import (
    mps_to_dense, logarithmic_negativity, purity as dm_purity,
    von_neumann_entropy, operator_participation_ratio, operator_entanglement_entropy,
)


import time


def negativity_experiment(num_qubits, theta, depth, noise, eps, repeats,
                           cut=None, checkpoint_layers=None, seed=None):
   
    if cut is None:
        cut = num_qubits // 2
    subsystem = list(range(cut))

    qc = create_parametrized_circuit(num_qubits, theta, depth)
    layers = split_circuit_into_layers(qc)
    num_layers = len(layers)

    if checkpoint_layers is None:
        checkpoint_layers = [num_layers - 1]  # 0-indexed: last layer only

    dim = 2 ** num_qubits
    rho_accum = {li: np.zeros((dim, dim), dtype=np.complex128) for li in checkpoint_layers}
    bond_samples = {li: [] for li in checkpoint_layers}

    t_start = time.perf_counter()
    master_rng = np.random.default_rng(seed)
    for _ in range(repeats):
        psi = initialize_simulation_state(num_qubits)
        run_rng = np.random.default_rng(int(master_rng.integers(0, 2**31 - 1)))
        for layer_idx, layer in enumerate(layers):
            psi = evolve_one_layer(psi, layer, qc, p=noise, eps=eps, rng=run_rng)
            if layer_idx in rho_accum:
                bond_samples[layer_idx].append(psi.max_bond())
                vec = mps_to_dense(psi)
                rho_accum[layer_idx] += np.outer(vec, vec.conj())
    elapsed = time.perf_counter() - t_start

    history = []
    for layer_idx in sorted(rho_accum.keys()):
        rho = rho_accum[layer_idx] / repeats
        bonds = np.array(bond_samples[layer_idx])
        history.append({
            "layer": layer_idx + 1,
            "log_negativity": logarithmic_negativity(rho, num_qubits, subsystem),
            "purity": dm_purity(rho),
            "vn_entropy": von_neumann_entropy(rho),
            "operator_participation_ratio": operator_participation_ratio(rho, num_qubits, cut),
            "operator_entanglement_entropy": operator_entanglement_entropy(rho, num_qubits, cut),
            # single-trajectory bond dimension: comparison only, noise-blind.
            "bond_dimension_mean": float(bonds.mean()),
            "bond_dimension_max": float(bonds.max()),
            "wall_time_per_trajectory": elapsed / repeats,
        })
    return history


def negativity_saturation_scan(noise_values, num_qubits_list, depth, eps=EPS_EXACT,
                                trajectories_per_batch=15, batches=3, cut=None,
                                theta_repeats=1, seed=None):
   
    rng = np.random.default_rng(seed)
    negativity_table = {}
    purity_table = {}
    cost_table = {}
    op_entropy_table = {}
    bond_table = {}
    runtime_table = {}
    for N in num_qubits_list:
        dim = 2 ** N
        total_trajectories = theta_repeats * batches * trajectories_per_batch
        if total_trajectories < dim / 2:
            print(f"  WARNING: N={N} (Hilbert space dim={dim}) has only "
                  f"{total_trajectories} total trajectories per p point -- "
                  f"the operator-Schmidt cost proxy needs many more samples "
                  f"than negativity does to be reliable (it's sensitive to "
                  f"density-matrix reconstruction noise). Increase "
                  f"trajectories_per_batch/batches/theta_repeats for N={N}, "
                  f"or treat its cost_table/op_entropy_table numbers as "
                  f"indicative only.")
        thetas = [rng.uniform(0, np.pi, size=N * depth) for _ in range(theta_repeats)]
        ps, negs, errs, purs = [], [], [], []
        costs, cost_errs, opents, opent_errs, bonds, bond_errs, times = \
            [], [], [], [], [], [], []
        for p in noise_values:
            all_negs, all_purs, all_costs, all_opents, all_bonds, all_times = \
                [], [], [], [], [], []
            for theta in thetas:
                for _ in range(batches):
                    history = negativity_experiment(
                        N, theta, depth, p, eps, trajectories_per_batch,
                        cut=cut, seed=int(rng.integers(0, 2**31 - 1)),
                    )
                    last = history[-1]
                    all_negs.append(last["log_negativity"])
                    all_purs.append(last["purity"])
                    all_costs.append(last["operator_participation_ratio"])
                    all_opents.append(last["operator_entanglement_entropy"])
                    all_bonds.append(last["bond_dimension_mean"])
                    all_times.append(last["wall_time_per_trajectory"])
            ps.append(p)
            negs.append(float(np.mean(all_negs)))
            errs.append(float(np.std(all_negs)))
            purs.append(float(np.mean(all_purs)))
            costs.append(float(np.mean(all_costs)))
            cost_errs.append(float(np.std(all_costs)))
            opents.append(float(np.mean(all_opents)))
            opent_errs.append(float(np.std(all_opents)))
            bonds.append(float(np.mean(all_bonds)))
            bond_errs.append(float(np.std(all_bonds)))
            times.append(float(np.mean(all_times)))
        negativity_table[N] = (np.array(ps), np.array(negs), np.array(errs))
        purity_table[N] = (np.array(ps), np.array(purs))
        cost_table[N] = (np.array(ps), np.array(costs), np.array(cost_errs))
        op_entropy_table[N] = (np.array(ps), np.array(opents), np.array(opent_errs))
        bond_table[N] = (np.array(ps), np.array(bonds), np.array(bond_errs))
        runtime_table[N] = (np.array(ps), np.array(times))
    return (negativity_table, purity_table, cost_table, op_entropy_table,
            bond_table, runtime_table)


def estimate_injection_count(num_qubits, depth):
   
    return depth * (num_qubits + 2 * (num_qubits - 1))


# ---------------------------------------------------------------------------
# Phase 0: averaging
# ---------------------------------------------------------------------------

def run_single_experiment(num_qubits, theta, depth, noise=0.0, eps=1e-6,
                           rng=None, noise_schedule=None, light=True):
    """Run one noisy trajectory and return its per-layer metric history."""
    qc = create_parametrized_circuit(num_qubits, theta, depth)
    mps = initialize_simulation_state(num_qubits)
    collect_fn = collect_information_light if light else collect_information
    final_state, history = evolve_simulation(
        mps, qc, p=noise, eps=eps, rng=rng,
        noise_schedule=noise_schedule, collect_fn=collect_fn,
    )
    return history


def repeat_experiment(repeats, num_qubits, theta, depth, noise, eps,
                       seed=None, light=True):
    """Run many independent noisy trajectories for a fixed circuit (theta)."""
    rng = np.random.default_rng(seed)
    runs = []
    for _ in range(repeats):
        history = run_single_experiment(
            num_qubits, theta, depth, noise=noise, eps=eps, rng=rng, light=light
        )
        runs.append(history)
    return runs


def _aggregate_layer_histories(runs):

    num_layers = min(len(r) for r in runs)
    aggregated = []
    for layer_idx in range(num_layers):
        entropies = np.array([r[layer_idx]["entropy"] for r in runs])
        bonds = np.array([r[layer_idx]["bond_dimension"] for r in runs])
        largest_svs = np.array([r[layer_idx]["largest_sv"] for r in runs])
        ranks = np.array([r[layer_idx]["schmidt_rank"] for r in runs])
        aggregated.append({
            "layer": layer_idx + 1,
            "entropy_mean": float(entropies.mean()),
            "entropy_std": float(entropies.std()),
            "bond_dimension_mean": float(bonds.mean()),
            "bond_dimension_std": float(bonds.std()),
            "bond_dimension_max": float(bonds.max()),
            "largest_sv_mean": float(largest_svs.mean()),
            "largest_sv_std": float(largest_svs.std()),
            "schmidt_rank_mean": float(ranks.mean()),
            "n_trajectories": len(runs),
        })
    return aggregated


def averaged_experiment(repeats, num_qubits, theta, depth, noise, eps=EPS_EXACT,
                         seed=None):
   
    runs = repeat_experiment(repeats, num_qubits, theta, depth, noise, eps, seed=seed)
    return _aggregate_layer_histories(runs)


def theta_and_noise_averaged_experiment(num_qubits, depth, noise, eps=EPS_EXACT,
                                         theta_repeats=5, noise_repeats=20,
                                         seed=None):
   
    rng = np.random.default_rng(seed)
    per_theta_histories = []
    for _ in range(theta_repeats):
        theta = rng.uniform(0, np.pi, size=num_qubits * depth)
        history = averaged_experiment(
            noise_repeats, num_qubits, theta, depth, noise, eps,
            seed=int(rng.integers(0, 2**31 - 1)),
        )
        per_theta_histories.append(history)

    num_layers = min(len(h) for h in per_theta_histories)
    combined = []
    for layer_idx in range(num_layers):
        entropy_means = np.array([h[layer_idx]["entropy_mean"] for h in per_theta_histories])
        bond_means = np.array([h[layer_idx]["bond_dimension_mean"] for h in per_theta_histories])
        bond_maxes = np.array([h[layer_idx]["bond_dimension_max"] for h in per_theta_histories])
        combined.append({
            "layer": layer_idx + 1,
            # mean across circuit instances of the (already trajectory-averaged) entropy
            "entropy_mean": float(entropy_means.mean()),
            # std across circuit instances -> captures instance-to-instance variability,
            # separate from the trajectory noise captured in averaged_experiment's std
            "entropy_std": float(entropy_means.std()),
            "bond_dimension_mean": float(bond_means.mean()),
            "bond_dimension_std": float(bond_means.std()),
            "bond_dimension_max": float(bond_maxes.max()),
            "theta_repeats": theta_repeats,
            "noise_repeats": noise_repeats,
        })
    return combined


# ---------------------------------------------------------------------------
# Phase 1: entanglement collapse vs noise, multiple system sizes
# ---------------------------------------------------------------------------

def noise_scan_averaged(noise_values, num_qubits_list, depth, eps=EPS_EXACT,
                         theta_repeats=5, noise_repeats=20, seed=None):
   
    rng = np.random.default_rng(seed)
    results = {N: {} for N in num_qubits_list}
    for N in num_qubits_list:
        for p in noise_values:
            history = theta_and_noise_averaged_experiment(
                N, depth, p, eps=eps,
                theta_repeats=theta_repeats, noise_repeats=noise_repeats,
                seed=int(rng.integers(0, 2**31 - 1)),
            )
            results[N][p] = history
    return results


def saturation_entropy_table(results):
   
    table = {}
    for N, by_p in results.items():
        ps = sorted(by_p.keys())
        entropies = np.array([by_p[p][-1]["entropy_mean"] for p in ps])
        errs = np.array([by_p[p][-1]["entropy_std"] for p in ps])
        table[N] = (np.array(ps), entropies, errs)
    return table


# ---------------------------------------------------------------------------
# Phase 3: classical simulability boundary
# ---------------------------------------------------------------------------

def _paired_fidelity_run(num_qubits, theta, depth, noise, eps_reference,
                          eps_candidate, rng):
    
    from circuit import state_fidelity

    qc = create_parametrized_circuit(num_qubits, theta, depth)
    mps0 = initialize_simulation_state(num_qubits)
    schedule = build_noise_schedule(qc, noise, rng)

    psi_ref, _ = evolve_simulation(
        mps0, qc, eps=eps_reference, noise_schedule=schedule,
        collect_fn=collect_information_light,
    )
    psi_cand, hist_cand = evolve_simulation(
        mps0, qc, eps=eps_candidate, noise_schedule=schedule,
        collect_fn=collect_information_light,
    )

    fidelity = state_fidelity(psi_ref, psi_cand)
    max_bond = max(h["bond_dimension"] for h in hist_cand) if hist_cand else 1
    return fidelity, max_bond


def minimal_bond_for_fidelity(num_qubits, depth, noise, eps_candidates,
                               fidelity_threshold=0.99, repeats=10,
                               eps_reference=EPS_EXACT, seed=None):
    
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0, np.pi, size=num_qubits * depth)

    best = None  # (bond_dimension, eps, fidelity) for the loosest passing eps
    for eps_candidate in sorted(eps_candidates):
        fidelities = []
        bonds = []
        for _ in range(repeats):
            run_rng = np.random.default_rng(int(rng.integers(0, 2**31 - 1)))
            fid, bond = _paired_fidelity_run(
                num_qubits, theta, depth, noise, eps_reference, eps_candidate, run_rng
            )
            fidelities.append(fid)
            bonds.append(bond)
        mean_fid = float(np.mean(fidelities))
        mean_bond = float(np.mean(bonds))
        if mean_fid >= fidelity_threshold:
            best = (mean_bond, eps_candidate, mean_fid)
        else:
            # once fidelity drops below threshold, looser eps will only be worse
            break
    if best is None:
        # even the tightest candidate failed -- report it so the boundary
        # map still has a (worst-case) data point instead of a gap
        eps_candidate = min(eps_candidates)
        fidelities, bonds = [], []
        for _ in range(repeats):
            run_rng = np.random.default_rng(int(rng.integers(0, 2**31 - 1)))
            fid, bond = _paired_fidelity_run(
                num_qubits, theta, depth, noise, eps_reference, eps_candidate, run_rng
            )
            fidelities.append(fid)
            bonds.append(bond)
        best = (float(np.mean(bonds)), eps_candidate, float(np.mean(fidelities)))
    return best


def simulability_boundary_scan(num_qubits_list, noise_values, depth,
                                eps_candidates=None, fidelity_threshold=0.99,
                                repeats=10, seed=None):
    """Phase-3 headline scan: grid of (N, p) -> minimal bond dimension needed
    to hit fidelity_threshold against a near-exact reference simulation.

    Returns
    -------
    boundary[N][p] = (bond_dimension, eps_used, achieved_fidelity)
    """
    if eps_candidates is None:
        eps_candidates = [1e-8, 1e-6, 1e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2]

    rng = np.random.default_rng(seed)
    boundary = {N: {} for N in num_qubits_list}
    for N in num_qubits_list:
        for p in noise_values:
            result = minimal_bond_for_fidelity(
                N, depth, p, eps_candidates,
                fidelity_threshold=fidelity_threshold, repeats=repeats,
                seed=int(rng.integers(0, 2**31 - 1)),
            )
            boundary[N][p] = result
    return boundary



def epsilon_scan_averaged(eps_values, num_qubits, depth, theta_repeats=5,
                           noise_repeats=1, seed=None):
    """Truncation-only sweep at p=0: shows how much entropy/bond-dimension
    suppression comes from SVD compression alone, for comparison against the
    physical-noise curves from noise_scan_averaged.
    """
    rng = np.random.default_rng(seed)
    results = {}
    for eps in eps_values:
        history = theta_and_noise_averaged_experiment(
            num_qubits, depth, noise=0.0, eps=eps,
            theta_repeats=theta_repeats, noise_repeats=noise_repeats,
            seed=int(rng.integers(0, 2**31 - 1)),
        )
        results[eps] = history
    return results


# --- legacy single-trajectory helpers (debugging / quick look only) -------

def noise_scan(noise_values, num_qubits, theta, depth, eps=1e-6):
    results = {}
    for p in noise_values:
        history = run_single_experiment(num_qubits, theta, depth, noise=p, eps=eps)
        results[p] = history
    return results


def depth_scan(depths, num_qubits, noise=0.0, eps=1e-6):
    results = {}
    for depth in depths:
        theta_local = np.random.uniform(0, np.pi, size=num_qubits * depth)
        history = run_single_experiment(num_qubits, theta_local, depth, noise, eps)
        results[depth] = history
    return results


def qubit_scan(qubit_numbers, depth, noise, eps):
    results = {}
    for N in qubit_numbers:
        theta_local = np.random.uniform(0, np.pi, size=N * depth)
        history = run_single_experiment(N, theta_local, depth, noise, eps)
        results[N] = history
    return results