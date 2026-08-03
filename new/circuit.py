

import numpy as np
from qiskit import QuantumCircuit
import quimb.tensor as qtn


EPS_EXACT = 1e-10

_X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
_Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
_Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
_PAULIS = [_X, _Y, _Z]


def create_parametrized_circuit(num_qbit, theta, layer):
    qc = QuantumCircuit(num_qbit)
    index = 0
    for i in range(layer):
        for j in range(num_qbit):
            qc.ry(theta[index], j)
            index += 1
        for j in range(num_qbit - 1):
            qc.cx(j, j + 1)
    return qc


def initialize_simulation_state(num_qubits):
    initial_configuration = ['0'] * num_qubits
    mps = qtn.MPS_computational_state(initial_configuration)
    return mps


def apply_ry_gate(psi, qubit_idx, angle):
    """Applies an ideal single-qubit Ry rotation gate explicitly contracted."""
    ry_matrix = np.array([
        [np.cos(angle / 2), -np.sin(angle / 2)],
        [np.sin(angle / 2),  np.cos(angle / 2)]
    ], dtype=np.complex128)
    psi.gate_(ry_matrix, qubit_idx, contract=True)


def apply_cx_gate(psi, control_idx, target_idx, eps=1e-6):
    """Applies an ideal two-qubit CNOT gate with adaptive SVD compression."""
    cx_matrix = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0]
    ], dtype=np.complex128).reshape(2, 2, 2, 2)
    psi.gate_(cx_matrix, (control_idx, target_idx), contract='swap+split', cutoff=eps)



def build_noise_schedule(qc, p, rng):
    
    schedule = []
    for instruction in qc.data:
        gate_name = instruction.operation.name
        if gate_name == "ry":
            schedule.append(_draw_noise_decision(p, rng))
        elif gate_name == "cx":
            schedule.append(_draw_noise_decision(p, rng))
            schedule.append(_draw_noise_decision(p, rng))
    return schedule


def _draw_noise_decision(p, rng):
    if p <= 0.0:
        return None
    if rng.random() < p:
        return int(rng.integers(0, 3))
    return None


def inject_depolarizing_noise(psi, qubit_idx, p, rng=None):
    
    if p <= 0.0:
        return
    generator = rng if rng is not None else np.random
    dice_roll = generator.random()
    if dice_roll < p:
        idx = generator.randint(0, 3) if rng is None else int(generator.integers(0, 3))
        psi.gate_(_PAULIS[idx], qubit_idx, contract=True)


def apply_scheduled_noise(psi, qubit_idx, decision):
    """Apply a precomputed noise decision (None, or 0/1/2 for X/Y/Z)."""
    if decision is None:
        return
    psi.gate_(_PAULIS[decision], qubit_idx, contract=True)


# ---------------------------------------------------------------------------
# Layered evolution
# ---------------------------------------------------------------------------

def split_circuit_into_layers(qc):
    layers = []
    current_layer = []
    current_type = None

    for instruction in qc.data:
        gate_name = instruction.operation.name
        if current_type is None:
            current_type = gate_name

        if gate_name != current_type:
            layers.append(current_layer)
            current_layer = []
            current_type = gate_name

        current_layer.append(instruction)

    if current_layer:
        layers.append(current_layer)
    return layers


class _ScheduleCursor:
    """Simple pointer into a precomputed noise schedule list."""

    def __init__(self, schedule):
        self.schedule = schedule
        self.i = 0

    def next(self):
        decision = self.schedule[self.i]
        self.i += 1
        return decision


def evolve_one_layer(psi, layer, qc, p=0.0, eps=1e-6, rng=None, cursor=None):
   
    for instruction in layer:
        gate = instruction.operation
        gate_name = gate.name
        qubits = instruction.qubits
        target_indices = [qc.find_bit(q).index for q in qubits]

        if gate_name == "ry":
            qubit_idx = target_indices[0]
            angle = float(gate.params[0])
            apply_ry_gate(psi, qubit_idx, angle)
            if cursor is not None:
                apply_scheduled_noise(psi, qubit_idx, cursor.next())
            else:
                inject_depolarizing_noise(psi, qubit_idx, p, rng)

        elif gate_name == "cx":
            control_idx = target_indices[0]
            target_idx = target_indices[1]
            apply_cx_gate(psi, control_idx, target_idx, eps)
            if cursor is not None:
                apply_scheduled_noise(psi, control_idx, cursor.next())
                apply_scheduled_noise(psi, target_idx, cursor.next())
            else:
                inject_depolarizing_noise(psi, control_idx, p, rng)
                inject_depolarizing_noise(psi, target_idx, p, rng)
    return psi


def evolve_simulation(mps, qc, p=0.0, eps=1e-6, rng=None, noise_schedule=None,
                       collect_fn=None):
    
    if collect_fn is None:
        from information import collect_information
        collect_fn = collect_information

    psi = mps.copy()
    layers = split_circuit_into_layers(qc)
    history = []

    cursor = _ScheduleCursor(noise_schedule) if noise_schedule is not None else None

    for layer_number, layer in enumerate(layers):
        psi = evolve_one_layer(psi, layer, qc, p=p, eps=eps, rng=rng, cursor=cursor)
        metrics = collect_fn(psi)
        metrics["layer"] = layer_number + 1
        history.append(metrics)

    return psi, history


def state_fidelity(psi_a, psi_b):
    
    overlap = (psi_a.H & psi_b) ^ ...
    norm_a = (psi_a.H & psi_a) ^ ...
    norm_b = (psi_b.H & psi_b) ^ ...
    return float(abs(overlap) ** 2 / (abs(norm_a) * abs(norm_b)))