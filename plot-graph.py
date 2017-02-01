#! /usr/bin/python
# coding=utf-8

# fixes:
# fuerza que separa los nodos ahora es independiente de la temperatura

import argparse
import Gnuplot
import random
import time

def leer_grafo_archivo(file_path):
    '''
    Lee un grafo desde un archivo y devuelve su representacion como lista.
    Ejemplo Entrada: 
        3
        A
        B
        C
        A B
        B C
        C B
    Ejemplo retorno: 
        (['A','B','C'],[('A','B'),('B','C'),('C','B')])
    '''
    V = []
    E = []
    f = open(file_path, 'r')
    n = int(f.readline().strip(" \n"))
    for i in range(1, n+1):
        V.append(f.readline().strip(" \n"))
    for line in iter(f):
        [n0, n1] = line.strip(" \n").split(' ')
        E.append((n0,n1))
    return (V,E)

class Vector():
    x = 0
    y = 0
   
    def __init__(self, x, y):
        self.x = x
        self.y = y
       
    def add(self, v):
        self.x += v.x
        self.y += v.y
        return self
          
    def modulo(self):
        return (self.x**2 + self.y**2)**0.5
       
    def scalar(self, n):
        self.x *= n
        self.y *= n
        return self
        
    def versor(self):
        self.scalar(1/self.modulo())
        return self

       
