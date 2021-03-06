"""
======================================================================
>> Autor: Johann Gordillo
>> Email: jgordillo@ciencias.unam.mx
>> Fecha: 21/10/2020
======================================================================
Universidad Nacional Autónoma de México
Facultad de Ciencias

Computación Distribuida [2021-1]

Ejercicio 1.
Algoritmo para conocer a los vecinos de mis vecinos.
======================================================================
"""

import simpy
from Nodo import Nodo
from Canales.Canal import Canal


class NodoReconocimiento(Nodo):
    """Implementa la interfaz de Nodo para el algoritmo para conocer a
    los vecinos de mis vecinos."""
    def __init__(self, id: int, neighbors: list, 
                 input_channel: simpy.Store,
                 output_channel: simpy.Store):
        """Constructor para el nodo."""
        self.id = id
        self.neighbors = neighbors
        self.input_channel = input_channel
        self.output_channel = output_channel
        self.identifiers = set()

    def meet(self, env: simpy.Environment):
        """Función para que un nodo conozca a los vecinos de
        sus vecinos."""
        # Enviamos a nuestros vecinos nuestro conjunto de vecinos.
        # Supongamos que los mensajes se mandan en la ronda 0 y se reciben
        # en la ronda 1.
        yield env.timeout(1)
        self.output_channel.send(self.neighbors, self.neighbors)

        while True:
            # Esperamos a que nos llegue el mensaje.
            identifiers = yield self.input_channel.get()
            print(f'El proceso {self.id} recibió el conjunto {identifiers} en la ronda {env.now}')

            # Unimos nuestro conjunto identifiers con el que recibimos.
            self.identifiers = self.identifiers.union(identifiers)


if __name__ == "__main__":
    # Tomemos como ejemplo la siguiente gráfica:
    example = '''Para la siguiente gráfica:
                            (6)
           (1)             / |
          /   \           /  |
         /     \         /   |
       (0)-----(2)-----(3)--(4)
                         \   |       
                          \  | 
                           \ | 
                            (5)
    '''

    # Creamos los nodos.
    graph = list()
    adjacencies = [[1, 2], [0, 2], [0, 1, 3], [2, 4, 5, 6],
                   [3, 5, 6], [3, 4], [3, 4]]
    order = len(adjacencies)

    # Inicializamos el ambiente y el canal.
    env = simpy.Environment()
    pipe = Canal(env)

    # Llenado de la gráfica.
    for i in range(order):
        input_channel = pipe.create_input_channel()
        neighbors = adjacencies[i]
        n = NodoReconocimiento(i, neighbors, input_channel, pipe)
        graph.append(n)

    # Y le decimos al ambiente que lo procese.
    for n in graph:
        env.process(n.meet(env))

    # Imprimimos la gráfica de ejemplo.
    print(example)

    env.run(until=10)
    
    print("\nAl finalizar el algoritmo:")
    for n in graph:
        print(f"El nodo {n.id} conoce a los nodos: {n.identifiers}")
