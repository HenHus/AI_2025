#!/usr/bin/env python3
"""
Test AC-3 algorithm on all four Sudoku puzzles to analyze domain reduction.
This script runs AC-3 independently on each puzzle and shows the results.
"""

from csp import CSP, alldiff
import copy

def create_sudoku_csp(filename):
    """Create a Sudoku CSP from a file."""
    grid = open(filename).read().split()
    
    width = 9
    box_width = 3
    
    domains = {}
    for row in range(width):
        for col in range(width):
            if grid[row][col] == '0':
                domains[f'X{row+1}{col+1}'] = set(range(1, 10))
            else:
                domains[f'X{row+1}{col+1}'] = {int(grid[row][col])}
    
    edges = []
    # Row constraints
    for row in range(width):
        edges += alldiff([f'X{row+1}{col+1}' for col in range(width)])
    # Column constraints
    for col in range(width):
        edges += alldiff([f'X{row+1}{col+1}' for row in range(width)])
    # Box constraints
    for box_row in range(box_width):
        for box_col in range(box_width):
            edges += alldiff(
                [
                    f'X{row+1}{col+1}' for row in range(box_row * box_width, (box_row + 1) * box_width)
                    for col in range(box_col * box_width, (box_col + 1) * box_width)
                ]
            )
    
    return CSP(
        variables=[f'X{row+1}{col+1}' for row in range(width) for col in range(width)],
        domains=domains,
        edges=edges,
    )

def test_ac3_on_puzzles():
    """Test AC-3 on all four Sudoku puzzles."""
    puzzles = [
        'sudoku_easy.txt',
        'sudoku_medium.txt', 
        'sudoku_hard.txt',
        'sudoku_very_hard.txt'
    ]
    
    for puzzle in puzzles:
        print(f"\n{'='*60}")
        print(f"Testing AC-3 on {puzzle}")
        print(f"{'='*60}")
        
        try:
            # Create CSP
            csp = create_sudoku_csp(puzzle)
            
            # Show domains before AC-3
            print("\nDomains BEFORE AC-3:")
            initial_analysis = csp.analyze_domains()
            
            # Store original domains for comparison
            original_domains = copy.deepcopy(csp.domains)
            
            # Run AC-3
            print(f"\nRunning AC-3...")
            ac3_result = csp.ac_3()
            print(f"AC-3 result: {ac3_result}")
            
            # Show domains after AC-3
            print("\nDomains AFTER AC-3:")
            final_analysis = csp.analyze_domains()
            
            # Show the improvement
            solved_improvement = final_analysis['solved_vars'] - initial_analysis['solved_vars']
            print(f"\nImprovement:")
            print(f"  Variables solved by AC-3: {solved_improvement}")
            print(f"  Percentage solved: {final_analysis['solved_vars']/81*100:.1f}%")
            
            # Show some specific examples of domain reduction
            print(f"\nExamples of domain reduction:")
            count = 0
            for var in sorted(csp.variables):
                if len(original_domains[var]) > 1 and len(csp.domains[var]) < len(original_domains[var]):
                    print(f"  {var}: {sorted(original_domains[var])} → {sorted(csp.domains[var])}")
                    count += 1
                    if count >= 10:  # Show only first 10 examples
                        break
            if count == 0:
                print("  No domain reductions found.")
                
        except FileNotFoundError:
            print(f"Error: Could not find file {puzzle}")
        except Exception as e:
            print(f"Error processing {puzzle}: {e}")

if __name__ == "__main__":
    test_ac3_on_puzzles()