from graphviz import Digraph

class State:
    def __init__(self):
        self.transitions = {}

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
        raise ValueError(f"La expresión postfix está mal formada. Contenido final de la pila: {stack}")

    return stack.pop()

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
