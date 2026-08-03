

import numpy as np
import matplotlib.pyplot as plt

from experiments import (
    noise_scan_averaged,
    saturation_entropy_table,
    simulability_boundary_scan,
    epsilon_scan_averaged,
    estimate_injection_count,
)
from analysis import scaling_collapse, collapsed_curves, bootstrap_pc_uncertainty
from plots import (
    plot_entropy_vs_noise_multi_N,
    plot_scaling_collapse,
    plot_collapse_cost_landscape,
    plot_simulability_heatmap,
    plot_epsilon_scan_averaged,
    plot_saturation_check,
)


QUICK_TEST = False   
SEARCH_MODE = True   
                     
RUN_PHASE_3_4 = not SEARCH_MODE  
                     

if QUICK_TEST:
    NUM_QUBITS_LIST = [8, 10, 12]
    DEPTH = 10
    _min_inj = estimate_injection_count(min(NUM_QUBITS_LIST), DEPTH)
    NOISE_VALUES = np.concatenate([[0.0], np.geomspace(0.3 / _min_inj, 8.0 / _min_inj, 5)])
    THETA_REPEATS = 2
    NOISE_REPEATS = 5
    BOUNDARY_N_LIST = NUM_QUBITS_LIST
    BOUNDARY_P_VALUES = NOISE_VALUES
    BOUNDARY_REPEATS = 3
    EPS_SCAN_VALUES = [1e-8, 1e-6, 1e-4, 1e-2]
    NU_RANGE = (0.5, 4.0)
elif SEARCH_MODE:
    
    NUM_QUBITS_LIST = [6, 8, 10]
    DEPTH = 18
    _min_inj = estimate_injection_count(min(NUM_QUBITS_LIST), DEPTH)
    NOISE_VALUES = np.concatenate([[0.0], np.geomspace(0.3 / _min_inj, 10.0 / _min_inj, 9)])
    THETA_REPEATS = 2
    NOISE_REPEATS = 4
    BOUNDARY_N_LIST = NUM_QUBITS_LIST
    BOUNDARY_P_VALUES = NOISE_VALUES
    BOUNDARY_REPEATS = 4
    EPS_SCAN_VALUES = [1e-8, 1e-6, 1e-4, 1e-2]
    NU_RANGE = (0.1, 6.0)
else:
    NUM_QUBITS_LIST = [6, 8, 10, 12]
    DEPTH = 30
    _min_inj = estimate_injection_count(min(NUM_QUBITS_LIST), DEPTH)
    NOISE_VALUES = np.concatenate([[0.0], np.geomspace(0.3 / _min_inj, 10.0 / _min_inj, 15)])
    THETA_REPEATS = 8
    NOISE_REPEATS = 50
    BOUNDARY_N_LIST = [6, 8, 10, 12]
    BOUNDARY_P_VALUES = NOISE_VALUES
    BOUNDARY_REPEATS = 15
    EPS_SCAN_VALUES = [1e-10, 1e-8, 1e-6, 1e-4, 1e-3, 1e-2]
    NU_RANGE = (0.1, 6.0)

SEED = 42


def run_phase1():
    print(f"[Phase 1] noise scan over N={NUM_QUBITS_LIST}, "
          f"{len(NOISE_VALUES)} noise points, depth={DEPTH} ...")
    results = noise_scan_averaged(
        NOISE_VALUES, NUM_QUBITS_LIST, DEPTH,
        theta_repeats=THETA_REPEATS, noise_repeats=NOISE_REPEATS, seed=SEED,
    )
    table = saturation_entropy_table(results)
    return results, table


def run_phase2(table):
    print("[Phase 2] finite-size scaling collapse ...")
    collapse_result = scaling_collapse(table, nu_range=NU_RANGE)
    curves = collapsed_curves(table, collapse_result["best_pc"], collapse_result["best_nu"])
    pc_mean, pc_std = None, None
    if not QUICK_TEST and not SEARCH_MODE:
       
        
        pc_mean, pc_std = bootstrap_pc_uncertainty(table, n_boot=30, seed=SEED)
    return collapse_result, curves, pc_mean, pc_std


