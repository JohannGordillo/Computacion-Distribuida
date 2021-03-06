"""
======================================================================
>> Autor: Johann Gordillo
>> Email: jgordillo@ciencias.unam.mx
>> Fecha: 03/11/2020
======================================================================
Universidad Nacional Autónoma de México
Facultad de Ciencias

Computación Distribuida [2021-1]

Ejercicio 1.
Algoritmo DFS óptimo en tiempo y mensajes.
======================================================================
"""

import simpy

from Nodo import Nodo
from Canales.CanalRecorridos import CanalRecorridos


# La unidad de tiempo.
TICK = 1

class NodoDFS(Nodo):
    """Implementa la interfaz de Nodo para el algoritmo DFS."""
    def __init__(self, id_nodo: int, vecinos: set,
                 canal_entrada: simpy.Store,
                 canal_salida: simpy.Store):
        """Constructor para el nodo."""
        self.id_nodo = id_nodo
        self.vecinos = vecinos
        self.canal_entrada = canal_entrada
        self.canal_salida = canal_salida
        self.padre = id_nodo

    def dfs(self, env):
        """Implementación del algoritmo DFS."""
        # Nodo distinguido (id = 0).
        if self.id_nodo == 0:
            # El nodo distinguido es su propio padre.
            self.padre = self.id_nodo

            # La estructura es (msg_type, sender, visited).
            data = ("GO", self.id_nodo, {self.id_nodo})

            # Enviamos el mensaje a un vecino k.
            # Por convención, tomamos el vecino con menor id.
            k = min(self.vecinos)
            self.hijos = {k}
            yield env.timeout(TICK)
            self.canal_salida.envia(data, [k])

        while True:
            # Esperamos a que nos llegue el mensaje.
            msg_type, sender, visited = yield self.canal_entrada.get()
            print(f'El nodo {self.id_nodo} recibió el mensaje {msg_type}({visited}) de {sender} en la ronda {env.now}')

            # Cuando recibimos un mensaje GO(visited).
            if msg_type == "GO":
                # Su padre será el nodo del que recibió el mensaje.
                self.padre = sender

                if self.vecinos.issubset(visited):
                    data = ("BACK", self.id_nodo, visited.union({self.id_nodo}))
                    self.hijos = set()
                    yield env.timeout(TICK)
                    self.canal_salida.envia(data, [sender])
 
                else:
                    k = min(self.vecinos.difference(visited))
                    data = ("GO", self.id_nodo, visited.union({self.id_nodo}))
                    self.hijos = {k}
                    yield env.timeout(TICK)
                    self.canal_salida.envia(data, [k])

            # Cuando recibimos un mensaje BACK(visited).
            elif msg_type == "BACK":
                if self.vecinos.issubset(visited):
                    # Terminación global.
                    if self.padre == self.id_nodo:
                        print("Ha terminado la ejecución del algoritmo.")
                        return
                    # Terminación local.
                    else:
                        data = ("BACK", self.id_nodo, visited)
                        yield env.timeout(TICK)
                        self.canal_salida.envia(data, [self.padre])

                else:
                    k = min(self.vecinos.difference(visited))
                    data = ("GO", self.id_nodo, visited)
                    self.hijos = self.hijos.union({k})
                    yield env.timeout(TICK)
                    self.canal_salida.envia(data, [k])

            # Si el tipo de mensaje no existe, lanzamos excepción.
            else:
                raise Exception("El tipo de mensaje no existe.")


if __name__ == "__main__":
    # Creamos el ambiente y el objeto Canal.
    env = simpy.Environment()
    bc_pipe = CanalRecorridos(env)

    # Adyacencias.
    adyacencias = [{1, 3, 4, 6}, {0, 3, 5, 7}, {3, 5, 6},
                   {0, 1, 2}, {0}, {1, 2}, {0, 2}, {1}]

    # La lista que representa la gráfica.
    grafica = []

    # Creamos los nodos.
    for i in range(len(adyacencias)):
        grafica.append(NodoDFS(i, adyacencias[i],
                               bc_pipe.crea_canal_de_entrada(),
                               bc_pipe))

    # Le decimos al ambiente lo que va a procesar.
    for nodo in grafica:
        env.process(nodo.dfs(env))
    
    # Lo corremos.
    env.run(until=50)

    # Probamos que efectivamente se hizo un BFS.
    
    padres_esperados = [0, 0, 3, 1, 0, 2, 2, 1]
    hijos_esperados = [{1, 4}, {3, 7}, {5, 6}, {2}, set(), set(), set(), set()]

    # Para cada nodo verificamos que su lista de identifiers sea la esperada.
    for i in range(len(grafica)):
        n = grafica[i]
        assert n.padre == padres_esperados[i], ('El nodo %d tiene mal padre' % n.id_nodo)
        assert n.hijos == hijos_esperados[i], ('El nodo %d tiene distancia equivocada' % n.id_nodo)

