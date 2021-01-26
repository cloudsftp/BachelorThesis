#!/bin/python3.8

from qiskit import IBMQ # type: ignore
from qiskit.aqua import aqua_globals # type: ignore
from qiskit.aqua.quantum_instance import QuantumInstance # type: ignore
from qiskit import BasicAer # type: ignore
from qiskit.circuit.quantumcircuit import QuantumCircuit # type: ignore
from qiskit.aqua.algorithms import QAOA # type: ignore
from qiskit.optimization.algorithms import MinimumEigenOptimizer, RecursiveMinimumEigenOptimizer, GroverOptimizer # type: ignore
from qiskit.optimization.converters import QuadraticProgramToQubo

from UCP.unit_commitment_problem import UCP, ExperimentParameters, CombustionPlant, UCPSolution
from Gatebased.qubo import UCP_QUBO


ucp = UCP(ExperimentParameters(2, 2),
  [40, 50],
  [
    CombustionPlant(1, 1, 1, 10, 30, 1, 0),
    CombustionPlant(1, 1, 1, 10, 30, 0, 2)
  ]
)

qubo = UCP_QUBO(ucp)
qubo.model.prettyprint()

IBMQ.load_account()
provider = IBMQ.get_provider(group='open', project='main')
backend = provider.get_backend('ibmq_qasm_simulator')

qaoa_mes = QAOA(quantum_instance=backend, initial_point=[0., 0.])
qaoa = MinimumEigenOptimizer(qaoa_mes)
rqaoa = RecursiveMinimumEigenOptimizer(min_eigen_optimizer=qaoa, min_num_vars=1, min_num_vars_optimizer=qaoa)

grover_optimizer = GroverOptimizer(1, num_iterations=3, quantum_instance=backend)
sol: UCPSolution = qubo.optimize(grover_optimizer)
print(sol)
