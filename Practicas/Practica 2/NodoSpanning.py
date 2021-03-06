"""
======================================================================
>> Autor: Johann Gordillo
>> Email: jgordillo@ciencias.unam.mx
>> Fecha: 21/10/2020
======================================================================
Universidad Nacional Autónoma de México
Facultad de Ciencias

Computación Distribuida [2021-1]

Ejercicio 2.
Algoritmo Distribuido para construir un árbol generador.
======================================================================
"""

import simpy
from Canales.Canal import Canal
from Nodo import Nodo


class NodoSpanning(Nodo):
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

    def span(self, env: simpy.Environment):
        """Función para que un nodo colabore en la construcción
        de un árbol generador."""
        # Solo el nodo raiz (id = 0) envía el primer msj
        if self.id == 0:
            self.parent = self.id
            self.expected_msg = len(self.neighbors)

            data = ("GO", self.id, None)
            print(f'El nodo {self.id} inicializa sus variables en la ronda {env.now}')

            yield env.timeout(1)
            self.output_channel.send(data, self.neighbors)

        # Los nodos no distinguidos tendrán padre vacío al inicio.
        else:
            self.parent = None

        # Hacemos que el conjunto de hijos sea vacío para todos.
        self.children = set()

        while True:
            # Esperamos a que nos llegue el mensaje.
            msg_type, sender, val_set = yield self.input_channel.get()
            print(f'El nodo {self.id} recibió el mensaje {msg_type}({val_set}) de {sender} en la ronda {env.now}')
            yield env.timeout(1)

            # Cuando recibimos un mensaje GO().
            if msg_type == "GO":
                if self.parent is None:
                    self.parent = sender
                    self.expected_msg = len(self.neighbors) - 1

                    if self.expected_msg == 0:
                        data = ("BACK", self.id, self.id)
                        self.output_channel.send(data, [sender])

                    else:
                        data = ("GO", self.id, None)
                        receivers = [k for k in self.neighbors if k != sender]
                        self.output_channel.send(data, receivers)

                else:
                    data = ("BACK", self.id, None)
                    self.output_channel.send(data, [sender])

            # Cuando recibimos un mensaje BACK(val_set).            
            elif msg_type == "BACK":
                self.expected_msg -= 1

                if val_set is not None:
                    self.children.add(sender)
                
                if self.expected_msg == 0:
                    if self.parent != self.id:
                        data = ("BACK", self.id, self.id)
                        self.output_channel.send(data, [self.parent])

            # Si el tipo de mensaje no existe, lanzamos excepción.
            else:
                raise Exception("El tipo de mensaje no existe.")


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
        n = NodoSpanning(i, neighbors, input_channel, pipe)
        graph.append(n)
    
    # Y le decimos al ambiente que lo procese.
    for n in graph:
        env.process(n.span(env))

    # Imprimimos la gráfica de ejemplo.
    print(example)

    env.run(until=30)
    
    # Inicializamos el árbol resultante.
    tree = list()

    # Llenado del árbol generador.
    for n in graph:
        # Llenado del árbol generador.
        if len(n.children) > 0:
            for c in n.children:
                tree.append([n.id, c])

    print(f"\nFinalmente, las aristas del árbol generador son:\n{tree}\n")

    result = '''Visualmente, se ve como sigue:
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

    print(result)
