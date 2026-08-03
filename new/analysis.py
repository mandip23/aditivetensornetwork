

import numpy as np


def _rescale(p_arr, pc, nu, N):
    return (p_arr - pc) * (N ** (1.0 / nu))


def _collapse_cost(pc, nu, saturation_table, n_grid=200):
    
    rescaled = {}
    x_min, x_max = -np.inf, np.inf
    for N, (p_arr, S_arr, _err) in saturation_table.items():
        x = _rescale(p_arr, pc, nu, N)
        order = np.argsort(x)
        x_sorted, S_sorted = x[order], S_arr[order]
        rescaled[N] = (x_sorted, S_sorted)
        x_min = max(x_min, x_sorted.min())
        x_max = min(x_max, x_sorted.max())

    if not np.isfinite(x_min) or not np.isfinite(x_max) or x_min >= x_max:
        return np.inf  # candidate (pc, nu) gives no common overlap window

    grid = np.linspace(x_min, x_max, n_grid)
    curves = []
    for N, (x_sorted, S_sorted) in rescaled.items():
        curves.append(np.interp(grid, x_sorted, S_sorted))
    curves = np.array(curves)  # shape (num_N, n_grid)

    # mean squared deviation from the cross-N mean, at each grid point,
    # averaged over the grid -> single scalar cost
    spread = np.var(curves, axis=0)
    return float(np.mean(spread))


def scaling_collapse(saturation_table, pc_range=None, nu_range=None,
                      pc_steps=41, nu_steps=41):
    
    all_p = np.concatenate([p for p, _, _ in saturation_table.values()])
    if pc_range is None:
        pc_range = (float(all_p.min()) + 1e-6, float(all_p.max()) - 1e-6)
    if nu_range is None:
        nu_range = (0.5, 4.0)

    pc_values = np.linspace(pc_range[0], pc_range[1], pc_steps)
    nu_values = np.linspace(nu_range[0], nu_range[1], nu_steps)

    cost_grid = np.zeros((pc_steps, nu_steps))
    for i, pc in enumerate(pc_values):
        for j, nu in enumerate(nu_values):
            cost_grid[i, j] = _collapse_cost(pc, nu, saturation_table)

    best_i, best_j = np.unravel_index(np.argmin(cost_grid), cost_grid.shape)
    best_pc = float(pc_values[best_i])
    best_nu = float(nu_values[best_j])

    return {
        "best_pc": best_pc,
        "best_nu": best_nu,
        "cost_grid": cost_grid,
        "pc_values": pc_values,
        "nu_values": nu_values,
        "min_cost": float(cost_grid[best_i, best_j]),
    }


def collapsed_curves(saturation_table, pc, nu):
    """Return {N: (x_rescaled, S_arr)} for plotting the collapsed figure."""
    out = {}
    for N, (p_arr, S_arr, _err) in saturation_table.items():
        x = _rescale(p_arr, pc, nu, N)
        order = np.argsort(x)
        out[N] = (x[order], S_arr[order])
    return out


def bootstrap_pc_uncertainty(saturation_table, n_boot=50, seed=None,
                              pc_range=None, nu_range=None,
                              pc_steps=25, nu_steps=25):
    
    rng = np.random.default_rng(seed)
    pcs = []
    for _ in range(n_boot):
        resampled = {}
        for N, (p_arr, S_arr, err_arr) in saturation_table.items():
            noise = rng.normal(0.0, np.maximum(err_arr, 1e-6))
            resampled[N] = (p_arr, S_arr + noise, err_arr)
        result = scaling_collapse(
            resampled, pc_range=pc_range, nu_range=nu_range,
            pc_steps=pc_steps, nu_steps=nu_steps,
        )
        pcs.append(result["best_pc"])
    pcs = np.array(pcs)
    return float(pcs.mean()), float(pcs.std())