from graphviz import Digraph

class State:
    def __init__(self):
        self.transitions = {}
        self.is_accepting = False  # Estado de aceptación para el DFA

    def add_transition(self, symbol, state):
        if symbol in self.transitions:
            self.transitions[symbol].append(state)
        else:
            self.transitions[symbol] = [state]

class NFA:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    @staticmethod
    def from_symbol(symbol):
        start = State()
        end = State()
        start.add_transition(symbol, end)
        return NFA(start, end)

    @staticmethod
    def concatenate(nfa1, nfa2):
        nfa1.end.add_transition('ε', nfa2.start)
        return NFA(nfa1.start, nfa2.end)

    @staticmethod
    def union(nfa1, nfa2):
        start = State()
        end = State()
        start.add_transition('ε', nfa1.start)
        start.add_transition('ε', nfa2.start)
        nfa1.end.add_transition('ε', end)
        nfa2.end.add_transition('ε', end)
        return NFA(start, end)

    @staticmethod
    def kleene_star(nfa):
        start = State()
        end = State()
        start.add_transition('ε', nfa.start)
        start.add_transition('ε', end)
        nfa.end.add_transition('ε', nfa.start)
        nfa.end.add_transition('ε', end)
        return NFA(start, end)

    @staticmethod
    def plus(nfa):
        start = State()
        end = State()
        start.add_transition('ε', nfa.start)
        nfa.end.add_transition('ε', nfa.start)
        nfa.end.add_transition('ε', end)
        return NFA(start, end)

    @staticmethod
    def optional(nfa):
        start = State()
        end = State()
        start.add_transition('ε', nfa.start)
        start.add_transition('ε', end)
        nfa.end.add_transition('ε', end)
        return NFA(start, end)

def add_concatenation(regex):
    result = []
    for i in range(len(regex) - 1):
        result.append(regex[i])
        if regex[i] not in '(|' and regex[i+1] not in ')*+?|)':
            result.append('.')
    result.append(regex[-1])
    return ''.join(result)

def convert_to_postfix(regex):
    precedence = {'*': 3, '+': 3, '?': 3, '.': 2, '|': 1, '(': 0, ')': 0}
    output = []
    stack = []

    regex = add_concatenation(regex)  # Insertar operadores de concatenación
    i = 0
    while i < len(regex):
        char = regex[i]
        if char.isalnum() or char == 'ε':
            output.append(char)
        elif char == '[':
            j = i
            while j < len(regex) and regex[j] != ']':
                j += 1
            output.append(regex[i:j+1])
            i = j
        elif char == '(':
            stack.append(char)
        elif char == ')':
            top = stack.pop()
            while top != '(':
                output.append(top)
                top = stack.pop()
        else:
            while (stack and precedence[stack[-1]] >= precedence[char]):
                output.append(stack.pop())
            stack.append(char)
        i += 1

    while stack:
        output.append(stack.pop())

    return ''.join(output)

def construct_thompson(postfix):
    stack = []

    i = 0
    while i < len(postfix):
        char = postfix[i]
        if char.isalnum() or char == 'ε' or (char == '[' and postfix[i+1] == ']'):
            nfa = NFA.from_symbol(char)
            stack.append(nfa)
        elif char == '.':
            if len(stack) < 2:
                raise ValueError("Insufficient operands for concatenation.")
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(NFA.concatenate(nfa1, nfa2))
        elif char == '|':
            if len(stack) < 2:
                raise ValueError("Insufficient operands for union.")
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(NFA.union(nfa1, nfa2))
        elif char == '*':
            if len(stack) < 1:
                raise ValueError("Insufficient operands for Kleene star.")
            nfa = stack.pop()
            stack.append(NFA.kleene_star(nfa))
        elif char == '+':
            if len(stack) < 1:
                raise ValueError("Insufficient operands for plus.")
            nfa = stack.pop()
            stack.append(NFA.plus(nfa))
        elif char == '?':
            if len(stack) < 1:
                raise ValueError("Insufficient operands for optional.")
            nfa = stack.pop()
            stack.append(NFA.optional(nfa))
        elif char == '[':
            j = i
            while j < len(postfix) and postfix[j] != ']':
                j += 1
            nfa = NFA.from_symbol(postfix[i:j+1])
            stack.append(nfa)
            i = j
        else:
            raise ValueError(f"Unknown operator: {char}")
        i += 1

    if len(stack) != 1:
        raise ValueError(f"The postfix expression is malformed. Final stack content: {stack}")

    return stack.pop()

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
    
    while unmarked_states:
        current_set = unmarked_states.pop()
        current_state_id = dfa_states[current_set]

        dfa_transitions[current_state_id] = {}
        
        for symbol in 'abcdefghijklmnopqrstuvwxyz':  # Generalizando el alfabeto
            next_set = epsilon_closure(move(current_set, symbol))
            if not next_set:
                continue
            
            if frozenset(next_set) not in dfa_states:
                dfa_states[frozenset(next_set)] = state_count
                unmarked_states.append(frozenset(next_set))
                state_count += 1
            
            dfa_transitions[current_state_id][symbol] = dfa_states[frozenset(next_set)]
        
        if nfa.end in current_set:
            dfa_accept_states.add(current_state_id)

    return DFA(0, dfa_transitions, dfa_accept_states)

def visualize_nfa(start_state, graph, state_map, count):
    if start_state in state_map:
        return state_map[start_state]

    state_id = str(count[0])
    state_map[start_state] = state_id
    graph.node(state_id, "State")
    count[0] += 1

    for symbol, states in start_state.transitions.items():
        for state in states:
            target_id = visualize_nfa(state, graph, state_map, count)
            graph.edge(state_id, target_id, label=symbol)

    return state_id

def visualize_dfa(dfa, graph):
    for state, transitions in dfa.transitions.items():
        graph.node(str(state), shape="circle")
        for symbol, next_state in transitions.items():
            graph.edge(str(state), str(next_state), label=symbol)

    for accept_state in dfa.accept_states:
        graph.node(str(accept_state), shape="doublecircle")

# Nueva función para minimizar DFA
def minimize_dfa(dfa):
    # Implementación del algoritmo de minimización
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

# Función para procesar el archivo
def process_file(filename):
    with open(filename, 'r') as file:
        expressions = file.readlines()

    for i, expression in enumerate(expressions):
        expression = expression.strip()
        try:
            postfix = convert_to_postfix(expression)
            nfa = construct_thompson(postfix)
            
            # Visualizar el AFN
            graph_nfa = Digraph()
            visualize_nfa(nfa.start, graph_nfa, {}, [0])
            graph_nfa.render(filename=f'afn_{i+1}', format='png', cleanup=True)
            print(f'NFA for \"{expression}\" generated as afn_{i+1}.png')
            
            # Convertir el AFN a DFA
            dfa = construct_dfa_from_nfa(nfa)
            
            # Minimizar el DFA
            minimized_dfa = minimize_dfa(dfa)
            
            # Visualizar el DFA
            graph_dfa = Digraph()
            visualize_dfa(minimized_dfa, graph_dfa)
            graph_dfa.render(filename=f'afd_{i+1}_minimizado', format='png', cleanup=True)
            print(f'DFA Minimizado for \"{expression}\" generated as afd_{i+1}_minimizado.png')
        
        except Exception as e:
            print(f"Error processing expression '{expression}': {str(e)}")

if __name__ == "__main__":
    process_file('expresiones.txt')
