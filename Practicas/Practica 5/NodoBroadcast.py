"""
======================================================================
>> Autores: Johann Gordillo [jgordillo@ciencias.unam.mx]
            Alex Fernández  [alexg.fernandeza@ciencias.unam.mx]

>> Fecha:   01/12/2020
======================================================================
Universidad Nacional Autónoma de México
Facultad de Ciencias

Computación Distribuida [2021-1]

Ejercicio 1.
Broadcast Asíncrono con relojes lógicos de Lamport.
======================================================================
"""

import simpy
from random import randint

from Nodo import Nodo
from Canales.CanalRecorridos import CanalRecorridos


class NodoBroadcast(Nodo):
    """Implementa la interfaz de Nodo para el algoritmo para conocer a
    los vecinos de mis vecinos."""
    def __init__(self, id_nodo: int, vecinos: list,
                 canal_entrada: simpy.Store,
                 canal_salida: simpy.Store):
        """Constructor para el nodo."""
        self.id_nodo = id_nodo
        self.vecinos = vecinos
        self.canal_entrada = canal_entrada
        self.canal_salida = canal_salida
        self.reloj = 0  # Reloj de Lamport.
        self.eventos = list()  # Lista de eventos

    def broadcast(self, env: simpy.Environment):
        """Función para que un nodo colabore en la construcción
        de un árbol generador."""
        # Solo el nodo raiz (id = 0) envía el primer mensaje.
        if self.id_nodo == 0:
            yield env.timeout(randint(0, 10))
            # Mensaje que se quiere difundir.
            self.mensaje = "Hello, Graph"
            self.agrega_eventos('E', self.mensaje, self.id_nodo, self.vecinos, env)

        # Para los nodos no distinguidos data será nula.
        else:
            self.mensaje = None

        while True:
            yield env.timeout(randint(0, 10))
            # Esperamos a que nos llegue el mensaje.
            self.mensaje, emisor, reloj_emisor = yield self.canal_entrada.get()

            # Actualizamos el reloj.
            self.reloj = max(reloj_emisor, self.reloj) + 1

            # Agregamos el evento de recepción.
            self.agrega_eventos('R', self.mensaje, emisor, [self.id_nodo], env)
            
            # Reenvíamos el mensaje a nuestros hijos.
            if len(self.vecinos) > 0:
                yield env.timeout(randint(0, 10))
                self.agrega_eventos('E', self.mensaje, self.id_nodo, self.vecinos, env)

    def agrega_eventos(self, tipo, mensaje, emisor, receptores, env):
        """Función auxiliar para agregar los eventos a la lista correspondiente."""
        for receptor in receptores:
            if tipo == 'E':
                self.reloj += 1
                msg = [self.mensaje, self.id_nodo, self.reloj]
                self.canal_salida.envia(msg, [receptor])
            self.eventos.append([self.reloj, tipo, mensaje, emisor, receptor])


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
    adjacencies = [[1, 2], [], [3], [4, 5, 6], [], [], []]
    
    # Orden de la gráfica.
    order = len(adjacencies)

    # Inicializamos el ambiente y el canal.
    env = simpy.Environment()
    pipe = CanalRecorridos(env)

    # Llenado de la gráfica.
    for i in range(order):
        input_channel = pipe.crea_canal_de_entrada()
        n = NodoBroadcast(i, adjacencies[i], input_channel, pipe)
        graph.append(n)

    # Y le decimos al ambiente que lo procese.
    for n in graph:
        env.process(n.broadcast(env))

    # Imprimimos la gráfica de ejemplo.
    print(example)

    env.run()

    print("\nAl finalizar el algoritmo:")
    for n in graph:
        print(f"La información del proceso {n.id_nodo} es {n.mensaje}")
