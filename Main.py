import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import re
import scipy as sp
from ListaEnlazada import ListaEnlazada
from Pelicula import Pelicula
from Actor import Actor
from Director import Director

class Main:
    def __init__(self, archivo_csv):
        self.grafo, self.actores_directores = self.leer_dataset(archivo_csv)

    def leer_dataset(self, archivo_csv):
        grafo = nx.Graph()
        actores_directores = {}

        try:
            df = pd.read_csv(archivo_csv)

            for index, row in df.iterrows():
                titulo_pelicula = row['Series_Title']
                director = row['Director']

                actores = [row['Star1'], row['Star2'], row['Star3'], row['Star4']]
                actores = [actor for actor in actores if pd.notna(actor)]

                if director not in actores_directores:
                    actores_directores[director] = Director(director)
                director_objeto = actores_directores[director]
                director_objeto.agregar_pelicula(titulo_pelicula)

                for actor in actores:
                    if actor not in actores_directores:
                        actores_directores[actor] = Actor(actor)
                    actor_objeto = actores_directores[actor]
                    actor_objeto.agregar_pelicula(titulo_pelicula)

                    if not grafo.has_edge(director, actor):
                        grafo.add_edge(director, actor, peliculas=[])
                    if titulo_pelicula not in grafo[director][actor]['peliculas']:
                        grafo[director][actor]['peliculas'].append(titulo_pelicula)

                    for co_actor in actores:
                        if co_actor != actor:
                            if not grafo.has_edge(actor, co_actor):
                                grafo.add_edge(actor, co_actor, peliculas=[])
                            if titulo_pelicula not in grafo[actor][co_actor]['peliculas']:
                                grafo[actor][co_actor]['peliculas'].append(titulo_pelicula)

        except FileNotFoundError:
            print(f"Error: El archivo '{archivo_csv}' no se encontró.")
            return None, None

        return grafo, actores_directores

    def obtener_colaboradores_frecuentes(self, actor_nombre):
        actor = self.actores_directores.get(actor_nombre)
        if not actor:
            return []

        colaboradores = actor.obtener_colaboradores(self.grafo)
        colaboradores_frecuentes = [(colaborador, self.grafo[actor_nombre][colaborador]['peliculas'])
                                    for colaborador in colaboradores if len(self.grafo[actor_nombre][colaborador]['peliculas']) >= 2]
        return colaboradores_frecuentes

    def buscar_camino_bfs(self, actor1, actor2):
        if actor1 not in self.grafo or actor2 not in self.grafo:
            print("Uno o ambos actores no están en el grafo.")
            return []

        try:
            camino = nx.shortest_path(self.grafo, source=actor1, target=actor2)
            return camino
        except nx.NetworkXNoPath:
            print(f"No se encontró camino entre {actor1} y {actor2}.")
            return []

    def buscar_colaboraciones_dfs(self, actor_nombre):
        if actor_nombre not in self.grafo:
            print(f"{actor_nombre} no está en el grafo.")
            return []

        colaboraciones = []
        for vecino in nx.dfs_preorder_nodes(self.grafo, source=actor_nombre):
            if vecino != actor_nombre and self.grafo.has_edge(actor_nombre, vecino):
                peliculas = self.grafo[actor_nombre][vecino]['peliculas']
                colaboraciones.append((vecino, peliculas))
        return colaboraciones

    def mostrar_grafo(self):
        plt.figure(figsize=(24, 18))

        pos = nx.spring_layout(self.grafo, seed=42, k=0.3)  # El parámetro k ajusta la distancia entre nodos

        actores = [n for n in self.grafo.nodes if isinstance(self.actores_directores[n], Actor)]
        directores = [n for n in self.grafo.nodes if isinstance(self.actores_directores[n], Director)]

        nx.draw_networkx_nodes(self.grafo, pos, nodelist=actores, node_size=200, node_color='lightblue', node_shape='o', alpha=0.8)
        nx.draw_networkx_nodes(self.grafo, pos, nodelist=directores, node_size=200, node_color='lightgreen', node_shape='s', alpha=0.8)

        nx.draw_networkx_edges(self.grafo, pos, edge_color='gray', width=0.5)

        labels = {n: n for n in self.grafo.nodes()}
        nx.draw_networkx_labels(self.grafo, pos, labels, font_size=6, font_weight='bold')

        plt.title("Grafo de Colaboraciones")
        plt.show()

    def mostrar_menu(self):
        print("\n**Menú Principal**")
        print("1. Obtener colaboradores frecuentes de un actor")
        print("2. Encontrar camino más corto entre dos actores (BFS)")
        print("3. Explorar todas las colaboraciones de un actor (DFS)")
        print("4. Mostrar grafo")
        print("5. Salir")

        opcion = input("Ingrese una opción: ")
        return opcion

    def run(self):
        if self.grafo is None or self.actores_directores is None:
            print("No se puede continuar sin el archivo de datos.")
            return

        while True:
            opcion = self.mostrar_menu()

            if opcion == '1':
                nombre_actor = input("Ingrese el nombre del actor: ")
                colaboradores_frecuentes = self.obtener_colaboradores_frecuentes(nombre_actor)
                if colaboradores_frecuentes:
                    print(f"Colaboradores frecuentes de {nombre_actor}:")
                    for colaborador, peliculas in colaboradores_frecuentes:
                        print(f"- {colaborador}: {', '.join(peliculas)}")
                else:
                    print(f"No se encontraron colaboradores frecuentes para {nombre_actor}.")

            elif opcion == '2':
                actor1 = input("Ingrese el nombre del primer actor: ")
                actor2 = input("Ingrese el nombre del segundo actor: ")
                camino_corto = self.buscar_camino_bfs(actor1, actor2)

                if camino_corto:
                    print(f"Camino más corto entre {actor1} y {actor2}: {camino_corto}")
                    for i in range(len(camino_corto) - 1):
                        peliculas = self.grafo[camino_corto[i]][camino_corto[i+1]]['peliculas']
                        print(f"De {camino_corto[i]} a {camino_corto[i+1]}: {', '.join(peliculas)}")
                else:
                    print(f"No se encontró camino entre {actor1} y {actor2}.")

            elif opcion == '3':
                nombre_actor = input("Ingrese el nombre del actor: ")
                colaboraciones_extendidas = self.buscar_colaboraciones_dfs(nombre_actor)
                if colaboraciones_extendidas:
                    print(f"Colaboraciones extendidas de {nombre_actor}:")
                    for colaborador, peliculas in colaboraciones_extendidas:
                        print(f"- {colaborador}: {', '.join(peliculas)}")
                else:
                    print(f"No se encontraron colaboraciones extendidas para {nombre_actor}.")

            elif opcion == '4':
                self.mostrar_grafo()

            elif opcion == '5':
                print("Saliendo del programa...")
                break

            else:
                print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    main = Main("imdb_top_1000.csv")
    main.run()