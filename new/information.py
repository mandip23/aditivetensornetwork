

import numpy as np


def get_entanglement_entropy(mps, cut=None):
    if cut is None:
        cut = mps.nsites // 2
    return mps.entropy(cut)


def get_schmidt_spectrum(mps, cut=None):
    if cut is None:
        cut = mps.nsites // 2
    schmidt = np.array(mps.schmidt_values(cut))
    return schmidt


def get_bond_dimension(mps):
    return mps.max_bond()


def get_schmidt_rank(mps, cut=None, tol=1e-12):
    s = get_schmidt_spectrum(mps, cut)
    return int(np.sum(s > tol))


def largest_schmidt_value(mps, cut=None):
    s = get_schmidt_spectrum(mps, cut)
    if len(s) == 0:
        return 0.0
    return float(np.max(s))


def schmidt_probabilities(mps, cut=None):
    s = get_schmidt_spectrum(mps, cut)
    p = s ** 2
    norm = np.sum(p)
    if norm > 0:
        p /= norm
    return p


def collect_information(mps):
    entropy = get_entanglement_entropy(mps)
    schmidt = get_schmidt_spectrum(mps)
    probabilities = schmidt_probabilities(mps)
    bond_dimension = get_bond_dimension(mps)
    schmidt_rank = get_schmidt_rank(mps)
    largest_sv = largest_schmidt_value(mps)

    return {
        "entropy": entropy,
        "bond_dimension": bond_dimension,
        "schmidt_rank": schmidt_rank,
        "largest_sv": largest_sv,
        "schmidt_values": schmidt,
        "probabilities": probabilities,
    }


def collect_information_light(mps):
    
    entropy = get_entanglement_entropy(mps)
    bond_dimension = get_bond_dimension(mps)
    s = get_schmidt_spectrum(mps)
    schmidt_rank = int(np.sum(s > 1e-12))
    largest_sv = float(np.max(s)) if len(s) else 0.0

    return {
        "entropy": entropy,
        "bond_dimension": bond_dimension,
        "schmidt_rank": schmidt_rank,
        "largest_sv": largest_sv,
    }