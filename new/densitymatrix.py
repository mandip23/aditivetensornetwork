

import numpy as np


def mps_to_dense(psi):
    """Dense, normalized state vector (2**N,) from a quimb MPS."""
    vec = np.asarray(psi.to_dense()).reshape(-1)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec


def partial_transpose(rho, num_qubits, subsystem_qubits):
    
    dim = 2 ** num_qubits
    rho_tensor = rho.reshape([2] * num_qubits + [2] * num_qubits)
    axes = list(range(2 * num_qubits))
    for q in subsystem_qubits:
        row_idx, col_idx = q, num_qubits + q
        axes[row_idx], axes[col_idx] = axes[col_idx], axes[row_idx]
    return rho_tensor.transpose(axes).reshape(dim, dim)


def logarithmic_negativity(rho, num_qubits, subsystem_qubits):
   
    rho_pt = partial_transpose(rho, num_qubits, subsystem_qubits)
    eigvals = np.linalg.eigvalsh(rho_pt)
    trace_norm = np.sum(np.abs(eigvals))
    return float(np.log2(max(trace_norm, 1e-15)))


def negativity(rho, num_qubits, subsystem_qubits):
    
    rho_pt = partial_transpose(rho, num_qubits, subsystem_qubits)
    eigvals = np.linalg.eigvalsh(rho_pt)
    return float(np.sum(np.abs(eigvals[eigvals < 0])))


def purity(rho):
   
    return float(np.real(np.trace(rho @ rho)))


def von_neumann_entropy(rho):
    
    eigvals = np.linalg.eigvalsh(rho)
    eigvals = eigvals[eigvals > 1e-14]
    return float(-np.sum(eigvals * np.log2(eigvals)))


def effective_rank(rho, threshold=0.99):
    
    eigvals = np.linalg.eigvalsh(rho)
    eigvals = np.sort(eigvals)[::-1]
    eigvals = np.clip(eigvals, 0, None)
    total = eigvals.sum()
    if total <= 0:
        return len(eigvals)
    eigvals = eigvals / total
    cumulative = np.cumsum(eigvals)
    rank = int(np.searchsorted(cumulative, threshold) + 1)
    return rank


def operator_schmidt_spectrum(rho, num_qubits, cut):
    
    dimA = 2 ** cut
    dimB = 2 ** (num_qubits - cut)
    rho_tensor = rho.reshape(dimA, dimB, dimA, dimB)
    # realign (rowA, rowB, colA, colB) -> ((rowA,colA), (rowB,colB))
    M = rho_tensor.transpose(0, 2, 1, 3).reshape(dimA * dimA, dimB * dimB)
    return np.linalg.svd(M, compute_uv=False)


def operator_participation_ratio(rho, num_qubits, cut):
    
    sv = operator_schmidt_spectrum(rho, num_qubits, cut)
    w = sv ** 2
    total = w.sum()
    if total <= 0:
        return 1.0
    w = w / total
    return float(1.0 / np.sum(w ** 2))


def operator_entanglement_entropy(rho, num_qubits, cut):
    
    sv = operator_schmidt_spectrum(rho, num_qubits, cut)
    w = sv ** 2
    total = w.sum()
    if total <= 0:
        return 0.0
    w = w / total
    w = w[w > 1e-14]
    return float(-np.sum(w * np.log2(w)))