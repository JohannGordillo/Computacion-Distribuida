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


class Canal(object):
    """Interfaz que modela el comportamiento que cualquier canal
    debe tomar."""
    def __init__(self, env: simpy.Environment, capacidad):
        """Constructor de la clase. Se debe inicializar la
        lista de objetos Store al ser creado un canal."""

    def envia(self, mensaje, vecinos):
        """Envia un mensaje a los canales de entrada de
        los vecinos."""

    def crea_canal_de_entrada(self):
        """Creamos un objeto Store en el un nodo recibirá
        los mensajes."""
