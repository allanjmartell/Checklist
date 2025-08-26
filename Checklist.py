import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from fpdf import FPDF
import os
import csv

# Crear la ventana principal
root = tk.Tk()
root.title("Checklist de Validación")

# Crear un estilo personalizado
style = ttk.Style()
style.theme_use("clam")  # "clam" permite más personalización

# Personalizar el fondo del OptionMenu
style.configure("Custom.TMenubutton",
                background="#5C8FB6",   # Color de fondo
                foreground="white",    # Color del texto
                arrowcolor="white",    # Color de la flechita
                relief="groove",         # Estilo del borde (opcional)
                borderwidth=2,          # Ancho del borde
                font=("Segoe UI", 8))  

# Personalizar el fondo del OptionMenu
style.configure("Small.TCombobox",
                fieldbackground="#5C8FB6",   # Color de fondo
                background= "#5C8FB6",
                foreground="white",    # Color del texto
                arrowcolor="white",    # Color de la flechita
                padding = 5,
                selectbackground="#5C8FB6",  # <- color al seleccionar
                relief="groove",         # Estilo del borde (opcional)
                borderwidth=2,          # Ancho del borde
                font=("Segoe UI", 5)) 

# Crear el frame principal
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
frame.pack()

# Crear las etiquetas y opciones de selección
fields = [
    "¿Se recibe Arte?", "¿Se recibe Base de Datos?", "¿Se recibe Layout?", 
    "¿Se recibe Vo.Bo.?", "Ordenamiento", "Muestra Física", 
    "Código de Barras", "Foliatura"
]
variables = {}

x = 3
y = 0

for idx, field in enumerate(fields):
    if idx % 2 != 0:
        idx -= 1
        y = 5
    else:
        y = 0

    label = ttk.Label(frame, text=field)
    label.grid(row=idx + x, column=y, sticky=tk.W, pady=10)

    var = tk.StringVar(value="N/A")
    variables[field] = var

    ttk.Radiobutton(frame, text="Sí", variable=var, value="Sí").grid(row=idx + x, column=y + 1, padx=5)
    ttk.Radiobutton(frame, text="No", variable=var, value="No").grid(row=idx + x, column=y + 2, padx=5)
    ttk.Radiobutton(frame, text="N/A", variable=var, value="N/A").grid(row=idx + x, column=y + 3, padx=5)

# JOB
job_label = ttk.Label(frame, text="JOB:")
job_label.grid(row=0, column=0, sticky=tk.W, pady=5)

job_var = tk.StringVar()
job_entry = ttk.Entry(frame, textvariable=job_var, width=40, justify='center')
job_entry.grid(row=0, column=1, columnspan=3, pady=5)

# Celda vacía en la columna 4 para separar
vacio_col4 = ttk.Label(frame, text="                 ")
vacio_col4.grid(row=0, column=4, sticky=tk.W, pady=10)

# FECHA
fecha_label = ttk.Label(frame, text="Fecha:")
fecha_label.grid(row=0, column=5, sticky=tk.W, pady=5)

fecha_var = tk.StringVar()
fecha_entry = ttk.Entry(frame, textvariable=fecha_var, width=40, justify='center')
fecha_entry.grid(row=0, column=6, columnspan=3, pady=5)

# Leer el CSV y construir diccionario {Producto: [Subproductos]}
def leer_datos_csv(ruta_csv):
    datos = {}
    with open(ruta_csv, newline='', encoding='latin-1') as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            producto = fila['Cliente'].strip()
            subproducto = fila['Producto'].strip()
            if producto and subproducto:
                if producto not in datos:
                    datos[producto] = []
                datos[producto].append(subproducto)
    return datos

