# Laboratorio 3 - Problema 1
# Este programa reutiliza el algoritmo de Shunting Yard del laboratorio pasado


import matplotlib.pyplot as plt


PRECEDENCIA = {
    '|': 1,
    '~': 2,   # concatenacion explicita
    '*': 3,
    '+': 3,
    '?': 3
}

OPERADORES = ['(', ')', '|', '~', '*', '+', '?']


def tokenizar(expresion):
    tokens = []
    i = 0
    while i < len(expresion):
        caracter = expresion[i]
        if caracter == '\\' and i + 1 < len(expresion):
            tokens.append(expresion[i:i + 2])
            i += 2
        else:
            tokens.append(caracter)
            i += 1
    return tokens


def es_operando(token):
    return token not in OPERADORES


def insertar_concatenacion(tokens):
    tokens_nuevos = []
    for i in range(len(tokens)):
        token_actual = tokens[i]
        tokens_nuevos.append(token_actual)

        if i + 1 < len(tokens):
            token_siguiente = tokens[i + 1]
            termina_subexpresion = es_operando(token_actual) or token_actual == ')' or token_actual in ('*', '+', '?')
            empieza_subexpresion = es_operando(token_siguiente) or token_siguiente == '('
            if termina_subexpresion and empieza_subexpresion:
                tokens_nuevos.append('~')

    return tokens_nuevos


def shunting_yard(tokens):
    salida = []
    pila = []

    print("Token leido | Salida despues del token | Pila despues del token")

    for token in tokens:
        if es_operando(token):
            salida.append(token)
        elif token == '(':
            pila.append(token)
        elif token == ')':
            while len(pila) > 0 and pila[-1] != '(':
                salida.append(pila.pop())
            if len(pila) > 0:
                pila.pop()
        else:
            while (len(pila) > 0 and pila[-1] != '(' and
                   PRECEDENCIA.get(pila[-1], 0) >= PRECEDENCIA.get(token, 0)):
                salida.append(pila.pop())
            pila.append(token)

        print("     " + token + "        |  " + "".join(salida) + "   |  " + "".join(pila))

    while len(pila) > 0:
        salida.append(pila.pop())
        print("   (vaciando pila)   |  " + "".join(salida) + "   |  " + "".join(pila))

    return salida   # lista de tokens en postfix (no la unimos en string todavia)



# PARTE 2: Postfix -> Arbol sintactico

# El arbol se construye directo de la lista de tokens en postfix, no del string. Por eso el shunting_yard de arriba regresa una lista, no un string ya unido.

class Nodo:
    def __init__(self, valor, izquierdo=None, derecho=None):
        self.valor = valor
        self.izquierdo = izquierdo
        self.derecho = derecho


def copiar_arbol(nodo):
    # hace una copia independiente del subarbol, para que al usarlo dos veces 
    if nodo is None:
        return None
    return Nodo(nodo.valor, copiar_arbol(nodo.izquierdo), copiar_arbol(nodo.derecho))


def postfix_a_arbol(tokens_postfix):
    pila = []

    for token in tokens_postfix:

        if token == '~':
            # concatenacion: operador binario
            derecho = pila.pop()
            izquierdo = pila.pop()
            nodo = Nodo('concat', izquierdo, derecho)
            pila.append(nodo)

        elif token == '|':
            # union: operador binario
            derecho = pila.pop()
            izquierdo = pila.pop()
            nodo = Nodo('|', izquierdo, derecho)
            pila.append(nodo)

        elif token == '*':
            # estrella de kleene: operador unario
            hijo = pila.pop()
            nodo = Nodo('*', hijo, None)
            pila.append(nodo)

        elif token == '+':
            # SIMPLIFICACION: x+  equivale a  x . x* entonces en vez de crear un nodo "+", creamos directamente un nodo de concatenacion entre x  y  (x)*
        
            hijo = pila.pop()
            copia_hijo = copiar_arbol(hijo)
            nodo_estrella = Nodo('*', copia_hijo, None)
            nodo = Nodo('concat', hijo, nodo_estrella)
            pila.append(nodo)

        elif token == '?':
            # SIMPLIFICACION: x?  equivale a  (x | epsilon)
            hijo = pila.pop()
            nodo_epsilon = Nodo('eps', None, None)
            nodo = Nodo('|', hijo, nodo_epsilon)
            pila.append(nodo)

        else:
            # operando: una letra o un simbolo literal (incluye escapados)
            nodo = Nodo(token, None, None)
            pila.append(nodo)

    return pila[-1]   # la raiz del arbol queda como unico elemento de la pila



