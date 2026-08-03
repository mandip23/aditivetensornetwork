import numpy as np
import matplotlib.pyplot as plt




def _get(h, key):
    return h[key + "_mean"] if (key + "_mean") in h else h[key]


def plot_entropy(history, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
    layers = [h["layer"] for h in history]
    entropy = [_get(h, "entropy") for h in history]
    ax.plot(layers, entropy, marker="o")
    if "entropy_std" in history[0]:
        err = [h["entropy_std"] for h in history]
        ax.fill_between(layers,
                         np.array(entropy) - np.array(err),
                         np.array(entropy) + np.array(err), alpha=0.2)
    ax.set_xlabel("Circuit Layer")
    ax.set_ylabel("Entanglement Entropy")
    ax.grid(True)


def plot_bond_dimension(history, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
    layers = [h["layer"] for h in history]
    bond = [_get(h, "bond_dimension") for h in history]
    ax.plot(layers, bond, marker="s", color="orange")
    ax.set_xlabel("Circuit Layer")
    ax.set_ylabel("Maximum Bond Dimension")
    ax.grid(True)


def plot_largest_schmidt(history, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
    layers = [h["layer"] for h in history]
    values = [_get(h, "largest_sv") for h in history]
    ax.plot(layers, values, marker="o", color="green")
    ax.set_xlabel("Layer")
    ax.set_ylabel("Largest Schmidt Value")
    ax.grid(True)


def plot_schmidt_spectrum(history, layer=-1, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
    s = history[layer]["schmidt_values"]
    ax.bar(np.arange(len(s)), s, color="purple")
    ax.set_xlabel("Schmidt Index")
    ax.set_ylabel("Singular Value")
    ax.grid(True)


# --- Diagnostic: has entropy actually saturated by the chosen depth? -------

def plot_saturation_check(results, N_list, p_list, ax=None):
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
    for N in N_list:
        for p in p_list:
            if N not in results or p not in results[N]:
                continue
            history = results[N][p]
            layers = [h["layer"] for h in history]
            entropy = [h["entropy_mean"] for h in history]
            ax.plot(layers, entropy, marker=".", label=f"N={N}, p={p:.3f}")
    ax.set_xlabel("Circuit layer")
    ax.set_ylabel("Entropy")
    ax.set_title("Saturation check: has entropy plateaued by max depth?")
    ax.legend(fontsize=8)
    ax.grid(True)


# --- Phase 1: entropy vs noise, multiple N ---------------------------------

def plot_entropy_vs_noise_multi_N(saturation_table, ax=None):
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
    for N in sorted(saturation_table.keys()):
        p_arr, S_arr, err = saturation_table[N]
        ax.errorbar(p_arr, S_arr, yerr=err, marker="o", label=f"N={N}", capsize=3)
    ax.set_xlabel("Physical error rate p")
    ax.set_ylabel("Saturation entanglement entropy")
    ax.set_title("Entanglement collapse vs. noise")
    ax.legend()
    ax.grid(True)


# --- Correct classical-cost proxy: operator-Schmidt spectrum of rho -------

def plot_operator_cost_vs_noise_multi_N(cost_table, ax=None):
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
    for N in sorted(cost_table.keys()):
        p_arr, cost_arr, err = cost_table[N]
        ax.errorbar(p_arr, cost_arr, yerr=err, marker="s", label=f"N={N}", capsize=3)
    ax.set_xlabel("Physical error rate p")
    ax.set_ylabel("Operator-Schmidt participation ratio")
    ax.set_title("Simulation cost vs. noise (correct: operator entanglement)")
    ax.legend()
    ax.grid(True)


def plot_bond_dimension_noise_blindness(bond_table, ax=None):
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
    for N in sorted(bond_table.keys()):
        p_arr, bond_arr, err = bond_table[N]
        ax.errorbar(p_arr, bond_arr, yerr=err, marker="x", linestyle="--",
                     label=f"N={N}", capsize=3)
    ax.set_xlabel("Physical error rate p")
    ax.set_ylabel("Single-trajectory MPS bond dimension")
    ax.set_title("Comparison: single-trajectory bond dim. is noise-blind")
    ax.legend()
    ax.grid(True)


def plot_runtime_vs_noise_multi_N(runtime_table, ax=None):
    """runtime_table: {N: (p_array, wall_time_array)}."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
    for N in sorted(runtime_table.keys()):
        p_arr, t_arr = runtime_table[N]
        ax.plot(p_arr, t_arr, marker="^", label=f"N={N}")
    ax.set_xlabel("Physical error rate p")
    ax.set_ylabel("Wall time per trajectory (s)")
    ax.set_title("Simulation runtime vs. noise (trajectory sampling only)")
    ax.legend()
    ax.grid(True)


def plot_negativity_vs_cost(negativity_table, cost_table, ax=None):
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
    for N in sorted(negativity_table.keys()):
        _, neg_arr, _ = negativity_table[N]
        _, cost_arr, _ = cost_table[N]
        order = np.argsort(neg_arr)
        ax.plot(neg_arr[order], cost_arr[order], marker="o", label=f"N={N}")
    ax.set_xlabel("Logarithmic negativity")
    ax.set_ylabel("Operator-Schmidt participation ratio")
    ax.set_title("Entanglement collapse <-> simulation cost collapse")
    ax.legend()
    ax.grid(True)


# --- Phase 1 (corrected): negativity vs noise, multiple N ------------------

def plot_negativity_vs_noise_multi_N(table, ax=None):
   
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
    for N in sorted(table.keys()):
        p_arr, neg_arr, err = table[N]
        ax.errorbar(p_arr, neg_arr, yerr=err, marker="o", label=f"N={N}", capsize=3)
    ax.set_xlabel("Physical error rate p")
    ax.set_ylabel("Saturation logarithmic negativity")
    ax.set_title("Entanglement collapse vs. noise (mixed-state, correct)")
    ax.axhline(0, color="gray", linestyle=":", linewidth=1)
    ax.legend()
    ax.grid(True)


def plot_purity_vs_noise_multi_N(purity_table, ax=None):
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
    for N in sorted(purity_table.keys()):
        p_arr, pur_arr = purity_table[N]
        ax.plot(p_arr, pur_arr, marker="o", label=f"N={N}")
    ax.set_xlabel("Physical error rate p")
    ax.set_ylabel("Purity Tr(rho^2)")
    ax.set_title("Sanity check: state purity vs. noise")
    ax.set_ylim(-0.02, 1.02)
    ax.legend()
    ax.grid(True)


# --- Phase 2: scaling collapse ---------------------------------------------

def plot_scaling_collapse(collapsed, pc, nu, ax=None):
   
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
    for N in sorted(collapsed.keys()):
        x, S = collapsed[N]
        ax.plot(x, S, marker="o", linestyle="-", label=f"N={N}")
    ax.set_xlabel(r"$(p - p_c)\, N^{1/\nu}$")
    ax.set_ylabel("Saturation entropy")
    ax.set_title(f"Scaling collapse  ($p_c$={pc:.4f}, $\\nu$={nu:.2f})")
    ax.legend()
    ax.grid(True)


def plot_collapse_cost_landscape(collapse_result, ax=None):
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
    pc_values = collapse_result["pc_values"]
    nu_values = collapse_result["nu_values"]
    cost = collapse_result["cost_grid"]
    im = ax.pcolormesh(nu_values, pc_values, cost, shading="auto")
    ax.scatter([collapse_result["best_nu"]], [collapse_result["best_pc"]],
               color="red", marker="x", s=80, label="best fit")
    ax.set_xlabel(r"$\nu$")
    ax.set_ylabel(r"$p_c$")
    ax.set_title("Collapse cost landscape")
    ax.legend()
    plt.colorbar(im, ax=ax, label="collapse cost")


# --- Phase 3: simulability boundary heatmap --------------------------------

def plot_simulability_heatmap(boundary, pc=None, ax=None, value="bond_dimension"):
   
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))

    N_values = sorted(boundary.keys())
    p_values = sorted(next(iter(boundary.values())).keys())
    idx = {"bond_dimension": 0, "eps": 1, "fidelity": 2}[value]

    grid = np.array([[boundary[N][p][idx] for p in p_values] for N in N_values])

    im = ax.pcolormesh(p_values, N_values, grid, shading="auto", cmap="viridis")
    plt.colorbar(im, ax=ax, label=value.replace("_", " "))
    if pc is not None:
        ax.axvline(pc, color="red", linestyle="--", label=r"$p_c$")
        ax.legend()
    ax.set_xlabel("Physical error rate p")
    ax.set_ylabel("Number of qubits N")
    ax.set_title(f"Classical simulability boundary ({value})")


# --- Phase 4 (appendix): truncation-only vs physical-noise comparison ------

def plot_epsilon_scan_averaged(results, ax=None):
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
    eps_vals = sorted(results.keys())
    final_entropy = [results[e][-1]["entropy_mean"] for e in eps_vals]
    ax.semilogx(eps_vals, final_entropy, marker="o", color="brown")
    ax.set_xlabel("SVD truncation cutoff (eps)")
    ax.set_ylabel("Saturation entropy (p=0)")
    ax.set_title("Truncation-only entropy suppression")
    ax.grid(True)