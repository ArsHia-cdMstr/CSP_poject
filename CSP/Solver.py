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

        # Note: build the dictionary that has variable object and domain list in it
        variables_domain = {var: var.domain for var in self.problem.variables}

        for var in self.problem.variables:
            if not self.forward_check(variables_domain, var):
                print("Problem Unsolvable")
                return
        result = self.backtracking(variables_domain)
        end = time.time()
        time_elapsed = (end - start) * 1000
        if result:
            print(f'Solved after {time_elapsed} ms')
            # Fixed: we didn't need print the variables in here
            # [print(x) for x in result]
        else:
            print(f'Failed to solve after {time_elapsed} ms')

    def backtracking(self, variables_domain: dict[Variable, list]):

        if self.is_finished():
            self.problem.print_assignments()
            # Fixed : since we already have the value of variables
            # we don't need to return anything but a True boolean
            # return self.problem.variables  # todo: check
            return True

        unassigned_var: Variable or None = self.select_unassigned_variable(variables_domain)
        self.order_domain_values(unassigned_var, variables_domain)
        for uval in variables_domain[unassigned_var]:
            unassigned_var.value = uval  # assign a value variables  
            print(f"unassigned var: {unassigned_var}")
            if self.is_consistent(unassigned_var):  # check if don't ignore neighbors constraints
                # in here we shouldn't use forward check
                # we have to run backtracking without forward checking
                new_variables_domains = variables_domain
                if self.use_forward_check:
                    if fc_res:=self.forward_check(variables_domain, unassigned_var):
                        new_variables_domains = fc_res    


                result = self.backtracking(new_variables_domains)
                if result:
                    return result
                else:
                    # if with this value we don't have an opportunity to
                    # get to the goal we will change the value of variable
                    unassigned_var.value = None
            else:
                unassigned_var.value = None
        return False

    @staticmethod
    def forward_check(variables_dom: dict[Variable, list], var: Variable):
        new_variables_dom = {variable: domain.copy() for variable, domain in variables_dom.items()}
        variable_value = var.value

        for neighbor in var.neighbors:
            neighbor_domains: list = new_variables_dom[neighbor]
            for nei_v in neighbor_domains:
                if nei_v == variable_value:
                    neighbor_domains.remove(nei_v)
                    # NOTE: if there is no domain for a neighbor
                    # it means there is no solution for it and we need to backward
                    if len(neighbor_domains) == 0: # no solution
                        # Note: if we face to deadend we will return false,
                        # so that we won't continue calculating the deadend subtree
                        return False

        return new_variables_dom

    def arc_consistency(self, variable: Variable):
        constraints = self.problem.constraints
        return any([x.is_satisfied() for x in constraints])

    def select_unassigned_variable(self, variables_domain: dict[Variable, list]) -> Optional[Variable]:
        if self.use_mrv:
            return self.mrv(variables_domain)
        unassigned_variables = self.problem.get_unassigned_variables()
        return unassigned_variables[0] if unassigned_variables else None

    def order_domain_values(self, var: Variable, variable_domain: dict[Variable, list]):
        if self.use_lcv:
            return self.lcv(var, variable_domain)
        return variable_domain[var]

    def mrv(self, variables_domain: dict[Variable, list]) -> Optional[Variable]:
        """Returns a variable with minimum remain values"""
        unassigned_variables: list[Variable] or None = self.problem.get_unassigned_variables()
        min1 = float('inf')
        MRV_variable = None

        for var in unassigned_variables:
            if a:=len(variables_domain[var]) < min1:
                min1 = a
                MRV_variable = var

        return MRV_variable

    def degree_heuristic(self):
        unassigned_variables = self.problem.get_unassigned_variables()
        return max(unassigned_variables, key=attrgetter('len_neighbors_constraint'))

    def is_consistent(self, var: Variable):
        print("is consistant: {}".format([x.is_satisfied() for x in self.problem.get_neighbor_constraints(var)]))
        return all([x.is_satisfied() for x in self.problem.get_neighbor_constraints(var)])

    def lcv(self, var: Variable, variables_domain: dict[Variable, list]):
        domain: list = variables_domain[var]
        # return the value that has the least constrain value
        return min(domain, key=lambda value: self.count_constraint(value, var, variables_domain))

    @staticmethod
    def count_constraint(value, var: Variable, variable_domain: dict[Variable, list]):
        constraint_count = 0
        for neighbor in var.neighbors:
            for neighbor_value in variable_domain[neighbor]:
                if neighbor_value == value:
                    constraint_count += 1

        return constraint_count