class AutocompleteEntry(tk.Entry):
    def __init__(self, parent, lista=[], *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.lista = lista
        self.listbox = None
        self.var = self["textvariable"] = tk.StringVar()
        self.var.trace("w", self.actualizar)
        self.bind("<Down>", self.mover_abajo)
        self.bind("<Return>", self.seleccionar)
        self.bind("<Escape>", self.ocultar)
        self.bind("<FocusOut>", self.ocultar)

        # Estilo visual tipo ttk
        style = ttk.Style()
        bordercolor = "#A3A3A3"

        self.configure(
            bg="#5C8FB6",
            fg="#FFFFFF",
            font=("Segoe UI", 8),
            relief="solid",
            bd=1,
            highlightbackground=bordercolor,
            highlightcolor=bordercolor,
            highlightthickness=1,
            insertbackground="#FFFFFF",
            justify='center'
        )

    def actualizar(self, *args):
        texto = self.var.get().lower()
        coincidencias = [x for x in self.lista if texto in x.lower()]

        if coincidencias:
            if not self.listbox:
                self.listbox = tk.Listbox(self.master, height=5, width=40,
                                          relief="solid", bd=1, highlightthickness=1,
                                          activestyle="none")
                self.listbox.bind("<<ListboxSelect>>", self.seleccionar)
                self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())

                # Cierre automático al hacer clic fuera de la lista
                self.listbox.bind("<FocusOut>", lambda e: self.after(100, self.ocultar))

                # Estilo ttk visual
                style = ttk.Style()
                bg = style.lookup("TEntry", "fieldbackground") or "white"
                fg = style.lookup("TEntry", "foreground") or "black"
                font = style.lookup("TEntry", "font") or "TkDefaultFont"
                self.listbox.configure(
                    bg=bg,
                    fg=fg,
                    font=("Segoe UI", 8),
                    selectbackground="#D9EAF7"
                )

            self.listbox.delete(0, tk.END)
            for item in coincidencias:
                self.listbox.insert(tk.END, item)
        else:
            self.ocultar()

    def mover_abajo(self, event):
        if self.listbox:
            self.listbox.focus_set()
            self.listbox.select_set(0)

    def seleccionar(self, event=None):
        if self.listbox and self.listbox.curselection():
            valor = self.listbox.get(self.listbox.curselection()[0])
            self.var.set(valor)
        self.ocultar()

    def ocultar(self, event=None):
        if self.listbox:
            self.listbox.destroy()
            self.listbox = None

    def set_lista(self, nueva_lista):
        self.lista = nueva_lista
        self.actualizar()

datos = leer_datos_csv("BD.csv")
productoscsv = sorted(datos.keys())

# CLIENTE
cliente_label = ttk.Label(frame, text="Cliente:")
cliente_label.grid(row=1, column=0, sticky=tk.W, pady=5)

cliente_var = tk.StringVar()

cliente_menu = ttk.Combobox(frame, textvariable=cliente_var, values=list(datos.keys()), width=35, justify="center", state="normal", style="Small.TCombobox")
cliente_menu.option_add("*TCombobox*Listbox.font", ("Segoe UI", 8))  # Cambia el menú desplegable
cliente_menu.configure(font=("Segoe UI", 8))  # Cambia la parte visible del combobox
cliente_menu.grid(row=1, column=1, columnspan=3, pady=5)

cliente_var.set("Selecciona un cliente")

# PRODUCTO
producto_label = ttk.Label(frame, text="Producto:")
producto_label.grid(row=1, column=5, sticky=tk.W, pady=5)

producto_var = tk.StringVar()
producto_entry = AutocompleteEntry(frame, width=25)
producto_entry.grid(row=1, column=6, columnspan=2, pady=5)

comprod_var_final = tk.StringVar()
comprod_entry_final = ttk.Entry(frame, textvariable=comprod_var_final, width=13, justify='center')
comprod_entry_final.grid(row=1, column=8, columnspan=1, pady=5)

# Al seleccionar cliente, actualizar productos
def actualizar_productos(*args):
    cliente = cliente_var.get()
    productos = datos.get(cliente, [])
    producto_entry.set_lista(sorted(set(productos)))
    producto_entry.var.set("")  # limpiar

# Eventos
cliente_var.trace_add("write", actualizar_productos)

# RANGO FOLIATURA
rango_label = ttk.Label(frame, text="Rango:")
rango_label.grid(row=len(fields) + 2, column=5, sticky=tk.W, pady=5)

rango_var_inicial = tk.StringVar()
rango_entry_inicial = ttk.Entry(frame, textvariable=rango_var_inicial, width=13, justify='center')
rango_entry_inicial.grid(row=len(fields) + 2, column=6, columnspan=1, pady=5)

