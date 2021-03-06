"""
======================================================================
>> Autores: Johann Gordillo [jgordillo@ciencias.unam.mx]
            Alex Fernández  [alexg.fernandeza@ciencias.unam.mx]

>> Fecha:   01/12/2020
======================================================================
Universidad Nacional Autónoma de México
Facultad de Ciencias

Computación Distribuida [2021-1]

Ejercicio 2.
Algoritmo DFS asíncrono con relojes vectoriales.
======================================================================
"""

import simpy
from random import randint

from Nodo import Nodo
from Canales.CanalRecorridos import CanalRecorridos


class NodoDFS(Nodo):
    """Implementa la interfaz de Nodo para el algoritmo de Broadcast
    asíncrono. Usa el reloj de Lamport para asignar a cada evento
    una timestamp que respeta el orden causal."""
    def __init__(self, id_nodo: int, vecinos: set,
                 canal_entrada: simpy.Store,
                 canal_salida: simpy.Store,
                 order: int):
        """Constructor para el nodo."""
        self.id_nodo = id_nodo
        self.vecinos = vecinos
        self.canal_entrada = canal_entrada
        self.canal_salida = canal_salida
        self.padre = id_nodo
        self.order = order  # Orden de la gráfica.
        self.eventos = list()  # Lista de eventos
        self.reloj = [0] * self.order  # Reloj vectorial

    def dfs(self, env):
        """Implementación del algoritmo DFS."""
        # Nodo distinguido (id = 0).
        if self.id_nodo == 0:
            yield env.timeout(randint(0, 10))

            # El nodo distinguido es su propio padre.
            self.padre = self.id_nodo

            # La estructura es (msg_type, sender, visited).
            data = ("GO", self.id_nodo, {self.id_nodo})

            # Enviamos el mensaje a un vecino k.
            # Por convención, tomamos el vecino con menor id.
            k = min(self.vecinos)
            self.hijos = {k}

            # Actualizamos nuestra entrada en el reloj.
            self.reloj[self.id_nodo] += 1

            # Agregamos los eventos de envío.
            self.canal_salida.envia([data, self.id_nodo, self.reloj], [k])
            self.eventos.append([self.reloj, 'E', 'GO', self.id_nodo, k])

        while True:
            yield env.timeout(randint(0, 10))

            # Esperamos a que nos llegue el mensaje.
            data, emisor, reloj_emisor = yield self.canal_entrada.get()
            msg_type, _, visited = data
            
            # Actualizamos el reloj vectorial.
            self.actualiza_reloj(reloj_emisor)

            # Agregamos el evento de recepción.
            self.eventos.append([self.reloj, 'R', msg_type, emisor, self.id_nodo])
            
            # Cuando recibimos un mensaje GO(visited).
            if msg_type == "GO":
                # Su padre será el nodo del que recibió el mensaje.
                yield env.timeout(randint(0, 10))

                self.padre = emisor
                self.reloj[self.id_nodo] += 1
                
                if self.vecinos.issubset(visited):
                    yield env.timeout(randint(0, 10))
                    data = ("BACK", self.id_nodo, visited.union({self.id_nodo}))
                    self.hijos = set()

                    # Agregamos los eventos de envío.
                    self.canal_salida.envia([data, self.id_nodo, self.reloj], [emisor])
                    self.eventos.append([self.reloj, 'E', 'BACK', self.id_nodo, emisor])

                else:
                    yield env.timeout(randint(0, 10))
                    k = min(self.vecinos.difference(visited))
                    data = ("GO", self.id_nodo, visited.union({self.id_nodo}))
                    self.hijos = {k}

                    # Agregamos los eventos de envío.
                    self.canal_salida.envia([data, self.id_nodo, self.reloj], [k])
                    self.eventos.append([self.reloj, 'E', 'GO', self.id_nodo, k])

            # Cuando recibimos un mensaje BACK(visited).
            elif msg_type == "BACK":
                self.reloj[self.id_nodo] += 1

                if self.vecinos.issubset(visited):
                    # Terminación global.
                    if self.padre == self.id_nodo:
                        print("Ha terminado la ejecución del algoritmo.")
                        return

                    # Terminación local.
                    else:
                        yield env.timeout(randint(0, 10))
                        data = ("BACK", self.id_nodo, visited)

                        self.canal_salida.envia([data, self.id_nodo, self.reloj], [self.padre])
                        self.eventos.append([self.reloj, 'E', 'BACK', self.id_nodo, self.padre])

                else:
                    yield env.timeout(randint(0, 10))
                    k = min(self.vecinos.difference(visited))
                    data = ("GO", self.id_nodo, visited)
                    self.hijos = self.hijos.union({k})

                    # Agregamos los eventos de envío.
                    self.canal_salida.envia([data, self.id_nodo, self.reloj], [k])
                    self.eventos.append([self.reloj, 'E', 'GO', self.id_nodo, k])

            # Si el tipo de mensaje no existe, lanzamos excepción.
            else:
                raise Exception("El tipo de mensaje no existe.")

    def agrega_eventos(self, tipo, mensaje, emisor, receptores, env):
        """Función auxiliar para agregar los eventos a la lista correspondiente."""
        for receptor in receptores:
            if tipo == 'E':
                msg = [mensaje, self.id_nodo, self.reloj]
                self.canal_salida.envia(msg, [receptor])
            msg_type, _, _ = mensaje
            self.eventos.append([self.reloj, tipo, msg_type, emisor, receptor])

    def actualiza_reloj(self, reloj_emisor):
        """Función auxiliar para actualizar el reloj vectorial."""
        for i in range(self.order):
            if i == self.id_nodo:
                self.reloj[i] += 1
            else:
                self.reloj[i] = max(reloj_emisor[i], self.reloj[i])


if __name__ == "__main__":
    # Creamos el ambiente y el objeto Canal.
    env = simpy.Environment()
    bc_pipe = CanalRecorridos(env)

    # Adyacencias.
    adyacencias = [{1, 3, 4, 6}, {0, 3, 5, 7}, {3, 5, 6}, {0, 1, 2}, {0}, {1, 2}, {0, 2}, {1}]

    # La lista que representa la gráfica.
    grafica = []

    order = len(adyacencias)

    # Creamos los nodos.
    for i in range(len(adyacencias)):
        grafica.append(NodoDFS(i, adyacencias[i],
                               bc_pipe.crea_canal_de_entrada(),
                               bc_pipe, order))

    # Le decimos al ambiente lo que va a procesar.
    for nodo in grafica:
        env.process(nodo.dfs(env))
    
    # Lo corremos.
    env.run()

    # Probamos que efectivamente se hizo un BFS.
    
    padres_esperados = [0, 0, 3, 1, 0, 2, 2, 1]
    hijos_esperados = [{1, 4}, {3, 7}, {5, 6}, {2}, set(), set(), set(), set()]

    # Para cada nodo verificamos que su lista de identifiers sea la esperada.
    for i in range(len(grafica)):
        n = grafica[i]
        print(f'El nodo {n.id_nodo} tiene eventos: {n.eventos}\n')
        assert n.padre == padres_esperados[i], ('El nodo %d tiene mal padre' % n.id_nodo)
        assert n.hijos == hijos_esperados[i], ('El nodo %d tiene distancia equivocada' % n.id_nodo)

    #n = grafica[0]
    #for e in n.eventos:
    #    print(e)