"""
======================================================================
>> Autor: Johann Gordillo
>> Email: jgordillo@ciencias.unam.mx
>> Fecha: 08/11/2020
======================================================================
Universidad Nacional Autónoma de México
Facultad de Ciencias

Computación Distribuida [2021-1]

Práctica #03

Ejercicio 1
Algoritmo de Consenso (sin Early-Stopping).
======================================================================
"""

import simpy
import random

from Nodo import Nodo
from Canales.CanalRecorridos import CanalRecorridos


# La unidad de tiempo.
TICK = 1

class NodoConsenso(Nodo):
    """Implementa la interfaz de Nodo para el algoritmo de Consenso."""
    def __init__(self, id_nodo: int, vecinos: list,
                 canal_entrada: simpy.Store,
                 canal_salida: simpy.Store):
        """Constructor de nodo que implemente el algoritmo de consenso.

        Args:
            id_nodo (int): El Identificador del nodo.
            vecinos (List[int]): Lista de vecinos.
            canal_entrada (simpy.Store): Canal de entrada.
            canal_salida (simpy.Store): Canal de salida.
        """
        self.id_nodo = id_nodo
        self.vecinos = vecinos
        self.canal_entrada = canal_entrada
        self.canal_salida = canal_salida
        # Atributos extra
        self.V = [None] * (len(vecinos) + 1)  # Llenamos la lista de Nones
        self.V[id_nodo] = id_nodo
        self.New = set([id_nodo])
        self.rec_from = [None] * (len(vecinos) + 1)
        self.fallare = False  # Colocaremos esta en True si el nodo fallará
        self.lider = None  # La elección del lider.

    def consenso(self, env: simpy.Store, f: int) -> None:
        """Implementación del algoritmo de consenso.
        
        Args:
            env (simpy.Store): El ambiente.
            f (int): Número de fallos.
        """
        # Por convención, fallan los primeros f nodos.
        if self.id_nodo < f:
            self.fallare = True
            # Un entero pseudo-aleatorio m tal que 0 <= m <= f.
            ronda_a_fallar = random.randint(0, f)

        # Ejecutamos f + 1 rondas.
        while env.now < f + 1:
            # En caso de que el algoritmo vaya a fallar.
            if self.fallare:
                if env.now == ronda_a_fallar:
                    return

            # Envío de los mensajes.
            yield env.timeout(TICK)
            if len(self.New) != 0:
                data = (self.New, self.id_nodo)
                self.canal_salida.envia(data, self.vecinos)

            # Recepción de los mensajes.
            expected_msgs = len(self.canal_entrada.items)
            for _ in range(expected_msgs):
                msg, sender = yield self.canal_entrada.get()
                self.rec_from[sender] = msg

            self.New = set()

            for j in self.vecinos:
                new = self.rec_from[j]
                if new is not None:
                    for k in new:
                        if self.V[k] is None:
                            self.V[k] = k
                            self.New = self.New.union({k})

        # Buscamos el primer elemento no nulo de V.
        for v in self.V:
            if v is not None:
                # Lo hacemos su lider.
                self.lider = v
                return


if __name__ == "__main__":
    # Ejecutaremos el algoritmo sobre una gráfica completa de 6 nodos.
    example='''Consideremos la siguiente gráfica completa de seis nodos:\n
                           @@@@@@@@.                             #@@@@@@@(                          
                           @@@@@@@@@                             @@@@@@@@@                          
                           ,@@@@@@@  @@                        @  @@@@@@@                           
                         %#        ,      &@.             @@      ,       @                         
                       &(      @    @          %@/   @@          @   @      @*                      
                     &(        @     @         .@@  (@(        &.    @        @#                    
                   &/          @       @  *@#            *@%  @      @          /@                  
                 &/            @     #@/@                   @*,@&    @             @                
               @*              @@@.      *@                @        @@               @              
             @*            @@. @           @             &.          @   @@.           @            
           @*         @@       @            %(          @            @        %@*        @.         
         @,      @@            @              @       @,             @             #@(     @(       
  @@@@@@   *@%                 @               &.    @               @                  /@  &@@@@@@ 
&@@@@@@@@*                     @                 @ &.                @                     @@@@@@@@@
.@@@@@@@@                      @                  @                  @                     @@@@@@@@@
  ,@@@@.    &@.                @                @, .@                @                  @@   @@@@@  
         *@      @@            @               @     @               @             @@     *@        
           #%         @@       @             &.       *%             @        @@         @          
             @.           ,@%  @            @           @            @   #@*           @            
               @               &@(        @,             #/         /@(              @              
                 @             @    %@,  @                 @   ,@%   @             @                
                   @           @       &.&@.              .@@,       @           @                  
                    .@         @      @       @@      @@      @      @         @                    
                      (%       @    @,           @@@@          @     @       @                      
                        @*     @   @        @@         ,@%       @   @     @                        
                          @            %@,                  /@(                                     
                           %@@@@@@@ *                            ,@@@@@@@                           
                           @@@@@@@@@ @@@@@@@@@@@@@@@@@@@@@@@@@@@ @@@@@@@@@                          
                           %@@@@@@@                              *@@@@@@@, 
    '''

    # Creamos el ambiente y el objeto Canal.
    env = simpy.Environment()
    bc_pipe = CanalRecorridos(env)

    # Adyacencias.
    adyacencias = [[1, 2, 3, 4, 5], [0, 2, 3, 4, 5],
                   [0, 1, 3, 4, 5], [0, 1, 2, 4, 5],
                   [0, 1, 2, 3, 5], [0, 1, 2, 3, 4]]

    # La lista que representa la gráfica.
    grafica = []

    # Creamos los nodos.
    for i in range(len(adyacencias)):
        grafica.append(NodoConsenso(i, adyacencias[i],
                               bc_pipe.crea_canal_de_entrada(),
                               bc_pipe))
    
    # Número de fallos.
    f = 2

    # Le decimos al ambiente lo que va a procesar.
    for nodo in grafica:
        env.process(nodo.consenso(env, f))
    
    # Y lo corremos.
    env.run()

    print(example)
    print(f"\nEjecutando el algoritmo con f = {f}, obtenemos:")
    for nodo in grafica:
        if nodo.fallare:
            print(f"El proceso {nodo.id_nodo} falló.")
        else:
            print(f"El proceso {nodo.id_nodo} tiene lider {nodo.lider}.")