def run_phase3(pc_estimate):
    print(f"[Phase 3] simulability boundary scan over N={BOUNDARY_N_LIST}, "
          f"{len(BOUNDARY_P_VALUES)} noise points ...")
    boundary = simulability_boundary_scan(
        BOUNDARY_N_LIST, BOUNDARY_P_VALUES, DEPTH,
        fidelity_threshold=0.99, repeats=BOUNDARY_REPEATS, seed=SEED,
    )
    return boundary


def run_phase4():
    print("[Phase 4] truncation-only sweep (appendix figure) ...")
    ref_N = NUM_QUBITS_LIST[len(NUM_QUBITS_LIST) // 2]
    results = epsilon_scan_averaged(
        EPS_SCAN_VALUES, ref_N, DEPTH,
        theta_repeats=THETA_REPEATS, noise_repeats=1, seed=SEED,
    )
    return results


def main():
    results1, table1 = run_phase1()
    collapse_result, curves, pc_mean, pc_std = run_phase2(table1)
    pc = collapse_result["best_pc"]
    nu = collapse_result["best_nu"]
    print(f"  -> best_pc = {pc:.4f}, best_nu = {nu:.2f}"
          + (f"  (bootstrap: pc = {pc_mean:.4f} +/- {pc_std:.4f})" if pc_mean else ""))

    # Diagnostic: is DEPTH actually deep enough that entropy has plateaued,
    # for the extremes of the p range we're scanning? Check the largest N.
    check_N = NUM_QUBITS_LIST[-1]
    check_ps = [NOISE_VALUES[0], NOISE_VALUES[len(NOISE_VALUES) // 2], NOISE_VALUES[-1]]
    fig_check, ax_check = plt.subplots(figsize=(7, 5))
    plot_saturation_check(results1, [check_N], check_ps, ax=ax_check)
    fig_check.tight_layout()
    fig_check.savefig("saturation_check.png", dpi=150)
    print(f"Saved saturation_check.png (N={check_N}, p={[f'{p:.3f}' for p in check_ps]})")

    if RUN_PHASE_3_4:
        boundary3 = run_phase3(pc)
        results4 = run_phase4()

        fig, axes = plt.subplots(2, 3, figsize=(19, 11))
        axes_flat = axes.flatten()
        plot_entropy_vs_noise_multi_N(table1, ax=axes_flat[0])
        plot_scaling_collapse(curves, pc, nu, ax=axes_flat[1])
        plot_collapse_cost_landscape(collapse_result, ax=axes_flat[2])
        plot_simulability_heatmap(boundary3, pc=pc, ax=axes_flat[3], value="bond_dimension")
        plot_simulability_heatmap(boundary3, pc=pc, ax=axes_flat[4], value="fidelity")
        plot_epsilon_scan_averaged(results4, ax=axes_flat[5])
    else:
        fig, axes = plt.subplots(1, 3, figsize=(19, 5.5))
        axes_flat = axes.flatten()
        plot_entropy_vs_noise_multi_N(table1, ax=axes_flat[0])
        plot_scaling_collapse(curves, pc, nu, ax=axes_flat[1])
        plot_collapse_cost_landscape(collapse_result, ax=axes_flat[2])

    fig.suptitle(
        "Entanglement Collapse & Classical Simulability Boundary "
        "of Noisy Variational Quantum Circuits"
        + ("  [SEARCH MODE]" if SEARCH_MODE else ""),
        fontsize=15, fontweight="bold", y=0.98,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    plt.subplots_adjust(hspace=0.4, wspace=0.3)

    out_path = "dashboard.png"
    fig.savefig(out_path, dpi=150)
    print(f"\nSaved dashboard to {out_path}")

    if QUICK_TEST:
        print("\nNOTE: QUICK_TEST=True -- these numbers are for pipeline "
              "sanity-checking only, not publication-quality statistics. "
              "Set QUICK_TEST=False and increase repeat counts / N range "
              "for real runs.")

    plt.show()


if __name__ == "__main__":
    main()