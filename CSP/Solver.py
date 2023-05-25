import os
import subprocess
import time
from collections import deque
from copy import deepcopy
from typing import Optional
from operator import attrgetter

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
        if self.is_finished():
            print(f'Assignments: {self.problem.print_assignments()}')
            return self.problem.variables  # todo: check

        unassigned_var: Variable or None = self.select_unassigned_variable()
        self.order_domain_values(unassigned_var)
        for uval in unassigned_var.domain:
            unassigned_var.value = uval  # added to assignment variables  
            print(f"unassigned var: {unassigned_var}")
            if self.is_consistent(unassigned_var):  # check if don't ignore neighbors constraints
                # in here we shouldn't use forward check
                # we have to run backtracking without forward checking
                if self.use_forward_check:
                    if not self.forward_check(unassigned_var):
                        break

                result = self.backtracking()
                if result:
                    return result
                else:
                    # if with this value we don't have an opportunity to
                    # get to the goal we will change the value of variable
                    unassigned_var.value = None
            else:
                unassigned_var.value = None
        return False

    def forward_check(self, var: Variable):

        # ERROR: why do you calculate neighbors again ?
        # self.problem.calculate_neighbors()
        variable_value = var.value

        # Note : I will take care of this
        # if you accept you delete your code

        # NOTE: you are using this method to do
        # 2 action ( forward checking / check that we are not at a deadend)
        # you don't need to do the 2nd one the backward method do it itself

        # pre_neighbors = var.neighbors

        # # set the value for variable, so other domains will be removed
        # var.domain = [variable_value]
        # # remove the value from all the neighbors, if it has more than one value, then remove the value
        # for i, neighbor in enumerate(var.neighbors):
        #     if len(neighbor.domain) > 1:
        #         neighbor.domain.remove(variable_value)
        #     else:
        #         var.value = None
        #         for x in range(i + 1):
        #             var.neighbors[i].domain = pre_neighbors[i].domain
        #         # todo: revert the changed values from neighbors
        #         return False
        # return True

        # todo: we have to copy domain and send it into lower layers

        is_not_deadend: bool = True

        for neighbor in var.neighbors:
            for nei_v in neighbor.domain:
                if nei_v == variable_value:
                    neighbor.domain.remove(nei_v)
                    # NOTE: if there is no domain for a neighbor
                    # it means there is no solution for it and we need to backward
                    if len(neighbor.domain) == 0:
                        is_not_deadend = False

        return is_not_deadend

    def arc_consistency(self, variable: Variable):
        constraints = self.problem.constraints
        return any([x.is_satisfied() for x in constraints])

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
        return min(unassigned_variables, key=attrgetter('len_domain'))

    def degree_heuristic(self):
        unassigned_variables = self.problem.get_unassigned_variables()
        return max(unassigned_variables, key=attrgetter('len_neighbors_constraint'))

    def is_consistent(self, var: Variable):
        print("is consistant: ".format([x.is_satisfied() for x in self.problem.get_neighbor_constraints(var)]))
        return all([x.is_satisfied() for x in self.problem.get_neighbor_constraints(var)])

    def lcv(self, var: Variable):
        pass