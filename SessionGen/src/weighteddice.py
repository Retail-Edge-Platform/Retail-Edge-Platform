import random

def roll(bias_list):
    """Rolls a weighted dice
    A die with N sides that are biased through the *bias_list* are
    rolled once and the selected side is returned.

    The bias list should sum to 1.0. Tolerance can be adjusted

    Modified from stack-overflow weighted dice
 
    ```python
    my_die_biases = (0.10, 0.30, 0.49, 0.11) 
    outcome_of_roll = roll(my_die_biases)
    print(outcome_of_roll) 
    # Should print one of these numbers 1,2,3 or 4
    ```
    Returns:
        outcome: The result of rolling the weighted die
    """
    def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
        """Floating point compare with realtive and absolute tolerances
        From PEP 485 documentation. 
        """
        return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

    sides = len(bias_list)
    assert isclose(sum(bias_list), 1.0)
    number = random.uniform(0, sum(bias_list))
    current = 0
    for i, bias in enumerate(bias_list):
        current += bias
        if number <= current:
            return i + 1