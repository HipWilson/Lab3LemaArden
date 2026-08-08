# Laboratorio 3 - Teoría de la Computación

## Video de ejecución (Problema 1)
[Link del video](https://youtube.com/tu-link-aqui)

## Estructura del repositorio
- `problema1/` — `arbol_sintactico.py` + `regex.txt` (infix → postfix → árbol sintáctico)
- `problema2/` — Lema de Arden (PDF)

## Problema 1 — Árbol sintáctico
```
cd problema1
python3 arbol_sintactico.py
```
El programa muestra en consola la conversión infix → postfix y luego abre una ventana con el árbol
sintáctico dibujado y cierra la ventana para pasar a la siguiente expresión.

Simplificaciones aplicadas al construir el árbol:
- `x+` se construye como el nodo de concatenación de `x` y `x*`
- `x?` se construye como el nodo de unión de `x` y `ε`