rango_label2 = ttk.Label(frame, text="           al")
rango_label2.grid(row=len(fields) + 2, column=7, sticky=tk.W, pady=5)

rango_var_final = tk.StringVar()
rango_entry_final = ttk.Entry(frame, textvariable=rango_var_final, width=13, justify='center')
rango_entry_final.grid(row=len(fields) + 2, column=8, columnspan=1, pady=5)

# Prueba Código de Barras
barcode_label = ttk.Label(frame, text="Prueba Código de Barras:")
barcode_label.grid(row=len(fields) + 2, column=0, sticky=tk.W, pady=5)

barcode_var = tk.StringVar()
barcode_entry = ttk.Entry(frame, textvariable=barcode_var, width=40, justify='center')
barcode_entry.grid(row=len(fields) + 2, column=1, columnspan=3, pady=5)

# Tipo Código de Barras
typebar_label = ttk.Label(frame, text="Tipo Código de Barras:")
typebar_label.grid(row=len(fields) + 3, column=0, sticky=tk.W, pady=5)

typebar_var = tk.StringVar()
typebar_entry = ttk.OptionMenu(frame, typebar_var, "Seleccionar", "N/A", "3 de 9", "Code 128", "EAN 13", "QR", "ITF")
typebar_entry.config(style="Custom.TMenubutton")  # Aplicar el estilo
typebar_entry.grid(row=len(fields) + 3, column=1, columnspan=3, pady=5)

# Impresión
impresion_label = ttk.Label(frame, text="Tipo Impresión:")
impresion_label.grid(row=len(fields) + 5, column=5, sticky=tk.W, pady=5)

varimp = tk.StringVar(value="N/A")

ttk.Radiobutton(frame, text="Simplex", variable=varimp, value="Simplex").grid(row=len(fields) + 5, column=6, padx=5)
ttk.Radiobutton(frame, text="Duplex", variable=varimp, value="Duplex").grid(row=len(fields) + 5, column=7, padx=5)

# Tipo de Documento
documento_label = ttk.Label(frame, text="Tipo Documento:")
documento_label.grid(row=len(fields) + 5, column=0, sticky=tk.W, pady=5)

vardoc = tk.StringVar(value="N/A")

ttk.Radiobutton(frame, text="PDF", variable=vardoc, value="PDF").grid(row=len(fields) + 5, column=1, padx=5)
ttk.Radiobutton(frame, text="AFP", variable=vardoc, value="AFP").grid(row=len(fields) + 5, column=2, padx=5)
ttk.Radiobutton(frame, text="PS", variable=vardoc, value="PS").grid(row=len(fields) + 5, column=3, padx=5)

# Tamaño Documento
tamaño_label = ttk.Label(frame, text="Tamaño Documento:")
tamaño_label.grid(row=len(fields) + 6, column=0, sticky=tk.W, pady=5)

tamaño_var = tk.StringVar()
tamaño_entry = ttk.OptionMenu(frame, tamaño_var, "Seleccionar", "Carta", "Tabloide", "33 x 48 cm", "48.2 x 21.55 cm")
tamaño_entry.config(style="Custom.TMenubutton")  # Aplicar el estilo
tamaño_entry.grid(row=len(fields) + 6, column=1, columnspan=3, pady=5)

# Máquina
maquina_label = ttk.Label(frame, text="Máquina:")
maquina_label.grid(row=len(fields) + 6, column=5, sticky=tk.W, pady=5)

maquina_var = tk.StringVar()
maquina_entry = ttk.OptionMenu(frame, maquina_var, "Seleccionar", "Canon", "HP", "OCE", "Zebra")
maquina_entry.config(style="Custom.TMenubutton")  # Aplicar el estilo
maquina_entry.grid(row=len(fields) + 6, column=6, columnspan=3, pady=5)

# Desarrolladores
dev_label = ttk.Label(frame, text="Desarrolladores")
dev_label.grid(row=len(fields) + 8, column=0, sticky=tk.W, pady=5)

