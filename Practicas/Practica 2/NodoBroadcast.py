"""
======================================================================
>> Autor: Johann Gordillo
>> Email: jgordillo@ciencias.unam.mx
>> Fecha: 21/10/2020
======================================================================
Universidad Nacional Autónoma de México
Facultad de Ciencias

Computación Distribuida [2021-1]

Ejercicio 3.
Algoritmo Distribuido para hacer Broadcast.
======================================================================
"""

import simpy
from Canales.Canal import Canal
from Nodo import Nodo


class NodoBroadcast(Nodo):
    """Implementa la interfaz de Nodo para el algoritmo para conocer a
    los vecinos de mis vecinos."""
    def __init__(self, id: int, neighbors: list,
                 input_channel: simpy.Store,
                 output_channel: simpy.Store,
                 children: list):
        """Constructor para el nodo."""
        self.id = id
        self.neighbors = neighbors
        self.input_channel = input_channel
        self.output_channel = output_channel
        self.children = children

    def broadcast(self, env: simpy.Environment):
        """Función para que un nodo colabore en la construcción
        de un árbol generador."""
        # Solo el nodo raiz (id = 0) envía el primer msj
        if self.id == 0:
            # Mensaje que se quiere difundir.
            self.data = "Hello, World"
            print(f'El proceso {self.id} inicializa su mensaje {self.data} en la ronda {env.now}')
            yield env.timeout(1)
            self.output_channel.send(self.data, self.children)

        # Para los nodos no distinguidos data será nula.
        else:
            self.data = None

        while True:
            # Esperamos a que nos llegue el mensaje.
            self.data = yield self.input_channel.get()

            print(f'El proceso {self.id} recibió el mensaje {self.data} en la ronda {env.now}')
            
            # Reenvíamos el mensaje a nuestros hijos.
            if len(self.children) > 0:
                yield env.timeout(1)
                self.output_channel.send(self.data, self.children)


if __name__ == "__main__":
    # Tomemos como ejemplo la siguiente gráfica:
    example = '''Para el siguiente árbol:
                            (6)
           (1)             / 
          /               /  
         /               /   
       (0)-----(2)-----(3)--(4)
                         \          
                          \   
                           \  
                            (5)
    '''

    # Creamos los nodos.
    graph = list()

    # Lista de adyacencias.
    adjacencies = [[1, 2], [0], [0, 3], [2, 4, 5, 6],
                   [3], [3], [3]]
    
    # Hijos de cada nodo.
    children = [[1, 2], [], [3], [4, 5, 6], [], [], []]
    
    # Orden de la gráfica.
    order = len(adjacencies)

    # Inicializamos el ambiente y el canal.
    env = simpy.Environment()
    pipe = Canal(env)

    # Llenado de la gráfica.
    for i in range(order):
        input_channel = pipe.create_input_channel()
        n = NodoBroadcast(i, adjacencies[i], input_channel, pipe, children[i])
        graph.append(n)

    # Y le decimos al ambiente que lo procese.
    for n in graph:
        env.process(n.broadcast(env))

    # Imprimimos la gráfica de ejemplo.
    print(example)

    env.run(until=10)

    print("\nAl finalizar el algoritmo:")
    for n in graph:
        print(f"La información del proceso {n.id} es {n.data}")
