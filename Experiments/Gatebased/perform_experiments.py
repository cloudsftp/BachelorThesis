#!/bin/python
# version 3.8 required

from qiskit import IBMQ # type: ignore
from qiskit.optimization.algorithms import GroverOptimizer # type: ignore

from UCP.unit_commitment_problem import UCP, ExperimentParameters, UCPSolution
from Data.build_ucp import build_ucp
from Gatebased.qubo import UCP_QUBO
from Util.logging import debug_msg

'''
this file is the experiment runner for the gatebased optimizations
it is not fully implemented
'''

def grover_opt(qubo: UCP_QUBO, backend) -> None:
  '''
  performs the gatebased optimization for an UCP

  :ucp: UCP instance
  :backend: IBMQ backend to use
  '''
  grover_optimizer = GroverOptimizer(1, num_iterations=5, quantum_instance=backend)

  sol: UCPSolution = qubo.optimize(grover_optimizer)
  debug_msg(sol)

if __name__ == "__main__":
  '''
  loads the IBMQ account
  and then optimizes small UCP
  '''
  param: ExperimentParameters = ExperimentParameters(2, 4)
  ucp: UCP = build_ucp(param)

  qubo = UCP_QUBO(ucp)

  IBMQ.load_account()
  provider = IBMQ.get_provider(group='open', project='main')
  backend = provider.get_backend('ibmq_qasm_simulator')

  grover_opt(qubo, backend)
