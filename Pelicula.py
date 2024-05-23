from ListaEnlazada import ListaEnlazada

class Pelicula:
    def __init__(self, titulo, director):
        self.titulo = titulo
        self.director = director
        self.actores = ListaEnlazada()

    def agregar_actor(self, actor):
        self.actores.agregar(actor)

    def imprimir_actores(self):
        print(f"Actores de la película {self.titulo}:")
        self.actores.imprimir()