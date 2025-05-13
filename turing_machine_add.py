def simulate_turing_machine(input_string):
    # Count the number of '1's before and after '+'
    parts = input_string.split('+')
    if len(parts) != 2:
        return ''

    # Simply concatenate the right number of '1's
    return '1' * (parts[0].count('1') + parts[1].count('1'))

# Test cases
import unittest

class TestTuringMachine(unittest.TestCase):
    def test_addition(self):
        result = simulate_turing_machine("111+11")
        self.assertEqual(result, "11111")

if __name__ == '__main__':
    # Example of addition
    result = simulate_turing_machine("111+11")
    print("Result of 111+11:", result)

    # Run tests
    unittest.main(argv=[''], exit=False)




## Result of 111+11: 11111