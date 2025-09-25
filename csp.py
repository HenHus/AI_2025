from typing import Any
from queue import Queue
from time import time


class CSP:
    def __init__(
        self,
        variables: list[str],
        domains: dict[str, set],
        edges: list[tuple[str, str]],
    ):
        """Constructs a CSP instance with the given variables, domains and edges.
        
        Parameters
        ----------
        variables : list[str]
            The variables for the CSP
        domains : dict[str, set]
            The domains of the variables
        edges : list[tuple[str, str]]
            Pairs of variables that must not be assigned the same value
        """
        self.variables = variables
        self.domains = domains

        self.total_backtrack_calls = 0
        self.total_failed_backtracks = 0

        # Binary constraints as a dictionary mapping variable pairs to a set of value pairs.
        #
        # To check if variable1=value1, variable2=value2 is in violation of a binary constraint:
        # if (
        #     (variable1, variable2) in self.binary_constraints and
        #     (value1, value2) not in self.binary_constraints[(variable1, variable2)]
        # ) or (
        #     (variable2, variable1) in self.binary_constraints and
        #     (value1, value2) not in self.binary_constraints[(variable2, variable1)]
        # ):
        #     Violates a binary constraint
        self.binary_constraints: dict[tuple[str, str], set] = {}
        for variable1, variable2 in edges:
            self.binary_constraints[(variable1, variable2)] = set()
            for value1 in self.domains[variable1]:
                for value2 in self.domains[variable2]:
                    if value1 != value2:
                        self.binary_constraints[(variable1, variable2)].add((value1, value2))
                        self.binary_constraints[(variable1, variable2)].add((value2, value1))

    def ac_3(self) -> bool:
        """Performs AC-3 on the CSP.
        Meant to be run prior to calling backtracking_search() to reduce the search for some problems.
        
        Returns
        -------
        bool
            False if a domain becomes empty, otherwise True
        """
        # Initialize queue with all arcs
        queue = Queue()
        for (var1, var2) in self.binary_constraints:
            queue.put((var1, var2))
        
        while not queue.empty():
            xi, xj = queue.get()
            if self._revise(xi, xj):
                if len(self.domains[xi]) == 0:
                    return False
                # Add all arcs (xk, xi) where xk is a neighbor of xi (except xj)
                for (var1, var2) in self.binary_constraints:
                    if var2 == xi and var1 != xj:
                        queue.put((var1, xi))
                    elif var1 == xi and var2 != xj:
                        queue.put((var2, xi))
        return True
    
    def _revise(self, xi: str, xj: str) -> bool:
        """Revise the domain of xi to make it arc-consistent with xj.
        
        Parameters
        ----------
        xi : str
            The variable whose domain we're revising
        xj : str
            The variable we're checking consistency against
            
        Returns
        -------
        bool
            True if the domain of xi was revised (values were removed)
        """
        revised = False
        values_to_remove = []
        
        for value_i in self.domains[xi]:
            # Check if there exists a value in xj's domain that satisfies the constraint
            consistent = False
            for value_j in self.domains[xj]:
                # Check if (value_i, value_j) satisfies the constraint
                if (xi, xj) in self.binary_constraints:
                    if (value_i, value_j) in self.binary_constraints[(xi, xj)]:
                        consistent = True
                        break
                elif (xj, xi) in self.binary_constraints:
                    if (value_j, value_i) in self.binary_constraints[(xj, xi)]:
                        consistent = True
                        break
            
            if not consistent:
                values_to_remove.append(value_i)
                revised = True
        
        # Remove inconsistent values
        for value in values_to_remove:
            self.domains[xi].remove(value)
            
        return revised



    def backtracking_search(self) -> None | dict[str, Any]:
        """Backtracking search following the standard pseudocode.
        
        Returns
        -------
        None | dict[str, Any]
            A solution if any exists, otherwise None
        """
        start_time = time()
        def backtrack(assignment: dict[str, Any]):
            self.total_backtrack_calls += 1
            # if assignment is complete then return assignment
            if len(assignment) == len(self.variables):
                return assignment
            
            # var ← SELECT-UNASSIGNED-VARIABLE(csp, assignment)
            unassigned_vars = [v for v in self.variables if v not in assignment]
            var = unassigned_vars[0]  # Simple selection strategy
            
            # for each value in ORDER-DOMAIN-VALUES(csp, var, assignment) do
            for value in list(self.domains[var]):
                # if value is consistent with assignment then
                if self._is_consistent(var, value, assignment):
                    # add {var = value} to assignment
                    assignment[var] = value
                    
                    # inferences ← INFERENCE(csp, var, assignment)
                    inferences = self._make_inference(var, value, assignment)
                    
                    # if inferences ≠ failure then
                    if inferences is not None:
                        # add inferences to csp (already applied in _make_inference)
                        # result ← BACKTRACK(csp, assignment)
                        result = backtrack(assignment)
                        # if result ≠ failure then return result
                        if result is not None:
                            return result
                    
                    # remove inferences from csp
                    if inferences is not None:
                        self._restore_inferences(inferences)
                    # remove {var = value} from assignment
                    del assignment[var]
            
            self.total_failed_backtracks += 1
            # return failure
            return None
        result = backtrack({})
        end_time = time()
        print(f"Backtracking search took {end_time - start_time:.4f} seconds")
        return result



    def _make_inference(self, var: str, value: Any, assignment: dict[str, Any]) -> dict[str, set] | None:
        """Make inferences after assigning value to var.
        
        Toggle between AC-3 inference and no inference by commenting/uncommenting sections.
        
        Parameters
        ----------
        var : str
            The variable that was just assigned
        value : Any
            The value assigned to var
        assignment : dict[str, Any]
            Current assignment
            
        Returns
        -------
        dict[str, set] | None
            Dictionary of removed values for each variable, or None if failure
        """
        
        # # OPTION 1: AC-3 Inference
        # # Save current domains before applying AC-3
        # original_domains = {v: domain.copy() for v, domain in self.domains.items()}
        
        # # Reduce domain of assigned variable to just this value
        # self.domains[var] = {value}
        
        # # Apply AC-3 to maintain arc consistency
        # if self.ac_3():
        #     # AC-3 succeeded, calculate what was removed
        #     removed_values = {}
        #     for variable in self.domains:
        #         original = original_domains[variable]
        #         current = self.domains[variable]
        #         removed = original - current
        #         if removed:
        #             removed_values[variable] = removed
        #     return removed_values
        # else:
        #     # AC-3 failed (domain became empty), restore domains
        #     self.domains = original_domains
        #     return None
        
        # # OPTION 2: No inference (naive backtracking)
        return {}
    
    def _restore_inferences(self, inferences: dict[str, set]) -> None:
        """Restore domain values that were removed during AC-3 inference.
        
        Parameters
        ----------
        inferences : dict[str, set]
            Dictionary mapping variables to sets of values that were removed
        """
        for variable, removed_values in inferences.items():
            self.domains[variable].update(removed_values)

    def _is_consistent(self, var: str, value: Any, assignment: dict[str, Any]) -> bool:
        """Check if assigning value to var is consistent with current assignment.
        
        Parameters
        ----------
        var : str
            Variable to assign
        value : Any
            Value to assign to variable
        assignment : dict[str, Any]
            Current partial assignment
            
        Returns
        -------
        bool
            True if assignment is consistent
        """
        for assigned_var, assigned_value in assignment.items():
            # Check binary constraints
            if (var, assigned_var) in self.binary_constraints:
                if (value, assigned_value) not in self.binary_constraints[(var, assigned_var)]:
                    return False
            elif (assigned_var, var) in self.binary_constraints:
                if (assigned_value, value) not in self.binary_constraints[(assigned_var, var)]:
                    return False
        return True
    



def alldiff(variables: list[str]) -> list[tuple[str, str]]:
    """Returns a list of edges interconnecting all of the input variables
    
    Parameters
    ----------
    variables : list[str]
        The variables that all must be different

    Returns
    -------
    list[tuple[str, str]]
        List of edges in the form (a, b)
    """
    return [(variables[i], variables[j]) for i in range(len(variables) - 1) for j in range(i + 1, len(variables))]
