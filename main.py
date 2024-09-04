from graphviz import Digraph
from nfa import NFA, convert_to_postfix, construct_thompson, visualize_nfa
from nfa import State
from dfa import DFA, construct_dfa_from_nfa, minimize_dfa, visualize_dfa

def process_file(filename):
    try:
        with open(filename, 'r') as file:
            expressions = file.readlines()

        for i, expression in enumerate(expressions):
            expression = expression.strip()
            if not expression:
                continue

            try:
                # Convertir la expresión regular a postfix
                postfix = convert_to_postfix(expression)
                print(f"Postfix de '{expression}': {postfix}")
                
                # Construir el AFN utilizando el Algoritmo de Thompson
                nfa = construct_thompson(postfix)
                
                # Visualizar el AFN
                graph_nfa = Digraph()
                visualize_nfa(nfa.start, graph_nfa, {}, [0])
                graph_nfa.render(filename=f'afn_{i+1}', format='png', cleanup=True)
                print(f'NFA para \"{expression}\" generado como afn_{i+1}.png')
                
                # Convertir el AFN a DFA utilizando el Algoritmo de Subconjuntos
                dfa = construct_dfa_from_nfa(nfa)
                
                # Minimizar el DFA
                minimized_dfa = minimize_dfa(dfa)
                
                # Visualizar el DFA minimizado
                graph_dfa = Digraph()
                visualize_dfa(minimized_dfa, graph_dfa)
                graph_dfa.render(filename=f'afd_{i+1}_minimizado', format='png', cleanup=True)
                print(f'DFA Minimizado para \"{expression}\" generado como afd_{i+1}_minimizado.png')
            
            except ValueError as ve:
                print(f"Error procesando la expresión '{expression}': {ve}")
            except Exception as e:
                print(f"Error inesperado procesando la expresión '{expression}': {e}")

    except FileNotFoundError:
        print(f"Error: El archivo '{filename}' no fue encontrado.")
    except Exception as e:
        print(f"Error al leer el archivo '{filename}': {e}")

if __name__ == "__main__":
    process_file('expresiones.txt')