# PARTE 3: Dibujar el arbol con matplotlib


def calcular_posiciones(nodo, profundidad, contador_x):
    # recorrido in-order: primero el hijo izquierdo, despues este nodo, despues el hijo derecho. 
    if nodo is None:
        return

    if nodo.izquierdo is not None:
        calcular_posiciones(nodo.izquierdo, profundidad + 1, contador_x)

    nodo.pos_x = contador_x[0]
    nodo.pos_y = -profundidad
    contador_x[0] = contador_x[0] + 1

    if nodo.derecho is not None:
        calcular_posiciones(nodo.derecho, profundidad + 1, contador_x)


def dibujar_conexiones(ax, nodo):
    if nodo is None:
        return
    if nodo.izquierdo is not None:
        ax.plot([nodo.pos_x, nodo.izquierdo.pos_x], [nodo.pos_y, nodo.izquierdo.pos_y], color="gray", zorder=1)
        dibujar_conexiones(ax, nodo.izquierdo)
    if nodo.derecho is not None:
        ax.plot([nodo.pos_x, nodo.derecho.pos_x], [nodo.pos_y, nodo.derecho.pos_y], color="gray", zorder=1)
        dibujar_conexiones(ax, nodo.derecho)


def dibujar_nodos(ax, nodo):
    if nodo is None:
        return

    etiqueta = nodo.valor
    if etiqueta == 'concat':
        etiqueta = '.'
    if etiqueta == 'eps':
        etiqueta = 'ε'

    ax.scatter([nodo.pos_x], [nodo.pos_y], s=900, color="#cfe8ff", edgecolors="#3366cc", zorder=2)
    ax.text(nodo.pos_x, nodo.pos_y, etiqueta, ha="center", va="center", fontsize=12, zorder=3)

    dibujar_nodos(ax, nodo.izquierdo)
    dibujar_nodos(ax, nodo.derecho)


def dibujar_arbol(raiz, titulo):
    contador_x = [0]
    calcular_posiciones(raiz, 0, contador_x)

    figura, ax = plt.subplots(figsize=(10, 6))
    dibujar_conexiones(ax, raiz)
    dibujar_nodos(ax, raiz)

    ax.set_title(titulo)
    ax.axis("off")
    plt.tight_layout()
    plt.show()


# PARTE 4: Programa principal


def main():
    nombre_archivo = "regex.txt"

    try:
        archivo = open(nombre_archivo, "r", encoding="utf-8")
    except FileNotFoundError:
        print("No se encontro el archivo:", nombre_archivo)
        return

    lineas = archivo.readlines()
    archivo.close()

    numero_linea = 1
    for linea in lineas:
        linea = linea.strip()

        if linea == "":
            continue

        print("=" * 70)
        print("Expresion " + str(numero_linea) + " (infix): " + linea)
        print("-" * 70)

        tokens = tokenizar(linea)
        tokens_con_concat = insertar_concatenacion(tokens)
        print("Con concatenacion explicita (~): " + "".join(tokens_con_concat))
        print("-" * 70)

        tokens_postfix = shunting_yard(tokens_con_concat)
        print("-" * 70)
        print("RESULTADO POSTFIX: " + "".join(tokens_postfix))
        print()

        raiz_arbol = postfix_a_arbol(tokens_postfix)

        print("Mostrando arbol sintactico en pantalla... (cierra la ventana para continuar)")
        dibujar_arbol(raiz_arbol, "Arbol sintactico de: " + linea)

        numero_linea = numero_linea + 1


main()