dev_var = tk.StringVar()
dev_menu = ttk.OptionMenu(frame, dev_var, "Seleccionar", "Rocío González", "Allan Martell")
dev_menu.config(style="Custom.TMenubutton")  # Aplicar el estilo
dev_menu.grid(row=len(fields) + 8, column=1, columnspan=3, pady=5)

# Función para guardar el PDF
def save_pdf():
    job_name = job_var.get()
    if not job_name:
        messagebox.showerror("Error", "El campo JOB no puede estar vacío.")
        return

    # Crear la carpeta JOBS si no existe
    if not os.path.exists("JOBS"):
        os.makedirs("JOBS")

    # Crear el PDF
    pdf = FPDF()
    pdf.add_page()

    # Insertar la imagen
    pdf.image("Formex_logo.jpeg", x=10, y=8, w=60)

    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.cell(250, 10, txt="Checklist Desarrollo Dato Variable", ln=True, align="C")
    pdf.ln(20)  # Espacio después del título

    # Configurar 2 columnas
    pdf.set_font("Arial", size=12)
    col_width = 90  # Ancho de la columna
    start_y = pdf.get_y()
    
    # Primera columna
    pdf.set_x(10)
    pdf.cell(col_width, 10, txt=f"JOB: {job_var.get()}", ln=False, align="L")
    pdf.cell(col_width, 10, txt=f"Fecha: {fecha_var.get()}", ln=False, align="R")
    pdf.ln(10)
    
    pdf.cell(col_width, 10, txt=f"Cliente: {cliente_var.get()}", ln=False, align="L")
    pdf.ln(10)
    pdf.cell(col_width, 10, txt=f"Producto: {producto_entry.get()} {comprod_var_final.get()}", ln=False, align="L")
    pdf.ln(10)

    for idx, (field, var) in enumerate(variables.items()):
        if(idx%2 != 0):
            alinea = "R"     
        else:
            alinea = "L"
            pdf.ln(10)
        pdf.cell(col_width, 10, txt=f"{field}: {var.get()}", ln=False, align=alinea)

    # Agregar rango, prueba de código de barras, y demás campos adicionales en la segunda columna
    pdf.ln(10)
    pdf.cell(col_width, 10, txt=f"Tipo Código de Barras: {typebar_var.get()}", ln=False, align="L")
    pdf.cell(col_width, 10, txt=f"Rango: Del {rango_var_inicial.get()} al {rango_var_final.get()}", ln=True, align="R")
    pdf.cell(col_width, 10, txt=f"Prueba Código de Barras: {barcode_var.get()}", ln=False, align="L")
    pdf.ln(30)
    pdf.cell(col_width, 10, txt=f"Tipo Impresión: {varimp.get()}", ln=False, align="L")
    pdf.cell(col_width, 10, txt=f"Tipo Documento: {vardoc.get()}", ln=False, align="R")
    pdf.ln(10)
    pdf.cell(col_width, 10, txt=f"Tamaño Documento: {tamaño_var.get()}", ln=False, align="L")
    pdf.cell(col_width, 10, txt=f"Máquina: {maquina_var.get()}", ln=False, align="R")
    pdf.ln(30)
    # Espacio para firmas
    pdf.cell(200, 10, txt=f"Desarrollador: {dev_var.get()}", ln=True, align="L")

    # Espacio para las firmas
    pdf.ln(20)
    pdf.cell(90, 10, txt="Desarrollador:", ln=False, align="L")
    pdf.cell(90, 10, txt="Jefe Digital:", ln=False, align="L")
    pdf.ln(20)

    pdf.cell(90, 10, txt="________________________", ln=False, align="L")
    pdf.cell(90, 10, txt="________________________", ln=False, align="L")


    # Guardar el PDF
    pdf.output(f"JOBS/{job_name}.pdf")
    messagebox.showinfo("Éxito", f"PDF guardado como JOBS/{job_name}.pdf")

# Botón para aceptar y guardar el PDF
save_button = ttk.Button(frame, text="Aceptar", command=save_pdf)
save_button.grid(row=len(fields) + 9, column=2, pady=10)

# Botón para cancelar
cancel_button = ttk.Button(frame, text="Cancelar", command=root.quit)
cancel_button.grid(row=len(fields) + 9, column=3, pady=10)

# Iniciar la aplicación
root.mainloop()
