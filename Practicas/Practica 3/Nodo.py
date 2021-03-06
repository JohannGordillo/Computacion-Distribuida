"""
======================================================================
>> Autor: Johann Gordillo
>> Email: jgordillo@ciencias.unam.mx
>> Fecha: 03/11/2020
======================================================================
Universidad Nacional Autónoma de México
Facultad de Ciencias

Computación Distribuida [2021-1]

Implementación de la interfaz nodo.
======================================================================
"""

import simpy


class Nodo:
    """Representa un nodo.

    Cada nodo tiene un id, una lista de vecinos y dos canales de
    comunicación. Los métodos que tiene son únicamente getters."""
    def __init__(self, id_nodo: int, vecinos: list,
                 canal_entrada: simpy.Store,
                 canal_salida: simpy.Store):
        """Inicializa los atributos del nodo."""

    def get_id(self) -> int:
        """Regresa el id del nodo."""
