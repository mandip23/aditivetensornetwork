# Entanglement Collapse & Classical Simulability Boundary of Noisy Variational Quantum Circuits

> **Can realistic quantum noise destroy the quantum advantage of variational quantum circuits?**
>
> This project investigates where noisy variational quantum circuits transition from highly entangled quantum systems into states that become progressively easier to simulate classically.

---

# Overview

This repository studies the relationship between

- Quantum entanglement
- Noise
- Classical tensor-network simulation complexity

using Matrix Product States (MPS), mixed-state density matrices, logarithmic negativity, and operator-Schmidt analysis.

During this project, several commonly-used complexity measures were tested and systematically eliminated because they fail under stochastic Pauli trajectory simulations.

The work ultimately identifies **mixed-state logarithmic negativity** together with the **operator-Schmidt spectrum** as the correct quantities for studying entanglement collapse and classical simulability.

---

# Motivation

Many papers study

- Entanglement transitions
- Measurement-induced phase transitions
- Tensor-network simulation

However, an important practical question remains:

> **When does realistic hardware noise make a variational quantum circuit classically easy to simulate?**

This project approaches that question experimentally.

Instead of assuming a complexity measure is correct, multiple candidate measures are tested, validated, or rejected.

---

# Main Contributions

This work makes several methodological contributions.

## 1. Demonstrates why pure-state entropy fails

The first experiments reproduced an unexpected result:

Increasing the physical error rate produced almost **no change** in bipartite von Neumann entropy.

This was traced to a mathematical property of stochastic Pauli trajectory simulations.

Each sampled Pauli error is a **local unitary operation**, and local unitaries preserve the Schmidt spectrum of an individual pure trajectory.

Therefore

- Pure-state entropy remains constant
- Single-trajectory MPS bond dimension remains constant

even though physical noise is increasing.

This explains why many intuitive trajectory-based metrics become completely insensitive to noise.

---

## 2. Identifies the correct entanglement measure

Instead of analyzing individual trajectories,

the project reconstructs the mixed-state density matrix

\[
\rho=\sum_i p_i |\psi_i\rangle\langle\psi_i|
\]

from many noisy trajectories.

Quantum entanglement is then measured using

**Logarithmic Negativity**

which correctly detects mixed-state entanglement.

Unlike pure-state entropy,

negativity decreases smoothly as physical noise increases.

---

## 3. Identifies the correct classical simulation complexity measure

Several complexity measures were tested.

### Rejected

❌ Pure-state von Neumann entropy

❌ Single-trajectory MPS bond dimension

❌ Density-matrix rank

Each fails for a different physical reason.

---

### Correct

The operator-Schmidt spectrum of the density matrix provides a meaningful estimate of mixed-state simulation complexity.

Its participation ratio decreases together with logarithmic negativity.

This directly links

Quantum Entanglement

↓

Operator Complexity

↓

Tensor-Network Simulation Cost

---

## 4. Establishes the entanglement–simulability connection

Using the same reconstructed density matrices,

the project compares

- Logarithmic negativity
- Operator-Schmidt participation ratio

and finds a strong positive correlation.

As entanglement collapses,

the effective operator complexity also collapses,

indicating that noisy circuits become progressively easier to simulate classically.

---

# Experimental Workflow

```
Variational Quantum Circuit
            │
            ▼
Random Pauli Noise
            │
            ▼
Multiple Quantum Trajectories
            │
            ▼
Density Matrix Reconstruction
            │
            ▼
──────────────────────────────────────
│                                    │
│  Logarithmic Negativity            │
│  (Quantum Entanglement)            │
│                                    │
──────────────────────────────────────
            │
            ▼
Operator-Schmidt Decomposition
            │
            ▼
Participation Ratio
            │
            ▼
Estimated Classical Simulation Cost
```

---

# Figures

---

## Figure 1 — Entanglement Saturation

![Entropy Saturation](figures/saturation.png)

This verifies that the circuit reaches its maximum entanglement before measurements are taken.

### Observation

- Entanglement rapidly increases with circuit depth.
- Around 30–35 layers the entropy saturates.
- Increasing depth further produces almost no additional entanglement.
- Different noise levels reach almost the same saturation value.

### Conclusion

The circuits are sufficiently deep.

The absence of entropy collapse is **not** due to shallow circuits.

---

## Figure 2 — Pure-State Entropy Search (Negative Result)

![Search Mode](figures/search_mode.png)

This figure shows the original search using pure-state von Neumann entropy.

### Panel A

Entanglement vs. noise

Observation:

Almost perfectly flat.

Increasing physical noise does not reduce entropy.

---

### Panel B

Finite-size scaling

The scaling collapse fails.

The fitted exponent reaches the boundary of the search space,

indicating no genuine transition.

---

### Panel C

Collapse-cost landscape

No clear minimum exists.

The optimization simply sticks to the parameter boundaries.

---

### Conclusion

Pure-state entropy cannot detect entanglement collapse under stochastic Pauli trajectory simulations.

This negative result motivated the remainder of the project.

---

## Figure 3 — Correct Mixed-State Analysis

![Main Results](figures/main_results.png)

This figure summarizes the corrected mixed-state analysis.

---

### (a) Entanglement collapse vs. noise

Measured using logarithmic negativity.

Observation

- Entanglement decreases monotonically.
- Larger systems begin with larger entanglement.
- Increasing noise suppresses quantum correlations.

Conclusion

The mixed-state entanglement transition is clearly visible.

---

### (b) State purity

Purity rapidly decreases with noise.

Observation

- Noise converts pure quantum states into mixed states.
- The reconstructed density matrix behaves physically.

This validates the simulation.

---

### (c) Finite-size scaling

Finite-size scaling produces an interior optimum.

Unlike the entropy search,

the optimizer no longer sticks to parameter boundaries.

This indicates that the transition is now physically meaningful.

---

### (d) Operator-Schmidt participation ratio

This estimates mixed-state operator complexity.

Observation

As noise increases,

the participation ratio decreases.

Interpretation

The density matrix becomes progressively simpler,

making tensor-network simulation easier.

---

### (e) Entanglement versus simulation cost

This compares

- Logarithmic negativity
- Operator participation ratio

Observation

Both decrease together.

Conclusion

Quantum entanglement collapse is directly associated with reduced classical simulation complexity.

---

### (f) Single-trajectory bond dimension

Observation

Bond dimension remains essentially constant.

Interpretation

Single noisy trajectories remain highly entangled because every sampled Pauli error is a local unitary.

This confirms that trajectory bond dimension is not an appropriate complexity measure for this problem.

---



# Main Findings

- Pure-state entropy is completely insensitive to stochastic Pauli trajectory noise.
- Single-trajectory bond dimension is also noise-blind.
- Mixed-state logarithmic negativity correctly captures entanglement collapse.
- Operator-Schmidt participation ratio decreases with entanglement.
- Classical simulation complexity reduces as quantum entanglement disappears.
- The corrected finite-size scaling behaves consistently, unlike the original entropy-based analysis.

---

# Scientific Significance

This work demonstrates that selecting the wrong metric can completely hide the physics of noisy quantum circuits.

Rather than introducing a new simulation algorithm, it establishes **which quantities should and should not be used** when studying entanglement collapse in stochastic trajectory simulations.

The results provide a practical framework for connecting

- quantum entanglement,
- mixed-state physics,
- and classical tensor-network simulation complexity.

---

