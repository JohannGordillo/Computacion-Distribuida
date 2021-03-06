"""
======================================================================
>> Autor: Johann Gordillo
>> Email: jgordillo@ciencias.unam.mx
>> Fecha: 21/10/2020
======================================================================
Universidad Nacional Autónoma de México
Facultad de Ciencias

Computación Distribuida [2021-1]

Ejercicio 4 (Extra).
Algoritmo Distribuido para hacer Convergecast.
======================================================================
"""

import simpy
from Canales.Canal import Canal
from Nodo import Nodo
from random import randint


class NodoConvergecast(Nodo):
    """Implementa la interfaz de Nodo para el algoritmo de Convergecast."""
    def __init__(self, id: int, neighbors: list,
                 input_channel: simpy.Store,
                 output_channel: simpy.Store,
                 children: list, parent, elem):
        """Constructor para el nodo."""
        self.id = id
        self.neighbors = neighbors
        self.input_channel = input_channel
        self.output_channel = output_channel
        self.children = children
        self.parent = parent
        # Atributo Extra.
        self.elem = elem
        self.val_set = set()

    def convergecast(self, env: simpy.Environment, func):
        """Función para que un nodo haga convergecast."""
        # Las hojas comienzan la ejecución.
        if len(self.children) == 0:
            # Mensaje que se quiere difundir.
            data = (self.id, self.elem)
            print(f'El proceso {self.id} envía el mensaje {data} a {self.parent} en la ronda {env.now}')
            yield env.timeout(1)
            self.output_channel.send(data, [self.parent])

        self.expected_msg = len(self.children)

        while True:
            # Esperamos a que nos llegue el mensaje.
            data = yield self.input_channel.get()
            print(f'El proceso {self.id} recibió el mensaje {data} en la ronda {env.now}')
            
            if isinstance(data, set):
                self.val_set = self.val_set.union(data)
            else:
                self.val_set.add(data)
            
            self.expected_msg -= 1
            if self.expected_msg == 0:
                if self.parent == self.id:
                    print(f"\nFinalmente, el nodo {self.id} calcula la función y obtiene: {f(self.val_set)}")
                else:
                    yield env.timeout(1)
                    print(f'El proceso {self.id} envía el mensaje {data} a {self.parent} en la ronda {env.now}')
                    self.output_channel.send(self.val_set, [self.parent])


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

    # Padre de cada nodo.
    parents = [0, 0, 0, 2, 3, 3, 3]
    
    # Orden de la gráfica.
    order = len(adjacencies)

    # Inicializamos el ambiente y el canal.
    env = simpy.Environment()
    pipe = Canal(env)

    # Llenado de la gráfica.
    for i in range(order):
        input_channel = pipe.create_input_channel()
        val = randint(100, 500)
        n = NodoConvergecast(i, adjacencies[i], input_channel, pipe,
                             children[i], parents[i], val)
        graph.append(n)

    # Función que queremos que calcule el proceso distinguido.
    f = (lambda vals: sum([v for (i, v) in vals]))

    # Y le decimos al ambiente que lo procese.
    for n in graph:
        env.process(n.convergecast(env, f))

    # Imprimimos la gráfica de ejemplo.
    print(example)

    env.run(until=30)