class LayoutGraph:
    
    g = Gnuplot.Gnuplot()
    
    def __init__(self, grafo, iters, refresh, pause, W, H, c1, c2, eps, force,
                 grav, temp, cool, verbose):
        '''    
        Parametros de layout:
        iters: cantidad de iteraciones a realizar
        refresh: Numero de iteraciones entre actualizaciones de pantalla. 
        0 -> se grafica solo al final.
        c1: constante usada para calcular la repulsion entre nodos
        c2: constante usada para calcular la atraccion de aristas
        '''

        # Guardo el grafo
        self.grafo = leer_grafo_archivo(grafo)

        # Inicializo estado
        self.posiciones = {v : Vector(0,0) for v in self.grafo[0]}
        self.fuerzas = {v : Vector(0,0) for v in self.grafo[0]}        
        
        # Guardo opciones
        self.iters = iters
        self.refresh = refresh
        self.pause = pause
        self.k1 = (W*H/len(self.grafo[0]))**0.5
        self.k2 = 2*len(self.grafo[1]) / float(len(self.grafo[0])**2)
        '''k2 es la relación entra cantidad de aristas y cantidad de nodos.
        Para los completos, cuando la cantidad de aristas es máxima, k2 es
        igual a 1, para menos aristas, k2 es menor a 1. 
        Esto se multiplica a c1, haciendo que la fuerza de atraccion sea mínima
        para los grafos con muchas aristas (como los completos) y máxima para 
        grafos con pocas aristas (como los árboles).'''
        self.c1 = c1 * self.k1 * self.k2
        self.c2 = c2 * self.k1
        self.nsize = self.k1 * 0.03 #tamaño de los nodos
        self.eps = 2*self.nsize*eps #distancia mínima entre dos nodos
        self.Fc = 2*self.nsize*force #fuerza que separa dos nodos cercanos
        self.W = W
        self.H = H
        self.grav = grav
        self.temp = temp
        self.cool = cool
        self.verbose = verbose

    def randomize(self):
        ''' Inicializa en forma aleatoria las posiciones de los nodos'''
        self.posiciones = {v : Vector(random.random()*self.W,random.random()*
            self.H) for v in self.grafo[0]}
        pass


    def step(self):
        ''' Efectua un paso de la simulacion fisica y actualiza las posiciones \
        de los nodos'''
        
        # 1: Calcular repulsiones de nodos (actualiza fuerzas)
        for i, v in enumerate(self.grafo[0]):
            F = Vector(0,0)
            for u in self.grafo[0]:
                dx = self.posiciones[v].x - self.posiciones[u].x
                dy = self.posiciones[v].y - self.posiciones[u].y
                d = (dx**2 + dy**2)**0.5
                if d > self.eps:
                    mod = self.c2**2 / d
                    F.add(Vector(mod * dx / d, mod * dy / d))
            self.fuerzas[v].add(F)
            if self.verbose:
                print "Fuerza de repulsión de", i, ":", F.modulo(), F.x, F.y
                    
        # 2: Calcular atracciones de aristas (actualiza fuerzas)
        for v,u in self.grafo[1]:
            dx = self.posiciones[u].x - self.posiciones[v].x
            dy = self.posiciones[u].y - self.posiciones[v].y
            d = (dx**2 + dy**2)**0.5
            mod = d**2 / self.c1
            if d != 0:
                F = Vector(mod * dx / d, mod * dy / d)
                self.fuerzas[v].add(F)
                self.fuerzas[u].add(F.scalar(-1))
                if self.verbose:
                    print "Fuerza de atracción de", self.grafo[0].index(v), \
                        self.grafo[0].index(u), ":", F.modulo(), F.x, F.y

        # 3: Calcular fuerza de gravedad (opcional)
        
        for i, v in enumerate(self.grafo[0]):
            dx = self.posiciones[v].x - self.W/2
            dy = self.posiciones[v].y - self.H/2
            d = (dx**2 + dy**2)**0.5
            mod = self.grav
            mod = min(mod, d)
            if d != 0:
                F = Vector(mod * dx / d, mod * dy / d)
                F = F.scalar(-1)
                self.fuerzas[v].add(F)
                if self.verbose:
                    print "Fuerza de gravedad de", i, ":", F.modulo(), F.x, F.y
                    
        # 4: En base a fuerzas, actualizar posiciones, setear fuerzas a cero     
        for i, v in enumerate(self.grafo[0]):
            minimo = min((self.fuerzas[v]).modulo(), self.temp)
            if self.fuerzas[v].modulo() != 0:
                versor = (self.fuerzas[v]).versor()
                self.fuerzas[v] = versor.scalar(minimo)
            if self.verbose:
                print "Fuerza acumulada de", i, ":", self.fuerzas[v].modulo(),\
                self.fuerzas[v].x, self.fuerzas[v].y
            self.posiciones[v].add(self.fuerzas[v])    
            self.fuerzas[v] = Vector(0,0)
        self.temp *= self.cool
        if self.verbose:
            print "Temperatura:", self.temp

        # 5: Separar nodos que estan muy juntos
        for v in self.grafo[0]:
            for u in self.grafo[0]:
                dy = self.posiciones[v].x - self.posiciones[u].x
                dx = self.posiciones[v].y - self.posiciones[u].y
                d = (dx**2 + dy**2)**0.5
                if d <= self.eps:
                    x = random.random()
                    y = (1 - x**2)**0.5
                    w = Vector(x, y)
                    w.scalar(self.Fc)                   
                    self.posiciones[v].add(w)
                    self.posiciones[u].add(w.scalar(-1))

        # 6: Mantener en pantalla todos los nodos
        for v in self.grafo[0]:
            (self.posiciones[v]).x = min(self.W - self.nsize, max(self.nsize, (self.posiciones[v]).x))
            (self.posiciones[v]).y = min(self.H - self.nsize, max(self.nsize, (self.posiciones[v]).y)) 


    def dibujar(self):
        ''' Dibuja (o actualiza) el estado del grafo gr en pantalla'''
        
        self.g('unset for [n = 1:'+str(len(self.grafo[1]))+'] arrow n')
        
        # Dibuja aristas
        for (u, v) in self.grafo[1]:
            self.g('set arrow nohead from '
            +str(self.posiciones[v].x)+','+str(self.posiciones[v].y)
            +' to '
            +str(self.posiciones[u].x)+','+str(self.posiciones[u].y))
        
        # Dibuja nodos
        for i,v in enumerate(self.grafo[0]):

            self.g('set object '+str(i+1)+' circle center '
            +str(self.posiciones[v].x)+','+str(self.posiciones[v].y)
            +' size '+str(self.nsize)+' front fc rgbcolor "white" fs solid border lt 1 lc rgbcolor "black')
            
        self.g('plot NaN notitle ')
        if self.pause:
            raw_input("Presione enter para continuar")
            #self.g('pause mouse keypress')
        #else:
            #self.g('pause 0.3')

    def layout(self):
        '''
        Aplica el algoritmo de Fruchtermann-Reingold para obtener (y mostrar) 
        un layout        
        '''
        
        # Ponerle titulo
        self.g('set title "GRAFO"')
        # setear el intervalo a mostrar
        self.g('set xrange [0:'+str(self.W)+']; set yrange [0:'+str(self.H)+']')
        # self.g('plot NaN')
        
        # Inicializamos las posiciones
        self.randomize()

        # Si es necesario, lo mostramos por pantalla
        if (self.refresh > 0):
            self.dibujar()

        # Bucle principal
        for i in range(0, self.iters):
            
            if self.verbose:
                print "Iteración:", i
                
            # Realizar un paso de la simulacion
            self.step()
                
            # Si es necesario, lo mostramos por pantalla
            if (self.refresh > 0 and i % self.refresh == 0):
                self.dibujar()
        
        # Ultimo dibujado al final
        self.dibujar()
        #self.g('pause mouse keypress')
        raw_input("Presione enter para finalizar")

