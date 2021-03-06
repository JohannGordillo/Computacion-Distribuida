"""
======================================================================
>> Autor: Johann Gordillo
>> Email: jgordillo@ciencias.unam.mx
>> Fecha: 21/10/2020
======================================================================
Universidad Nacional Autónoma de México
Facultad de Ciencias

Computación Distribuida [2021-1]

Implementación de un canal para los ejercicios de la práctica.
======================================================================
"""

import simpy


class Canal(object):
    """Implementación de un canal."""
    def __init__(self, env, capacity=simpy.core.Infinity):
        self.env = env
        self.capacity = capacity
        self.channels = list()
        self.output_channel = None

    def send(self, msg, neighbors):
        """Envía un mensaje a los canales de salida de los vecinos."""
        if self.output_channel is None:
            raise RuntimeError("No hay canales de salida.")
        events = list()
        l = len(self.channels)
        for i in range(l):
            if i in neighbors:
                events.append(self.channels[i].put(msg))
        return self.env.all_of(events)

    def create_input_channel(self):
        """Creamos un objeto Store en el que recibiremos mensajes."""
        channel = simpy.Store(self.env, capacity=self.capacity)
        self.channels.append(channel)
        self.output_channel = channel
        return channel

    def get_output_channel(self):
        """Regresa el objeto Store en el cual recibiremos los mensajes."""
        return self.output_channel
