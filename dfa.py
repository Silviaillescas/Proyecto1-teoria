class DFA:
    def __init__(self, start_state, transitions, accept_states):
        self.start_state = start_state
        self.transitions = transitions
        self.accept_states = accept_states

def epsilon_closure(states, nfa):
    stack = list(states)
    closure = set(states)

    while stack:
        state = stack.pop()
        if 'ε' in state.transitions:
            for next_state in state.transitions['ε']:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)

    return closure

def move(states, symbol):
    result = set()
    for state in states:
        if symbol in state.transitions:
            result.update(state.transitions[symbol])
    return result

def construct_dfa_from_nfa(nfa):
    start_closure = epsilon_closure({nfa.start}, nfa)
    dfa_states = {frozenset(start_closure): 0}
    dfa_transitions = {}
    dfa_accept_states = set()
    
    unmarked_states = [frozenset(start_closure)]
    state_count = 1
    
    while unmarked_states:
        current_set = unmarked_states.pop()
        current_state_id = dfa_states[current_set]

        dfa_transitions[current_state_id] = {}
        
        for symbol in ['a', 'b']:  # Puedes generalizar esto según el alfabeto
            next_set = epsilon_closure(move(current_set, symbol), nfa)
            if not next_set:
                continue
            
            if frozenset(next_set) not in dfa_states:
                dfa_states[frozenset(next_set)] = state_count
                unmarked_states.append(frozenset(next_set))
                state_count += 1
            
            dfa_transitions[current_state_id][symbol] = dfa_states[frozenset(next_set)]
        
        if any(state == nfa.end for state in current_set):
            dfa_accept_states.add(current_state_id)

    return DFA(0, dfa_transitions, dfa_accept_states)

def visualize_dfa(dfa, graph):
    for state, transitions in dfa.transitions.items():
        graph.node(str(state), shape="circle")
        for symbol, next_state in transitions.items():
            graph.edge(str(state), str(next_state), label=symbol)

    for accept_state in dfa.accept_states:
        graph.node(str(accept_state), shape="doublecircle")
