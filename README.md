# Entanglement Collapse & Classical Simulability of Noisy Variational Quantum Circuits

## Abstract

Variational quantum circuits are one of the main candidates for near-term quantum
advantage, but whether they stay classically hard to simulate once realistic noise
is added is still an open question. This project simulates a hardware-efficient
brickwork circuit (Ry rotations + CX entangling layers) under stochastic depolarizing
noise via matrix-product-state trajectory simulation, and systematically checks which
of the "obvious" complexity measures actually track what noise is doing. The short
version: trajectory entanglement entropy, Schmidt rank, and MPS bond dimension are
all invariant under this noise model — provably, not just empirically — and a naive
density-matrix rank measure moves in the *wrong* direction. Logarithmic negativity
and the operator-Schmidt participation ratio of the reconstructed mixed state are the
two measures that behave correctly, and they track each other (Pearson r = 0.91 in
the validated regime). The strongest claim this repo currently supports is the
methodological one — which metrics fail, and why — with the entanglement-collapse ↔
simulation-cost link demonstrated at N=6 and still being scaled up.

## Key contributions

- Proves (not just observes) that trajectory entanglement entropy is exactly
  invariant under single-qubit Pauli noise, and shows why the same argument kills
  Schmidt rank and MPS bond dimension too.
- Shows that a naive density-matrix rank measure gets the direction backwards —
  it increases with noise instead of decreasing.
- Identifies logarithmic negativity as the correct mixed-state entanglement measure
  for this setting, and the operator-Schmidt participation ratio as the correct
  classical-simulation-cost proxy.
- Ties the two together on identical data (same reconstructed density matrices) to
  test the entanglement-collapse-implies-cost-collapse claim directly, rather than
  asserting it.
- Full simulation framework — circuit construction, noisy MPS trajectory evolution,
  density-matrix reconstruction, scaling-collapse analysis with built-in sanity
  checks — reusable for other ansätze or noise models.

## Quick start

```bash
pip install qiskit quimb numpy matplotlib scipy
python main_negativity.py
```

That's the corrected pipeline — negativity, operator cost, scaling collapse, and the
correlation number, all in one run, dumping `negativity_cost_dashboard.png` plus a
full console log of every (N, p) point.

`main.py` still exists and still runs. It's kept for Phase 3/4 (the simulability
boundary via SVD truncation, a separate question that doesn't depend on any of the
broken metrics below) and, honestly, as a documented example of what a dead-end
metric looks like when you actually run it.

## Main results

![entropy vs noise, completely flat across every N](assets/entropy_flat_dashboard.png)

Three system sizes, noise swept from 0 to 0.035, three panels:

**Left — entropy vs. noise.** Flat, for every N. No decrease anywhere in this range.
Trajectory entropy simply doesn't respond to this noise model (explained below, and
it's not a numerical issue).

**Middle — scaling collapse.** Since there's no real transition to find, the fit
does what fits do when there's nothing there: it doesn't converge to anything
meaningful.

**Right — collapse cost landscape.** The optimizer's best fit sits at `ν=0.10`,
exactly the floor of the search window I gave it. That's the tell. A fit pinned to
the edge of its own search range means the data has no transition in it, not that
the search range needs to be wider. The code checks for this now and prints a
warning whenever it happens.

![entropy vs circuit layer, saturating around layer 25](assets/saturation_check.png)

Before trusting the flat result above, I checked whether it was simply an
under-evolved circuit — plotted entropy against circuit layer instead of noise, for
three different p values on the same N=10 system. Entropy climbs and saturates by
around layer 25, and — this is the important part — the p=0.000, p=0.006, and
p=0.035 curves are nearly on top of each other the entire way up. Depth was never the
issue. The noise genuinely isn't moving this metric, at any depth.

## The story

