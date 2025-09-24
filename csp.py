from typing import Any
from queue import Queue


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
        """Performs backtracking search on the CSP.
        
        Returns
        -------
        None | dict[str, Any]
            A solution if any exists, otherwise None
        """
        def backtrack(assignment: dict[str, Any]):
            if len(assignment) == len(self.variables):
                return assignment
            
            # Select unassigned variable (using MRV heuristic - minimum remaining values)
            unassigned_vars = [v for v in self.variables if v not in assignment]
            var = min(unassigned_vars, key=lambda v: len(self.domains[v]))
            
            # Try each value in the variable's domain
            for value in list(self.domains[var]):  # Create copy since we might modify during iteration
                # Check if this assignment is consistent with current assignments
                if self._is_consistent(var, value, assignment):
                    # Make assignment
                    assignment[var] = value
                    
                    # Save current domains before applying AC-3
                    saved_domains = {v: domain.copy() for v, domain in self.domains.items()}
                    
                    # Reduce domain of assigned variable to just this value
                    self.domains[var] = {value}
                    
                    # Apply AC-3 to maintain arc consistency
                    if self.ac_3():
                        # Recursively search with reduced domains
                        result = backtrack(assignment)
                        if result is not None:
                            return result
                    
                    # Backtrack: restore domains and remove assignment
                    self.domains = saved_domains
                    del assignment[var]
            
            return None
        
        return backtrack({})
    
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
