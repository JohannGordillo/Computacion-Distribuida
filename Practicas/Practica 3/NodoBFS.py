"""
======================================================================
>> Autor: Johann Gordillo
>> Email: jgordillo@ciencias.unam.mx
>> Fecha: 03/11/2020
======================================================================
Universidad Nacional Autónoma de México
Facultad de Ciencias

Computación Distribuida [2021-1]

Ejercicio 2.
Algoritmo BFS.
======================================================================
"""

import simpy

from Nodo import Nodo
from Canales.CanalRecorridos import CanalRecorridos


# La unidad de tiempo.
TICK = 1

class NodoBFS(Nodo):
    """Implementa la interfaz de Nodo para el algoritmo BFS."""
    def __init__(self, id_nodo: int, vecinos: set,
                 canal_entrada: simpy.Store,
                 canal_salida: simpy.Store):
        """Constructor para el nodo."""
        self.id_nodo = id_nodo
        self.vecinos = vecinos
        self.canal_entrada = canal_entrada
        self.canal_salida = canal_salida
        self.padre = id_nodo
        self.distancia = float('inf')
    
    def bfs(self, env: simpy.Store):
        """Implementación del algoritmo BFS."""
        if self.id_nodo == 0:
            self.distancia = 0
            data = (self.distancia, self.id_nodo)
            yield env.timeout(TICK)
            self.canal_salida.envia(data, self.vecinos)
            
        while True:
            # Esperamos a que nos llegue el mensaje.
            d, sender = yield self.canal_entrada.get()

            if d + 1 < self.distancia:
                self.distancia = d + 1
                self.padre = sender
                data = (self.distancia, self.id_nodo)
                yield env.timeout(TICK)
                self.canal_salida.envia(data, self.vecinos)


if __name__ == "__main__":
    # Creamos el ambiente y el objeto Canal.
    env = simpy.Environment()
    bc_pipe = CanalRecorridos(env)

    # Adyacencias.
    adyacencias = [{1, 3, 4, 6}, {0, 3, 5, 7}, {3, 5, 6},
                   {0, 1, 2}, {0}, {1, 2}, {0, 2}, {1}]

    # La lista que representa la gráfica.
    grafica = []

    # Creamos los nodos
    for i in range(0, len(adyacencias)):
        grafica.append(NodoBFS(i, adyacencias[i],
                               bc_pipe.crea_canal_de_entrada(), bc_pipe))

    # Le decimos al ambiente lo que va a procesar.
    for nodo in grafica:
        env.process(nodo.bfs(env))
    
    # Y lo corremos.
    env.run(until=50)

    # Probamos que efectivamente se hizo un BFS.
    padres_esperados = [0, 0, 3, 0, 0, 1, 0, 1]
    distancias_esperadas = [0, 1, 2, 1, 1, 2, 1, 2]

    # Para cada nodo verificamos que su lista de identifiers sea la esperada.
    for i in range(len(grafica)):
        n = grafica[i]
        assert n.padre == padres_esperados[i], ('El nodo %d tiene mal padre' % n.id_nodo)
        assert n.distancia == distancias_esperadas[i], ('El nodo %d tiene distancia equivocada' % n.id_nodo)