I started this wanting a pretty standard result from the noisy-random-circuit
literature: crank up the noise, entanglement entropy drops, past some critical `p_c`
the state becomes cheap to represent as an MPS, and that boundary is basically "when
does the classical simulability advantage from noise kick in." Scanned p from 0 to
0.5, plotted entropy vs. p for a few system sizes, got exactly the flat curves shown
above. Every N, every p, no bend anywhere.

Turns out that's not a tuning problem, it's a theorem. The noise here is implemented
as "with probability p, apply a random single-qubit Pauli (X/Y/Z), otherwise do
nothing" — a completely standard way to simulate a depolarizing channel via quantum
trajectories. The problem is that a single-qubit Pauli gate is just `UρU†` for a
unitary U acting on one qubit, and local unitaries can't change the Schmidt
decomposition across a bipartition they don't touch. Entropy before and after a Pauli
kick has to be *exactly* equal. Checked it directly on a running simulation:

```
entropy before Pauli kick: 0.9145951290871184
entropy after Pauli-X on one qubit: 0.9145951290871186
```

Same number to 1 part in 10¹⁴. Not noise, a fact. Schmidt rank and MPS bond dimension
are governed by the identical argument, so they fail for the identical reason —
every trajectory-level pure-state metric I tried was dead on arrival.

So I stopped trying to fix the metric and started cataloguing which quantities
survive this problem:

| Metric | What happened | Usable? |
|---|---|---|
| Entanglement entropy (single trajectory) | flat, invariant by theorem | no |
| Schmidt rank (single trajectory) | flat, same reason | no |
| MPS bond dimension (single trajectory) | flat, same reason | no |
| Linear rank of the density matrix ρ | goes the *wrong way* — increases with noise | no |
| Logarithmic negativity of ρ | drops smoothly, correctly detects entanglement dying | yes |
| Operator-Schmidt participation ratio of ρ | drops smoothly, tracks simulation cost | yes |

