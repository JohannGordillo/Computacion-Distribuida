"""
======================================================================
>> Autor: Johann Gordillo
>> Email: jgordillo@ciencias.unam.mx
>> Fecha: 03/11/2020
======================================================================
Universidad Nacional Autónoma de México
Facultad de Ciencias

Computación Distribuida [2021-1]

Pruebas para la práctica.
======================================================================
"""

import simpy

from Canales.CanalRecorridos import CanalRecorridos
from NodoBFS import NodoBFS
from NodoDFS import NodoDFS


# Las unidades de tiempo que les daremos a las pruebas.
TIEMPO_DE_EJECUCION = 50

class TestPractica1:
    """Clase para las pruebas unitarias de la práctica 1."""
    # Las aristas de adyacencias de la gráfica.
    adyacencias = [{1, 3, 4, 6}, {0, 3, 5, 7}, {3, 5, 6},
                   {0, 1, 2}, {0}, {1, 2}, {0, 2}, {1}]

    def test_ejercicio_uno(self):
        """Método que prueba el algoritmo de BFS."""
        # Creamos el ambiente y el objeto Canal.
        env = simpy.Environment()
        bc_pipe = CanalRecorridos(env)

        # La lista que representa la gráfica.
        grafica = []

        # Creamos los nodos.
        for i in range(len(self.adyacencias)):
            vecinos = self.adyacencias[i]
            canal_entrada = bc_pipe.crea_canal_de_entrada()
            canal_salida = bc_pipe
            nodo = NodoBFS(i, vecinos, canal_entrada, canal_salida)
            grafica.append(nodo)

        # Le decimos al ambiente lo que va a procesar.
        for nodo in grafica:
            env.process(nodo.bfs(env))
        
        # Y lo corremos.
        env.run(until=TIEMPO_DE_EJECUCION)

        # Probamos que efectivamente se hizo un BFS.
        padres_esperados = [0, 0, 3, 0, 0, 1, 0, 1]
        distancias_esperadas = [0, 1, 2, 1, 1, 2, 1, 2]

        # Para cada nodo verificamos que su lista de identifiers sea la esperada.
        for i in range(0, len(grafica)):
            nodo = grafica[i]
            assert nodo.padre == padres_esperados[i], (f"El nodo {nodo.id_nodo} tiene mal padre")
            assert nodo.distancia == distancias_esperadas[i], (f"El nodo {nodo.id_nodo} tiene distancia equivocada")


    def test_ejercicio_dos(self):
        """Prueba para el algoritmo DFS."""
        # Creamos el ambiente y el objeto Canal.
        env = simpy.Environment()
        bc_pipe = CanalRecorridos(env)

        # La lista que representa la gráfica.
        grafica = []

        # Creamos los nodos
        for i in range(0, len(self.adyacencias)):
            grafica.append(NodoDFS(i, self.adyacencias[i],
                                   bc_pipe.crea_canal_de_entrada(), bc_pipe))

        # Le decimos al ambiente lo que va a procesar.
        for nodo in grafica:
            env.process(nodo.dfs(env))
        
        # Y lo corremos.
        env.run(until=TIEMPO_DE_EJECUCION)

        # Probamos que efectivamente se hizo un BFS.
        padres_esperados = [0, 0, 3, 1, 0, 2, 2, 1]
        hijos_esperados = [{1, 4}, {3, 7}, {5, 6}, {2}, set(), set(), set(), set()]

        # Para cada nodo verificamos que su lista de identifiers sea la esperada.
        for i in range(0, len(grafica)):
            nodo = grafica[i]
            assert nodo.padre == padres_esperados[i], ("El nodo {nodo.id_nodo} tiene mal padre")
            assert nodo.hijos == hijos_esperados[i], ("El nodo {nodo.id_nodo} tiene distancia equivocada")