def main():
    # Definimos los argumentos de lina de comando que aceptamos
    parser = argparse.ArgumentParser()

    # Archivo de grafo
    parser.add_argument('filename', type=str, 
                        help='Archivo del cual leer el grafo')

    # Verbosidad, opcional, False por defecto
    parser.add_argument('-v', '--verbose', 
                        action='store_true', 
                        help='Muestra mas informacion',
                        default=False)
                        
    # Cantidad de iteraciones, opcional, 150 por defecto
    parser.add_argument('-i', '--iters', type=int, 
                        help='Cantidad de iteraciones a efectuar', 
                        default=150)

    # Refresh
    parser.add_argument('-r', '--refresh', type=int, 
                        help='Cada cuantas iteraciones se dibuja el grafo. \
                            0: se dibuja solo al finalizar',
                        default=0)
    # Pausa
    parser.add_argument('-p', '--pause', action='store_true',
                        help='Pausa en cada iteracion',
                        default=False)
                    
    # Width
    parser.add_argument('-W', '--width', type=float, 
                        help='Ancho', default=15000)

    # Height
    parser.add_argument('-H', '--height', type=float, 
                        help='Alto', default=10000)

    # Epsilon
    parser.add_argument('--eps', type=float, 
                        help='Distancia mínima entre dos nodos (en relacion al \
                            tamaño)', 
                        default=2)

    # Force
    parser.add_argument('--force', type=float, 
                        help='Modulo de la fuerza que separa dos nodos cercanos\
                             (relativo al tamaño de los nodos)', 
                        default=3)
                        
    # C1 (Fuerza de atraccion)
    parser.add_argument('--c1', type=float, 
                        help='Constante usada para calcular la fuerza de \
                            repulsión entre nodos', 
                        default=0.75)
                        
    # C2 (Fuerza de repulsion)
    parser.add_argument('--c2', type=float, 
                        help='Constante usada para calcular la fuerza de \
                            atracción entre nodos',
                        default=0.75)

    # Gravedad
    parser.add_argument('-g', '--grav', type=float, 
                        help='Fuerza de gravedad',
                        default=200)

    # Temperatura
    parser.add_argument('-t', '--temp', type=float, 
                        help='Temperatura (distancia máxima que se podrá mover\
                            un nodo en cada iteración)',
                        default=4505)

    # Enfriamiento
    parser.add_argument('-c', '--cool', type=float, 
                        help='Constante por la que se multiplicará la \
                            temeratura en cada iteración', 
                        default=0.95)

    args = parser.parse_args()

    # Creamos nuestro objeto LayoutGraph
    layout_gr = LayoutGraph(
        grafo=args.filename,
        iters=args.iters,
        refresh=args.refresh,
        pause=args.pause,
        W=args.width,
        H=args.height,
        c1=args.c1,
        c2=args.c2,
        eps=args.eps,
        force=args.force,
        grav=args.grav,
        temp=args.temp,
        cool=args.cool,
        verbose=args.verbose
    )
    
    # Ejecutamos el layout
    layout_gr.layout()
    return

if __name__ == '__main__':
    main()
