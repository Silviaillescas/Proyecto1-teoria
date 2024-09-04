from nfa import State


class DFA:
    def __init__(self, start_state, transitions, accept_states):
        self.start_state = start_state
        self.transitions = transitions
        self.accept_states = accept_states


def epsilon_closure(states):
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
        if isinstance(state, State):  # Asegurarse de que 'state' es un objeto de la clase State
            if symbol in state.transitions:
                result.update(state.transitions[symbol])
    return result


def construct_dfa_from_nfa(nfa):
    start_closure = epsilon_closure({nfa.start})
    dfa_states = {frozenset(start_closure): 0}
    dfa_transitions = {}
    dfa_accept_states = set()
    
    unmarked_states = [frozenset(start_closure)]
    state_count = 1
    
    alphabet = set()
    for state in start_closure:
        alphabet.update(state.transitions.keys())
    alphabet.discard('ε')  # Remover epsilon del alfabeto

    while unmarked_states:
        current_set = unmarked_states.pop()
        current_state_id = dfa_states[current_set]

        dfa_transitions[current_state_id] = {}
        
        for symbol in alphabet:
            next_set = epsilon_closure(move(current_set, symbol))
            if not next_set:
                continue
            
            next_set_frozen = frozenset(next_set)
            if next_set_frozen not in dfa_states:
                dfa_states[next_set_frozen] = state_count
                unmarked_states.append(next_set_frozen)
                state_count += 1
            
            dfa_transitions[current_state_id][symbol] = dfa_states[next_set_frozen]
        
        if any(state == nfa.end for state in current_set):
            dfa_accept_states.add(current_state_id)

    return DFA(0, dfa_transitions, dfa_accept_states)



def visualize_dfa(dfa, graph):
    for state, transitions in dfa.transitions.items():
        shape = "doublecircle" if state in dfa.accept_states else "circle"
        graph.node(str(state), shape=shape)
        
        for symbol, next_state in transitions.items():
            graph.edge(str(state), str(next_state), label=symbol)

def minimize_dfa(dfa):
    def distinguishable_pairs(dfa):
        states = list(dfa.transitions.keys())
        P = {}
        for i in range(len(states)):
            for j in range(i):
                if (states[i] in dfa.accept_states) != (states[j] in dfa.accept_states):
                    P[(states[i], states[j])] = True
                else:
                    P[(states[i], states[j])] = False

        changed = True
        while changed:
            changed = False
            for (s1, s2) in P:
                if not P[(s1, s2)]:
                    for symbol in dfa.transitions[s1]:
                        t1 = dfa.transitions[s1].get(symbol, None)
                        t2 = dfa.transitions[s2].get(symbol, None)
                        if t1 is not None and t2 is not None and t1 != t2 and (t1, t2) in P and P[(t1, t2)]:
                            P[(s1, s2)] = True
                            changed = True
                            break
        return P

    P = distinguishable_pairs(dfa)

    # Merge indistinguishable states
    merge_map = {}
    new_states = set(dfa.transitions.keys())
    for (s1, s2), are_distinguishable in P.items():
        if not are_distinguishable:
            merge_map[s2] = s1
            new_states.discard(s2)

    minimized_transitions = {}
    for state in new_states:
        state_repr = merge_map.get(state, state)
        if state_repr not in minimized_transitions:
            minimized_transitions[state_repr] = {}

        for symbol, target in dfa.transitions[state].items():
            target_repr = merge_map.get(target, target)
            minimized_transitions[state_repr][symbol] = target_repr

    minimized_accept_states = {merge_map.get(s, s) for s in dfa.accept_states}

    return DFA(dfa.start_state, minimized_transitions, minimized_accept_states)
