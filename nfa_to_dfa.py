from collections import deque

# NFA 
class NFA:
    def __init__(self, states, alphabet, transitions, start, accepts):
        self.states = states            
        self.alphabet = alphabet        # Allowed input  '&'
        self.transitions = transitions  
        self.start = start              
        self.accepts = accepts         

    def epsilon_closure(self, state_set):
        stack = list(state_set)         
        closure = set(state_set)        
        while stack:
            state = stack.pop()       

            for next_state in self.transitions.get(state, {}).get('&', []):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)  
        return closure

    # Convert this NFA to a DFA 
    def to_dfa(self):
        dfa_states = {}     
        dfa_trans = {}     
        queue = deque()   

        start_closure = frozenset(self.epsilon_closure({self.start}))
        dfa_states[start_closure] = 'q0'
        queue.append(start_closure)
        counter = 1

        while queue:
            current = queue.popleft() 
            dfa_trans[dfa_states[current]] = {}

            for symbol in self.alphabet:
                if symbol == '&':   
                    continue

                move = set() 
                for state in current:
                    move.update(self.transitions.get(state, {}).get(symbol, set()))

                closure = self.epsilon_closure(move)
                frozen_closure = frozenset(closure)

                # If this state group is new, assign a new name
                if frozen_closure not in dfa_states:
                    dfa_states[frozen_closure] = f'q{counter}'
                    counter += 1
                    queue.append(frozen_closure)

                # Add the DFA transition
                dfa_trans[dfa_states[current]][symbol] = dfa_states[frozen_closure]

        # Add a "dead" missing 
        dead_state_added = False
        for state in dfa_trans:
            for symbol in self.alphabet:
                if symbol != '&' and symbol not in dfa_trans[state]:
                    dfa_trans[state][symbol] = 'dead'
                    dead_state_added = True

        if dead_state_added:
            dfa_states[frozenset()] = 'dead'
            dfa_trans['dead'] = {symbol: 'dead' for symbol in self.alphabet if symbol != '&'}

        dfa_accepts = [dfa_states[s] for s in dfa_states if self.accepts & s]

        return DFA(
            states=list(dfa_states.values()),
            alphabet=[s for s in self.alphabet if s != '&'],
            transitions=dfa_trans,
            start='q0',
            accepts=dfa_accepts
        )

class DFA:
    def __init__(self, states, alphabet, transitions, start, accepts):
        self.states = states           
        self.alphabet = alphabet       
        self.transitions = transitions 
        self.start = start             
        self.accepts = accepts          

    def accepts_string(self, string):
        current_state = self.start
        for symbol in string:
            if symbol not in self.alphabet:  
                return False
            if current_state not in self.transitions or symbol not in self.transitions[current_state]:
                return False  
            current_state = self.transitions[current_state][symbol]  
        return current_state in self.accepts  

if __name__ == "__main__":

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
