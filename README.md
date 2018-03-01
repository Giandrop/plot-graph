plot-graph
=====

Programa hecho en Python para dibujar grafos

Proyecto final de la materia "Complementos Matemáticos I"

Hecho en base al algoritmo de Fruchterman y Reingold para dibujar gráficos: http://citeseer.ist.psu.edu/viewdoc/download;jsessionid=19A8857540E8C9C26397650BBACD5311?doi=10.1.1.13.8444&rep=rep1&type=pdf

# Requisitos
* gnuplot (recomendado gnuplot5)
* py-gnuplot: http://sourceforge.net/projects/gnuplot-py/files/latest/download?source=files

# Uso
El programa carga grafos desde archivos de texto. El formato de los grafos es el siguiente:
La primera línea indica la cantidad de nodos que tiene el grafo. Las líneas siguientes indican el nombre de cada uno de los nodos del grafo. 
Y por último, las líneas restantes representan las aristas, definidas por pares de nodos.

Ejemplo:

        3
        A
        B
        C
        A B
        B C
        C B
        
### Para ejecutar el programa:
> $python plot-graph.py _grafo_


### Para más opciones:
> $python plot-graph.py -h
