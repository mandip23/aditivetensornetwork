When Entanglement Entropy Fails
Identifying Reliable Complexity Measures for Noisy Variational Quantum Circuits
Abstract

Variational Quantum Circuits (VQCs) are among the leading candidates for near-term quantum computing. Their computational power relies heavily on quantum entanglement, making it essential to understand how realistic noise affects their complexity and classical simulability.

Many previous studies measure this complexity using pure-state quantities such as entanglement entropy or bond dimension. In this work we demonstrate that these quantities can become fundamentally misleading under stochastic Pauli trajectory simulations.

Instead of assuming a single complexity measure is sufficient, we systematically evaluate several candidate metrics and identify those that correctly capture mixed-state entanglement degradation and simulation complexity.

Motivation

The original objective was to locate an entanglement-collapse transition in noisy hardware-efficient variational quantum circuits.

Surprisingly, increasing physical noise produced almost no change in the commonly used entanglement entropy.

Rather than treating this as a numerical failure, we investigated the underlying reason and systematically tested multiple complexity measures.

This study therefore answers two questions:

Which commonly used complexity measures fail under stochastic Pauli noise?
Which quantities remain reliable indicators of mixed-state complexity?
Experimental Pipeline
Variational Quantum Circuit
        │
        ▼
Hardware-Efficient Brick-Wall Ansatz
        │
        ▼
Random Circuit Parameters
        │
        ▼
Depolarizing (Pauli) Noise
        │
        ▼
Trajectory Simulation
        │
        ▼
Density Matrix Reconstruction
        │
        ▼
Complexity Analysis

The following quantities are evaluated:

Bipartite Entanglement Entropy
Logarithmic Negativity
State Purity
MPS Bond Dimension
Operator-Schmidt Participation Ratio
Finite-Size Scaling
Main Results
Figure 1 – Initial Entropy Search

(Your first figure)

Entanglement entropy vs physical noise

Observation

Entanglement entropy remains nearly constant.
No observable entanglement transition appears.
Increasing physical noise has almost no effect.

Interpretation

Trajectory entanglement entropy is insensitive to stochastic Pauli noise.

Scaling collapse

Observation

The finite-size scaling fit converges to the boundary of parameter space.

Interpretation

No genuine critical collapse exists under this metric.

Collapse-cost landscape

Observation

The optimization landscape is nearly flat.

Interpretation

There is no meaningful critical point using trajectory entropy.

Figure 2 – Saturation Check

(Second figure)

This experiment verifies that the circuit depth is sufficient.

Observation

Entanglement increases steadily with circuit depth.
Around 30–35 layers the entropy reaches a stable plateau.
Different noise strengths converge to nearly identical saturation values.

Conclusion

The flat entropy curves are not caused by insufficient circuit depth.

The circuit is fully entangled before measurements are taken.

This experiment rules out one possible explanation for the entropy failure.

Figure 3 – Corrected Mixed-State Analysis

(Third figure)

This figure represents the main contribution of the project.

(A) Logarithmic Negativity

Measures genuine mixed-state quantum entanglement.

Observation

Negativity decreases monotonically as physical noise increases.
Larger systems begin with larger entanglement.
All system sizes exhibit entanglement degradation.

Conclusion

Unlike entropy, logarithmic negativity correctly detects the destruction of quantum entanglement by noise.

(B) State Purity

Measures how mixed the quantum state becomes.

Observation

Purity decreases rapidly with increasing noise.

Interpretation

The system evolves from an almost pure quantum state toward a mixed state.

This confirms that the applied noise model behaves physically.

(C) Finite-Size Scaling

Observation

After switching to logarithmic negativity, finite-size scaling becomes meaningful.

A critical noise scale

pc ≈ 0.028

is obtained together with

ν ≈ 4.23

Although additional system sizes are required for a precise estimate, the collapse now behaves consistently.

(D) Operator-Schmidt Participation Ratio

Measures effective operator complexity.

Observation

Operator complexity changes significantly with physical noise.

Interpretation

Unlike entropy or bond dimension, operator complexity responds to mixed-state degradation and provides a useful proxy for classical simulation difficulty.

(E) Entanglement vs Simulation Cost

Observation

Higher logarithmic negativity corresponds to larger operator complexity.

Interpretation

Mixed-state entanglement and classical simulation cost are strongly correlated.

As entanglement decreases, the effective simulation complexity also decreases.

(F) Single-Trajectory Bond Dimension

Observation

The MPS bond dimension remains essentially constant over the entire noise range.

Interpretation

This confirms that bond dimension of individual stochastic trajectories is insensitive to local Pauli errors.

Therefore bond dimension alone cannot characterize mixed-state complexity under this simulation model.

Main Scientific Findings

This work demonstrates that:

Trajectory entanglement entropy remains nearly invariant under stochastic Pauli noise.
Increasing circuit depth does not resolve this invariance.
State purity correctly detects mixed-state formation.
Logarithmic negativity successfully captures the destruction of genuine quantum entanglement.
Operator-Schmidt participation ratio provides a physically meaningful proxy for classical simulation complexity.
Single-trajectory bond dimension is insensitive to this noise model and therefore should not be used as the primary complexity indicator.
