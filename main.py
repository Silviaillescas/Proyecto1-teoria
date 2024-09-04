from graphviz import Digraph

# Clase para manejar los estados del automata
class State:

    #Constructor para inicializar un estado de un autómata (AFN o AFD).
    # transitions: Un diccionario que contiene las transiciones de este estado. La clave es el símbolo, y el valor es una lista de estados a los que puede moverse.
    #is_accepting: Un booleano que indica si este estado es un estado de aceptación (final).
    #name: Opcional, puede asignarse un nombre o identificador al estado. Si no se proporciona, se usa el id único del objeto.

    def __init__(self, name=None):
        self.transitions = {}
        self.is_accepting = False  # Estado de aceptación para el DFA
        self.name = name if name is not None else id(self)  # Opcional: agregar un nombre o identificador

    #Agrega una transición desde este estado hacia otro estado.
    #symbol: El símbolo con el que se realiza la transición.
    #state: El estado de destino al que se mueve al leer el símbolo.
    #Si ya existe una transición con el símbolo dado, el nuevo estado se agrega a la lista de destinos.

    def add_transition(self, symbol, state):
        if symbol in self.transitions:
            self.transitions[symbol].append(state)
        else:
            self.transitions[symbol] = [state]

    # Sobrescribimos __repr__ para una representación más legible
    def __repr__(self):
        return f"State({self.name})"

    # Método para convertir el estado en una cadena de texto cuando se imprime o se convierte en string.
    def __str__(self):
        return self.__repr__()
    
# Clase para NON DETERMINITSIC FINIT AUTOMAT
class NFA:
    # Inicializa el NFA con un estado inicial y final.
    def __init__(self, start, end):
        self.start = start
        self.end = end

    @staticmethod
    # Crea un NFA simple con una transición desde el estado inicial al final.
    def from_symbol(symbol):
        start = State()
        end = State()
        start.add_transition(symbol, end)
        return NFA(start, end)

    @staticmethod
    # Concatenación de dos NFAs, uniendo el final de nfa1 con el inicio de nfa2.        
    def concatenate(nfa1, nfa2):
        nfa1.end.add_transition('ε', nfa2.start)
        return NFA(nfa1.start, nfa2.end)

    @staticmethod
    # Unión de dos NFAs, agregando un nuevo estado inicial y final.
    def union(nfa1, nfa2):
        start = State()
        end = State()
        start.add_transition('ε', nfa1.start)
        start.add_transition('ε', nfa2.start)
        nfa1.end.add_transition('ε', end)
        nfa2.end.add_transition('ε', end)
        return NFA(start, end)

    @staticmethod
     # Aplica la estrella de Kleene al NFA, permitiendo cero o más repeticiones.
    def kleene_star(nfa):
        start = State()
        end = State()
        start.add_transition('ε', nfa.start)
        start.add_transition('ε', end)
        nfa.end.add_transition('ε', nfa.start)
        nfa.end.add_transition('ε', end)
        return NFA(start, end)

    # Aplica la operación "más" (una o más repeticiones).
    @staticmethod
    def plus(nfa):
        start = State()
        end = State()
        start.add_transition('ε', nfa.start)
        nfa.end.add_transition('ε', nfa.start)
        nfa.end.add_transition('ε', end)
        return NFA(start, end)

    # Aplica la opción, permitiendo que el NFA ocurra una vez o no.
    @staticmethod
    def optional(nfa):
        start = State()
        end = State()
        start.add_transition('ε', nfa.start)
        start.add_transition('ε', end)
        nfa.end.add_transition('ε', end)
        return NFA(start, end)

# Añade el operador de concatenación '.' implícito entre los símbolos donde sea necesario.
def add_concatenation(regex):
    result = []
    for i in range(len(regex) - 1):
        result.append(regex[i])
        if regex[i] not in '(|' and regex[i+1] not in ')*+?|)':
            result.append('.')
    result.append(regex[-1])
    return ''.join(result)

# Convierte una expresión regular infija en notación postfix (RPN).
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

 # Construye un AFN usando el algoritmo de Thompson a partir de una expresión postfix.    
def construct_thompson(postfix):
    # Pila para almacenar los AFNs parciales.
    stack = []

    i = 0
    while i < len(postfix):
        char = postfix[i]
        if char.isalnum() or char == 'ε' or (char == '[' and postfix[i+1] == ']'):
            # Crea un AFN simple para un símbolo y lo apila.
            nfa = NFA.from_symbol(char)
            stack.append(nfa)
        elif char == '.':
            # Concatenación: combina los dos últimos AFNs apilados.
            if len(stack) < 2:
                raise ValueError("Insufficient operands for concatenation.")
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(NFA.concatenate(nfa1, nfa2))
            # MANEJO CARACTERES ESPECIALES:
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

