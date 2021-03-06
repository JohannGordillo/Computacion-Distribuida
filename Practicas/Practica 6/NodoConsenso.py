"""
======================================================================
>> Autor: Johann Gordillo
>> Email: jgordillo@ciencias.unam.mx
>> Fecha: 26/01/2021
======================================================================
Universidad Nacional Autónoma de México
Facultad de Ciencias

Computación Distribuida [2021-1]

Práctica #05

Algoritmo de Consenso (sin Early-Stopping) utlizando detectores
de fallos.
======================================================================
"""

import simpy
import random

from Nodo import Nodo
from Canales.CanalRecorridos import CanalRecorridos


# La unidad de tiempo.
TICK = 1

# Cota en el delay de los mensajes.
DELTA = 2

# Cota de repetición en el detector de fallas.
# BETA > DELTA
BETA = DELTA + 1

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
        self.V = [None] * (len(vecinos) + 1)
        self.V[id_nodo] = id_nodo
        self.New = set([id_nodo])
        self.rec_from = [None] * (len(vecinos) + 1)
        self.fallare = False  # Colocaremos esta en True si el nodo fallará.
        self.lider = None  # La elección del lider.
        # Atributos extra para el detector de fallas.
        self.suspected = list()  # Procesos sospechados. Inicialmente vacía.
        self.crashed = [False] * len(self.vecinos)  # Procesos que fallaron en la ronda actual.
        self.timer = DELTA  # Timer del proceso.

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
        
    def detector(self):
        """Implementación del detector de fallas perfecto."""
        # Repetimos para siempre cada BETA unidades de tiempo.
        while True:
            if env.now % BETA == 0:
                for j in self.vecinos:
                    # Si no sospechamos de Pj, le enviamos INQUIRY.
                    if j not in self.suspected:
                        data = ("INQUIRY", self.id_nodo)
                        self.canal_salida.envia(data, [j])

                # Hacemos que las entradas de crashed sean True.
                self.crashed = [True] * len(self.vecinos)
                    
                # Reiniciamos el timer a DELTA.
                self.timer = DELTA

            # Recepción de los mensajes.
            msg, sender = yield self.canal_entrada.get()

            # Caso en el que recibimos un mensaje INQUIRY.
            if msg == "INQUIRY":
                data = ("ECHO", self.id_nodo)
                self.canal_salida.envia(data, [sender])

            # Caso en el que recibimos un mensaje ECHO.
            else:
                self.crashed[sender] = False
                  
            # Cuando el timer expira agregamos sospechosos.
            if self.timer == 0:
                for j in self.vecinos:
                    if self.crashed[j]:
                        self.suspected.append(j)
            
            # Decrementamos el timer.
            self.timer -= 1


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
            print(f"El proceso {nodo.id_nodo} sospecha de {nodo.suspected}")
