class Actor:
    def __init__(self, nombre):
        self.nombre = nombre
        self.peliculas = []

    def agregar_pelicula(self, pelicula):
        self.peliculas.append(pelicula)

    def obtener_colaboradores(self, grafo):
        colaboradores = set()
        for actor_o_director in grafo.neighbors(self.nombre):
            if actor_o_director != self.nombre:
                colaboradores.add(actor_o_director)
        return colaboradores