# Inicializa un Autómata Finito Determinista (DFA).
#start_state: El estado inicial del DFA.
#transitions: Un diccionario que define las transiciones. La clave es el estado actual, y el valor es un diccionario de símbolos que mapean a los estados de destino.
#accept_states: Conjunto de estados de aceptación (finales) del DFA.
class DFA:
    def __init__(self, start_state, transitions, accept_states):
        self.start_state = start_state
        self.transitions = transitions
        self.accept_states = accept_states

#Calcula el cierre epsilon de un conjunto de estados.
#El cierre epsilon es el conjunto de todos los estados que se pueden alcanzar desde los estados actuales
#a través de transiciones epsilon (ε) sin consumir ningún símbolo.
#states: Conjunto de estados desde los cuales calcular el cierre epsilon.
#Retorna:
#- closure: Un conjunto de estados que se pueden alcanzar con transiciones epsilon.
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


#Realiza una transición desde un conjunto de estados usando un símbolo específico.
#states: Conjunto de estados actuales desde los cuales se realizará la transición.
#symbol: El símbolo que se usa para mover desde los estados actuales.
#Retorna:
#result: Conjunto de estados alcanzables al consumir el símbolo desde los estados dados.
def move(states, symbol):
    result = set()
    for state in states:
        if symbol in state.transitions:
            result.update(state.transitions[symbol])
    return result


#Convierte un AFN (NFA) a un AFD (DFA) usando el algoritmo de subconjuntos.
#  - nfa: El autómata finito no determinista (NFA) de entrada.
#RRetorna: Un DFA que es equivalente al NFA dado.
def construct_dfa_from_nfa(nfa):
    # Obtén el cierre epsilon del estado inicial del NFA.
    start_closure = epsilon_closure({nfa.start})

    # Mapear los subconjuntos de estados del NFA a los estados del DFA.
    dfa_states = {frozenset(start_closure): 0}
    dfa_transitions = {}
    dfa_accept_states = set()
    
    unmarked_states = [frozenset(start_closure)]
    state_count = 1

    # Procesa cada subconjunto de estados del NFA.
    while unmarked_states:
        current_set = unmarked_states.pop()
        current_state_id = dfa_states[current_set]

        dfa_transitions[current_state_id] = {}
        
        for symbol in 'abcdefghijklmnopqrstuvwxyz0123456789':  # Incluye más símbolos si es necesario
            next_set = epsilon_closure(move(current_set, symbol))
            if not next_set:
                continue

            # Si el subconjunto de estados alcanzado aún no está en el DFA, se añade.
            if frozenset(next_set) not in dfa_states:
                dfa_states[frozenset(next_set)] = state_count
                unmarked_states.append(frozenset(next_set))
                state_count += 1
            
            # Añade la transición para el símbolo en el DFA.
            dfa_transitions[current_state_id][symbol] = dfa_states[frozenset(next_set)]
        # Si alguno de los estados en el conjunto actual es un estado final del NFA, marca este estado del DFA como de aceptación. 
        if nfa.end in current_set:
            dfa_accept_states.add(current_state_id)

    return DFA(0, dfa_transitions, dfa_accept_states)

  #Visualiza un AFN (NFA) recursivamente usando Graphviz.
def visualize_nfa(start_state, graph, state_map, count):
    if start_state in state_map:
        return state_map[start_state]

    # Asigna un ID único al estado actual y añádelo al mapa de estados.
    state_id = str(count[0])
    state_map[start_state] = state_id
    graph.node(state_id, "State")
    count[0] += 1
    
    # Recorre las transiciones del estado actual.
    for symbol, states in start_state.transitions.items():
        for state in states:
            target_id = visualize_nfa(state, graph, state_map, count)
            graph.edge(state_id, target_id, label=symbol)

    return state_id

# Visualiza un AFD (DFA) utilizando Graphviz.
#   - dfa: El autómata finito determinista (DFA) a visualizar.
#   - graph: El objeto Graphviz donde se construye el diagrama.
def visualize_dfa(dfa, graph):
    for state, transitions in dfa.transitions.items():
        graph.node(str(state), shape="circle")
        for symbol, next_state in transitions.items():
            graph.edge(str(state), str(next_state), label=symbol)

    for accept_state in dfa.accept_states:
        graph.node(str(accept_state), shape="doublecircle")

# Nueva función para minimizar DFA
#Recibe un dfa y retorna el dfa minimizado
def minimize_dfa(dfa):

    #Calcula los pares de estados distinguibles usando el algoritmo de pares.
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

    merge_map = {}
    new_states = set(dfa.transitions.keys())
    for (s1, s2), are_distinguishable in P.items():
        if not are_distinguishable:
            merge_map[s2] = s1
            new_states.discard(s2)

     # Crea las transiciones del DFA minimizado.
    minimized_transitions = {}
    for state in new_states:
        state_repr = merge_map.get(state, state)
        if state_repr not in minimized_transitions:
            minimized_transitions[state_repr] = {}

        for symbol, target in dfa.transitions[state].items():
            target_repr = merge_map.get(target, target)
            minimized_transitions[state_repr][symbol] = target_repr

    # Estados de aceptación en el DFA minimizado.
    minimized_accept_states = {merge_map.get(s, s) for s in dfa.accept_states}

    return DFA(dfa.start_state, minimized_transitions, minimized_accept_states)

