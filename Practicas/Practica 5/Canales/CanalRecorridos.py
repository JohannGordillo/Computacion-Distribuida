"""
======================================================================
>> Autor: Johann Gordillo
>> Email: jgordillo@ciencias.unam.mx
>> Fecha: 01/12/2020
======================================================================
Universidad Nacional Autónoma de México
Facultad de Ciencias

Computación Distribuida [2021-1]

Implementación del canal.
======================================================================
"""

import simpy

from Canales.Canal import Canal


class CanalRecorridos(Canal):
    """Implementación de un canal. Permite enviar mensajes
    one-to-many."""
    def __init__(self, env, capacidad=simpy.core.Infinity):
        self.env = env
        self.capacidad = capacidad
        self.canales = list()

    def envia(self, mensaje, vecinos):
        """Envía un mensaje a los canales de salida de los
        vecinos."""
        if not self.canales:
            raise RuntimeError("No hay canales de salida.")
        eventos = list()
        for i in range(len(self.canales)):
            if i in vecinos:
                eventos.append(self.canales[i].put(mensaje))
        return self.env.all_of(eventos)

    def crea_canal_de_entrada(self):
        """Creamos un objeto Store en el que recibiremos mensajes."""
        canal_entrada = simpy.Store(self.env, capacity=self.capacidad)
        self.canales.append(canal_entrada)
        return canal_entrada
