import tkinter as tk
from tkinter import ttk
import csv

# Leer el CSV y construir diccionario {Producto: [Subproductos]}
def leer_datos_csv(ruta_csv):
    datos = {}
    with open(ruta_csv, newline='', encoding='latin-1') as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            producto = fila['Producto'].strip()
            subproducto = fila['Subproducto'].strip()
            if producto and subproducto:
                if producto not in datos:
                    datos[producto] = []
                datos[producto].append(subproducto)
    return datos

# Actualizar submenú cuando se elige un producto
def actualizar_submenu(*args):
    producto_seleccionado = producto_var.get()
    subproductos = datos.get(producto_seleccionado, [])
    
    # Limpiar y volver a crear el menú
    menu_sub = submenu["menu"]
    menu_sub.delete(0, "end")
    
    for sub in subproductos:
        menu_sub.add_command(label=sub, command=tk._setit(subproducto_var, sub))
    
    # Reiniciar valor seleccionado
    if subproductos:
        subproducto_var.set(subproductos[0])
    else:
        subproducto_var.set("Sin opciones")

# Crear ventana principal
root = tk.Tk()
root.title("Menú dependiente desde CSV")

# Variables para los OptionMenu
producto_var = tk.StringVar()
subproducto_var = tk.StringVar()

# Leer CSV
datos = leer_datos_csv("datos.csv")
productos = sorted(datos.keys())

# Menú 1: Producto
producto_var.set("Seleccionar")
menu1 = ttk.OptionMenu(root, producto_var, producto_var.get(), *productos)
menu1.pack(padx=10, pady=10)

# Menú 2: Subproducto (inicialmente vacío)
subproducto_var.set("Selecciona un producto")
submenu = ttk.OptionMenu(root, subproducto_var, subproducto_var.get(), "")
submenu.pack(padx=10, pady=10)

# Cuando cambia el producto, actualizamos subproductos
producto_var.trace_add("write", actualizar_submenu)

root.mainloop()
