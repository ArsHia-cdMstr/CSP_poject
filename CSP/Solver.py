import os
import subprocess
import time
from collections import deque
from copy import deepcopy
from typing import Optional

from CSP.Problem import Problem
from CSP.Variable import Variable


class Solver:

    def __init__(self, problem: Problem, use_mrv=False, use_lcv=False, use_forward_check=False):
        self.problem = problem
        self.use_lcv = use_lcv
        self.use_mrv = use_mrv
        self.use_forward_check = use_forward_check

    def is_finished(self) -> bool:
        return all([x.is_satisfied() for x in self.problem.constraints]) and len(
            self.problem.get_unassigned_variables()) == 0

    def solve(self):
        self.problem.calculate_neighbors()
        start = time.time()
        for var in self.problem.variables:
            print(f"var: {var}")
            if not self.forward_check(var):
                print("Problem Unsolvable")
                return
        result = self.backtracking()
        end = time.time()
        time_elapsed = (end - start) * 1000
        if result:
            print(f'Solved after {time_elapsed} ms')
            [print(x) for x in result]
        else:
            print(f'Failed to solve after {time_elapsed} ms')


    def backtracking(self):
        uvar = self.select_unassigned_variable()
        if self.is_finished():
            return self.problem.variables # todo: check
        for uval in uvar.domain:
            uvar.value = uval
            print(f"unass var: {uvar}")
            if self.is_consistent(uvar):
                self.forward_check(uvar)
                result = self.backtracking()
                if result:
                    return result
                else:
                    pass # todo: unforward_check 
            else:
                uvar.value = None
        return False

    def forward_check(self, var):
        pre_var_value = var.value
        self.problem.calculate_neighbors()
        variable_value = var.value

        # set the value for variable, so other domains will be remove
        var.domain = [variable_value]
        # remove the value from all the neighbors, if it has more than one value, then remove the value
        for neighbor in enumerate(var.neighbors):
            if len(neighbor.domain) > 1:
                neighbor.domain.remove(variable_value)
            else:
                # todo: revert the changed values from neighbors
                break

    def select_unassigned_variable(self) -> Optional[Variable]:
        if self.use_mrv:
            return self.mrv()
        unassigned_variables = self.problem.get_unassigned_variables()
        return unassigned_variables[0] if unassigned_variables else None

    def order_domain_values(self, var: Variable):
        if self.use_lcv:
            return self.lcv(var)
        return var.domain

    def mrv(self) -> Optional[Variable]:
        unassigned_variables = self.problem.get_unassigned_variables()

    def is_consistent(self, var: Variable):
        print("is consistant: ".format([x.is_satisfied() for x in self.problem.constraints]))
        return all([x.is_satisfied() for x in self.problem.constraints])


    def lcv(self, var: Variable):
        pass
        # Write your code here


