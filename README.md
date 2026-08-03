# Entanglement Collapse & Classical Simulability Boundary of Noisy Variational Quantum Circuits

> Investigating when noisy variational quantum circuits lose quantum advantage and become classically simulable.

---

## Overview

This project studies how **noise affects entanglement** in variational quantum circuits and how that relates to the **cost of classical tensor-network simulation**.

The project began by attempting to reproduce the commonly reported **entanglement-collapse transition** using standard pure-state trajectory simulations.

However, an unexpected result appeared:

- Entanglement entropy remained almost perfectly constant.
- Scaling-collapse analysis failed.
- No critical point could be identified.

Rather than treating this as a coding error, the project investigated **why** this happened.

This ultimately led to identifying which quantities are physically meaningful and which are fundamentally incapable of detecting entanglement collapse under stochastic Pauli trajectory simulations.

---

# Motivation

Many papers claim that increasing noise eventually destroys quantum entanglement, making quantum circuits easier to simulate classically.

The natural question is

> **Which physical quantity actually detects this transition?**

Several intuitive candidates exist:

- von Neumann entropy
- MPS bond dimension
- density matrix rank
- logarithmic negativity
- operator-Schmidt spectrum

This work systematically evaluates each of them.

---

# Main Contributions

This work demonstrates that **not every complexity measure is physically meaningful for noisy trajectory simulations.**

Specifically,

✔ Identified why pure-state entropy fails.

✔ Identified why single-trajectory bond dimension fails.

✔ Identified why density-matrix rank is misleading.

✔ Demonstrated that logarithmic negativity correctly captures mixed-state entanglement collapse.

✔ Proposed operator-Schmidt participation ratio as a physically meaningful proxy for classical simulation cost.

---

# Methodology

## Circuit

Hardware-efficient variational quantum circuit

- Random parameters
- Alternating rotation layers
- Entangling CNOT layers
- Depth increased until entanglement saturation

---

## Noise Model

Independent stochastic single-qubit depolarizing noise

After every gate,

- Identity
- X
- Y
- Z

are sampled according to probability

```
p
```

Many trajectories are averaged to reconstruct the mixed density matrix.

---

## Simulation

Tensor-network simulation using Matrix Product States (MPS)

Implemented with

- Quimb
- Adaptive MPS compression
- Monte Carlo trajectory averaging

---

# Metrics Investigated

---

## 1. Saturation Entropy

Measures bipartite von Neumann entropy of a **single trajectory**

### Observation

Entropy remained nearly constant over the entire noise range.

Example

```
N = 10

Noise = 0.00
Entropy ≈ 4.30

Noise = 0.035
Entropy ≈ 4.28
```

### Conclusion

Single-trajectory entropy is **noise blind** under stochastic Pauli trajectories because every sampled error is a **local unitary**, which preserves Schmidt coefficients.

Therefore

**Pure-state entropy cannot detect entanglement collapse.**

---

## 2. Scaling Collapse

Attempted finite-size scaling

```
S = f[(p-pc)N^(1/ν)]
```

### Observation

The optimizer repeatedly converged to the search boundary.

Example

```
ν = 0.10
```

(the minimum allowed value)

rather than a stable interior solution.

### Conclusion

No physical transition exists in the measured observable.

The failure originates from using an inappropriate metric rather than incorrect fitting.

---

## 3. State Purity

Mixed-state purity

```
Tr(ρ²)
```

was reconstructed from trajectory averaging.

### Observation

Purity decreases rapidly with increasing noise.

```
Pure state

↓

Mixed state
```

### Interpretation

Noise successfully converts the quantum state into a mixed state.

This validates the density-matrix reconstruction.

---

## 4. Logarithmic Negativity

Negativity measures genuine quantum entanglement of mixed states.

Unlike entropy, it ignores classical randomness.

### Observation

Negativity decreases monotonically with noise.

For all system sizes,

- high at p = 0
- rapid decay
- plateau at large noise

### Conclusion

Negativity correctly detects entanglement collapse.

---

## 5. Operator-Schmidt Participation Ratio

The density matrix itself can be viewed as an operator.

Performing a Schmidt decomposition on the density operator yields the operator-Schmidt spectrum.

From this spectrum,

the participation ratio estimates the effective operator complexity.

### Observation

Operator complexity decreases together with negativity.

### Interpretation

As entanglement disappears,

the density matrix becomes easier to represent,

implying reduced classical simulation complexity.

---

## 6. Single-Trajectory Bond Dimension

The MPS bond dimension of individual trajectories was also monitored.

### Observation

Bond dimension remained completely flat across all noise values.

### Conclusion

Just like entropy,

single-trajectory bond dimension is invariant under local Pauli errors.

Therefore it cannot measure noise-induced simplification.

---

# Experimental Results

## Figure 1 — Entanglement Collapse

Negativity decreases smoothly with increasing physical error rate.

This demonstrates genuine mixed-state entanglement destruction.

---

## Figure 2 — State Purity

Purity rapidly decreases.

The reconstructed state evolves from

```
Pure

↓

Mixed
```

as expected for depolarizing noise.

---

## Figure 3 — Scaling Collapse

Finite-size scaling was explored.

The obtained critical parameters provide an estimate of the transition region, although larger system sizes are required for reliable critical exponents.

---

## Figure 4 — Simulation Cost

Operator-Schmidt participation ratio decreases together with negativity.

This indicates that quantum complexity and classical simulation cost collapse simultaneously.

---

## Figure 5 — Entanglement vs Simulation Cost

Negativity and operator complexity exhibit strong positive correlation.

This supports the hypothesis that

> **loss of entanglement coincides with increased classical simulability.**

---

## Figure 6 — Bond Dimension Comparison

Single-trajectory MPS bond dimension remains constant.

This experimentally demonstrates that it is not an appropriate complexity measure for stochastic Pauli trajectory simulations.

---

# Important Scientific Findings

## Finding 1

Single-trajectory von Neumann entropy is fundamentally incapable of detecting entanglement collapse under stochastic Pauli noise.

---

## Finding 2

Single-trajectory MPS bond dimension is equally insensitive.

---

## Finding 3

Density-matrix rank is not a meaningful simulation-cost metric because highly mixed states possess maximal rank while remaining easy to represent.

---

## Finding 4

Logarithmic negativity correctly captures mixed-state entanglement degradation.

---

## Finding 5

Operator-Schmidt participation ratio provides a meaningful proxy for classical simulation complexity.

---

## Finding 6

Entanglement collapse and simulation-cost reduction occur together.

This directly connects quantum correlations with tensor-network simulation efficiency.

---

# Key Takeaways

This project demonstrates that choosing the correct physical observable is essential.

Several intuitive quantities

- Entropy
- Bond Dimension
- Density Matrix Rank

appear reasonable but fail to describe the underlying physics.

Instead,

the combination of

- Mixed-state logarithmic negativity
- Operator-Schmidt participation ratio

provides a consistent picture of both

- entanglement collapse
- classical simulability.

---

# Future Work

- Larger qubit systems
- More Monte Carlo trajectories
- MPO-based mixed-state simulations
- Adaptive tensor-network compression
- Hardware validation on noisy quantum processors
- Comparison with Haar-random circuit transitions

---

# Technologies

- Python
- NumPy
- SciPy
- Quimb
- Matplotlib
- Tensor Networks
- Matrix Product States (MPS)

---



# License

MIT License
