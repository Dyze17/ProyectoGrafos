import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox


class Grafo:
    def __init__(self):
        self.G = nx.Graph()
        self.root = tk.Tk()
        self.root.withdraw()

    def dibujar(self):
        nx.draw(self.G, with_labels=True, font_weight='bold')
        plt.show()

    def guardar(self):
        # Solicitar nombre del grafo al usuario
        decision = messagebox.askquestion("Guardar", "¿Desea guardar el grafo?")
        if decision == "yes":
            nombre = simpledialog.askstring("Nombre", "Ingrese el nombre del archivo: ")
            filename = nombre + ".png"
            nx.draw(self.G, with_labels=True, font_weight='bold')
            plt.savefig(filename)
            plt.close()  # Aqui cierro el plot luego de guardar la imagen para que la imagen se muestre correctamente
        else:
            pass

    def cargar(self):
        # Aqui abró el filedialog para que el usuario pueda seleccionar el archivo desde dentro de su memoria
        filename = filedialog.askopenfilename(filetypes=[("GraphML files", "*.graphml")])
        if filename:
            self.G = nx.read_graphml(filename)
            return True
        else:
            pass


# Aqui se crea una instancia de la clase Grafo y se llama a los metodos cargar y dibujar
if __name__ == '__main__':
    g = Grafo()
    if g.cargar():
        g.dibujar()
        g.guardar()