The density-matrix-rank row is its own small trap worth flagging on its own: a
maximally mixed state has the *highest possible* linear rank while being the single
easiest state in the world to describe (it's just the identity, scaled). Rank
conflates "mixed" with "hard to simulate," and here those are opposites. Only found
this by trying it and watching the number climb instead of fall.

What worked: stop looking at individual trajectories, reconstruct the actual
noise-averaged density matrix ρ (average `|ψ⟩⟨ψ|` over many independently sampled
trajectories, each drawn with the physically correct Kraus-branch probability), and
measure that instead.

- **Logarithmic negativity** — the standard mixed-state entanglement measure.
  Ignores classical randomness, responds only to genuine quantum entanglement, drops
  cleanly toward zero as noise increases.
- **Operator-Schmidt participation ratio** — reshape ρ as an operator on subsystem
  A ⊗ subsystem B and look at the singular value spectrum. This is what determines
  matrix-product-*operator* bond dimension, i.e. actual classical simulation cost for
  a mixed state. A hard rank threshold on this spectrum gets swamped by a long tail
  of near-zero values, so the number I actually use is the participation ratio
  (effective count of singular values that matter) — continuous, no arbitrary
  cutoff, well-behaved.

Both only scale to modest N (dense 2^N × 2^N matrices), and both need enough Monte
Carlo trajectories to actually resolve that matrix — undersampling silently produces
a plot that looks fine and means nothing. Once sampling was adequate, negativity and
operator cost moved together cleanly:

```
p=0.000  negativity=2.57  op_cost=14.4
p=0.014  negativity=0.31  op_cost=4.6
p=0.063  negativity=0.24  op_cost=3.9
```

Pearson correlation across all sampled points: **0.91**.

## Methodology

```
hardware-efficient brickwork ansatz (Ry + CX)
            │
            ▼
stochastic Pauli noise injected per-qubit, per-layer
            │
            ▼
quantum trajectory simulation (MPS, quimb)
            │
            ▼
density-matrix reconstruction (average |ψ><ψ| over trajectories)
            │
            ▼
mixed-state analysis: negativity, purity, operator-Schmidt spectrum
            │
            ▼
finite-size scaling collapse + noise-blindness comparison
```

## Experimental settings

- Qubits: N = 4, 6, 8, 10 (N ≤ 10 for anything touching the dense density matrix —
  see limitations)
- Circuit depth: up to 36 layers, checked for saturation before trusting any
  "saturation value" (see the depth-check panel above)
- Noise model: stochastic depolarizing Pauli channel, one of {X, Y, Z} applied with
  probability p, identity otherwise
- Noise range: scaled by `estimate_injection_count()` — with `~D·(3N-2)` individual
  injection points per circuit, the transition sits around p ~ 0.01–0.05, not O(1);
  scanning p up to 0.5 (my first instinct) mostly just measures the fully-decohered
  plateau
- Trajectories: 120+ where validated (N=6); fewer than that gives visibly noisy,
  unreliable operator-cost estimates — the code now warns when this happens
- Tensor network backend: quimb (MPS)
- Circuit construction: Qiskit
- Python: 3.10+



## Running experiments

```bash
# corrected pipeline (negativity + operator cost + scaling collapse)
python main_negativity.py

# original entropy-based pipeline (Phase 3/4 truncation-boundary work,
# Phase 1/2 kept as documented negative-result reference)
python main.py
```

Both scripts print their full parameter grid and every measured point to the console
as they run, not just a summary at the end — useful for catching an undersampled
point before you've built a whole figure around it.

## Main findings

1. Trajectory entanglement entropy is exactly invariant under stochastic Pauli
   noise, for reasons that are provable, not just numerically small.
2. MPS bond dimension is invariant for individual trajectories, for the same reason.
3. Linear rank of the density matrix is actively misleading — it moves the wrong
   direction with noise.
4. Logarithmic negativity correctly detects mixed-state entanglement degradation.
5. Operator-Schmidt participation ratio tracks simulation complexity and correlates
   strongly with negativity (r = 0.91 in the validated N=6 case).
6. The commonly used pure-state measures — entropy, Schmidt rank, bond dimension —
   are simply the wrong tool for this noise model, not a matter of needing a wider
   parameter scan.

## Honest state of things

- N=6 is validated with adequate statistics. N=8 and N=10 need the same treatment —
  the density matrix is 2^N × 2^N, so the trajectory count needed to reconstruct it
  reliably grows fast, and a full high-statistics run at those sizes hasn't happened
  yet. `negativity_saturation_scan` warns automatically when a scan is undersampled
  rather than silently returning noisy numbers.
- Don't trust a p_c that comes with ν pinned to the edge of its search range — the
  screenshots above are a live example of exactly that failure mode, kept in this
  README on purpose as a reference case, not a real result.
- Operator-Schmidt participation ratio of the exact dense ρ is a strong proxy for
  classical simulation cost, but the real confirming experiment is an actual
  truncated MPO/LPDO simulation. Haven't built that yet.
- Negativity plateaus above zero and operator cost plateaus above 1 rather than
  hitting zero/one exactly — the noise kills quantum entanglement but some residual
  classical correlation survives. Worth its own discussion, not a loose end to
  quietly ignore.
- The README shouldn't claim more than the experiments show. The validated
  contribution right now is the methodological one: which metrics fail under this
  noise model and why, and that the two that work (negativity, operator-Schmidt
  participation ratio) behave consistently with each other. The full
  entanglement-collapse-defines-the-simulability-boundary story is supported at
  N=6 and still being scaled up, not yet a closed case across all N.

## Future work

- N=8, N=10 with properly adequate trajectory statistics
- alternative ansätze, not just this brickwork circuit
- other noise channels (dephasing, amplitude damping) — the invariance problem here
  is specific to unitary Kraus operators like Pauli twirl, worth checking whether
  non-unitary channels avoid it
- an actual truncated MPO/LPDO simulation to confirm the operator-cost proxy against
  real simulation runtime, not just a proxy computed from the dense density matrix
- finite-size scaling redone on properly-sampled negativity data across all N
- adaptive truncation tied to the operator-cost proxy directly


