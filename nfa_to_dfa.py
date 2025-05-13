from collections import deque

# This class represents an NFA (Non-deterministic Finite Automaton)
class NFA:
    def __init__(self, states, alphabet, transitions, start, accepts):
        self.states = states            # All states in the NFA
        self.alphabet = alphabet        # Allowed input symbols (including epsilon '&')
        self.transitions = transitions  # Transition table: state -> symbol -> next states
        self.start = start              # Start state
        self.accepts = accepts          # Accept (final) states

    # This function finds all states reachable from a given set using epsilon (&) moves
    def epsilon_closure(self, state_set):
        stack = list(state_set)         # Stack for tracking states to process
        closure = set(state_set)        # Start closure with the initial states
        while stack:
            state = stack.pop()         # Take one state from the stack
            # For each epsilon move from current state
            for next_state in self.transitions.get(state, {}).get('&', []):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)  # Add to stack to process its epsilon moves
        return closure

    # Convert this NFA to a DFA (Deterministic Finite Automaton)
    def to_dfa(self):
        dfa_states = {}     # Map NFA state sets to DFA state names
        dfa_trans = {}      # DFA transition table
        queue = deque()     # Queue to process DFA states

        # Start with epsilon closure of the NFA start state
        start_closure = frozenset(self.epsilon_closure({self.start}))
        dfa_states[start_closure] = 'q0'
        queue.append(start_closure)
        counter = 1

        while queue:
            current = queue.popleft()   # Take current DFA state
            dfa_trans[dfa_states[current]] = {}

            for symbol in self.alphabet:
                if symbol == '&':       # Ignore epsilon symbol in DFA
                    continue

                move = set()  # All states reachable on current symbol
                for state in current:
                    move.update(self.transitions.get(state, {}).get(symbol, set()))

                # Apply epsilon closure to the result
                closure = self.epsilon_closure(move)
                frozen_closure = frozenset(closure)

                # If this state group is new, assign a new name
                if frozen_closure not in dfa_states:
                    dfa_states[frozen_closure] = f'q{counter}'
                    counter += 1
                    queue.append(frozen_closure)

                # Add the DFA transition
                dfa_trans[dfa_states[current]][symbol] = dfa_states[frozen_closure]

        # Add a "dead" state if there are missing transitions
        dead_state_added = False
        for state in dfa_trans:
            for symbol in self.alphabet:
                if symbol != '&' and symbol not in dfa_trans[state]:
                    dfa_trans[state][symbol] = 'dead'
                    dead_state_added = True

        # Define transitions for the dead state
        if dead_state_added:
            dfa_states[frozenset()] = 'dead'
            dfa_trans['dead'] = {symbol: 'dead' for symbol in self.alphabet if symbol != '&'}

        # Find which DFA states are accepting (if any original NFA accept state is in them)
        dfa_accepts = [dfa_states[s] for s in dfa_states if self.accepts & s]

        # Return the final DFA
        return DFA(
            states=list(dfa_states.values()),
            alphabet=[s for s in self.alphabet if s != '&'],
            transitions=dfa_trans,
            start='q0',
            accepts=dfa_accepts
        )

# This class represents a DFA (Deterministic Finite Automaton)
class DFA:
    def __init__(self, states, alphabet, transitions, start, accepts):
        self.states = states            # All states in the DFA
        self.alphabet = alphabet        # Allowed input symbols
        self.transitions = transitions  # Transition table
        self.start = start              # Start state
        self.accepts = accepts          # Accept (final) states

    # Check if the DFA accepts a given input string
    def accepts_string(self, string):
        current_state = self.start
        for symbol in string:
            if symbol not in self.alphabet:  # Reject if invalid symbol
                return False
            if current_state not in self.transitions or symbol not in self.transitions[current_state]:
                return False  # No transition found
            current_state = self.transitions[current_state][symbol]  # Move to next state
        return current_state in self.accepts  # Accept if end in final state

# Run this part only when the script is executed directly
if __name__ == "__main__":
    # Define an NFA with 3 states and epsilon transition
    nfa = NFA(
        states={'q0', 'q1', 'q2'},
        alphabet={'a', 'b', '&'},
        transitions={
            'q0': {'&': {'q1'}},                 # Epsilon move from q0 to q1
            'q1': {'a': {'q2'}, 'b': {'q2'}},    # q1 goes to q2 on 'a' or 'b'
            'q2': {}                             # q2 has no transitions
        },
        start='q0',        # Starting state
        accepts={'q2'}     # Final state
    )

    # Convert the NFA to DFA
    dfa = nfa.to_dfa()

    # List of test strings to check
    test_strings = [
        "a",      # T
        "b",      # T
        "aa",     # F
        "ab",     # F
        "ba",     # F
        "bb",     # F
        "aaaabb"  # F
    ]

    # Run the tests and print results
    for test_string in test_strings:
        result = dfa.accepts_string(test_string)
        print(f"Does the DFA accept '{test_string}'? {result}")