# Funciones de simulación de AFN y DFA

#Simula la ejecución de un AFN sobre una cadena de entrada.
    
#   - nfa: El autómata finito no determinista (NFA) a simular.
#   - w: La cadena de entrada a procesar.
    
#    Retorna:
#   - True si la cadena es aceptada por el AFN, False en caso contrario.
def simulate_nfa(nfa, w):
    current_states = epsilon_closure({nfa.start})
    print(f"Estados actuales después del cierre epsilon: {current_states}")
    
    for symbol in w:
        next_states = set()
        print(f"Procesando símbolo: {symbol}")
        for state in current_states:
            if symbol in state.transitions:
                next_states.update(state.transitions[symbol])
                print(f"Transición de estado con símbolo '{symbol}' a: {state.transitions[symbol]}")
            else:
                print(f"No hay transición para el símbolo '{symbol}' en el estado {state}")
        current_states = epsilon_closure(next_states)
        print(f"Estados actuales después del cierre epsilon: {current_states}")
    
    result = nfa.end in current_states
    print(f"El estado final es un estado de aceptación: {result}")
    return result

#Simula la ejecución de un AFD sobre una cadena de entrada.
    
#    - dfa: El autómata finito determinista (DFA) a simular.
#    - w: La cadena de entrada a procesar.
    
#    Retorna:
#    - True si la cadena es aceptada por el DFA, False en caso contrario.
def simulate_dfa(dfa, w):
    current_state = dfa.start_state
    print(f"Iniciando simulación en el estado: {current_state}")
    
    for symbol in w:
        print(f"Símbolo actual: {symbol}")
        if symbol in dfa.transitions[current_state]:
            current_state = dfa.transitions[current_state][symbol]
            print(f"Transición al estado: {current_state}")
        else:
            print(f"No hay transición para el símbolo '{symbol}' en el estado {current_state}")
            return False
    
    is_accepting = current_state in dfa.accept_states
    print(f"Estado final: {current_state}, es estado de aceptación: {is_accepting}")
    return is_accepting

# Función para procesar el archivo
def process_file(filename, input_string):
    with open(filename, 'r') as file:
        expressions = file.readlines()

    for i, expression in enumerate(expressions):
        expression = expression.strip()
        try:
            print(f"\nProcesando expresión regular: {expression}")
            postfix = convert_to_postfix(expression)
            print(f"Postfijo: {postfix}")
            
            nfa = construct_thompson(postfix)
            print("AFN generado.")

            # Visualizar el AFN
            graph_nfa = Digraph()
            visualize_nfa(nfa.start, graph_nfa, {}, [0])
            graph_nfa.render(filename=f'afn_{i+1}', format='png', cleanup=True)
            print(f'NFA for \"{expression}\" generated as afn_{i+1}.png')
            
            # Convertir el AFN a DFA
            dfa = construct_dfa_from_nfa(nfa)
            print("AFD generado.")

            # Visualizar el DFA (sin minimizar)
            graph_dfa = Digraph()
            visualize_dfa(dfa, graph_dfa)
            graph_dfa.render(filename=f'afd_{i+1}', format='png', cleanup=True)
            print(f'DFA for \"{expression}\" generated as afd_{i+1}.png')

            # Minimizar el DFA
            minimized_dfa = minimize_dfa(dfa)
            print("AFD Minimizado generado.")

            # Visualizar el DFA minimizado
            graph_dfa_minimized = Digraph()
            visualize_dfa(minimized_dfa, graph_dfa_minimized)
            graph_dfa_minimized.render(filename=f'afd_{i+1}_minimizado', format='png', cleanup=True)
            print(f'DFA Minimizado for \"{expression}\" generated as afd_{i+1}_minimizado.png')
            
            # Simulación del AFN y AFD
            print("Iniciando simulación con la cadena:", input_string)
            nfa_result = simulate_nfa(nfa, input_string)
            dfa_result = simulate_dfa(dfa, input_string)
            minimized_dfa_result = simulate_dfa(minimized_dfa, input_string)

            print(f'Input "{input_string}" is accepted by NFA: {nfa_result}')
            print(f'Input "{input_string}" is accepted by DFA: {dfa_result}')
            print(f'Input "{input_string}" is accepted by Minimized DFA: {minimized_dfa_result}')
        
        except Exception as e:
            print(f" ")

if __name__ == "__main__":
    input_string = "ab"  # Cadena de entrada para la simulación FALSA
    #input_string = "babba"  # Cadena de entrada para la simulación VERDADERA
    process_file('expresiones.txt', input_string)
