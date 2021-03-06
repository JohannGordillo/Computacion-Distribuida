"""
======================================================================
>> Autor: Johann Gordillo
>> Email: jgordillo@ciencias.unam.mx
>> Fecha: 05/10/2020
======================================================================
Universidad Nacional Autónoma de México
Facultad de Ciencias

Computación Distribuida [2021-1]

Práctica #01 - BFS secuencial
======================================================================
"""

class GraphNode(object):
    """Implementación simple para el nodo de una gráfica"""
    def __init__(self, val: int) -> None:
        """Constructor para el nodo

        Args:
            val (int): El elemento dentro del nodo
        """
        self.neighbors = list()
        self.visited = False
        self.val = val

    def connect(self, *nodes) -> None:
        """Conecta al nodo N con los nodos dados y
        a cada uno de estos nodos con N

        Args:
            nodes (List[GraphNode]): Una lista de nodos
        """
        for n in nodes:
            if n is not self and n not in self.neighbors:
                self.neighbors.append(n)
                n.connect(self)

    def __str__(self) -> str:
        """Regresa la representación en cadena del nodo

        Regresa:
            str: La representación en cadena del nodo
        """
        return f"({self.val})"


def bfs(root: GraphNode) -> None:
    """Algoritmo de búsqueda por amplitud

    Complejidad en Tiempo:  O(|V| + |E|)
    Complejidad en Espacio: O(n)

    Args:
        root (GraphNode): El nodo raíz
    """
    root.visited = True
    queue = [root]
    while queue:
        n = queue.pop(0)
        print(n, end="  ")
        for m in n.neighbors:
            if not m.visited:
                m.visited = True
                queue.append(m)


def main() -> None:
    """Función principal
    Ejecuta BFS con un grafo de ejemplo"""
    # Ejemplo:
    # 
    # (1)------(2)-----(6)
    #    \       \     /
    #     \       \   /
    #     (3)      (4)
    #       \      / \
    #        \    /   \
    #         \  /     \
    #          (5)-----(7)           G(V, E)
    #
    # BFS: (1)--(2)--(3)--(4)--(6)--(5)--(7)

    # Creamos 7 nodos.
    n1, n2, n3, n4, n5, n6, n7 = [GraphNode(x) for x in range(1, 8)]

    # Conectamos los nodos.
    # Como al hacer n.connect(m) se aplica a la vez m.connect(n),
    # no es necesario volver a hacer m.connect(n).
    n1.connect(n2, n3)
    n2.connect(n4, n6)
    n3.connect(n5)
    n4.connect(n5, n6, n7)
    n5.connect(n7)

    # Tomamos como raíz a n1 y hacemos BFS.
    bfs(n1)


if __name__ == "__main__":
    main()
