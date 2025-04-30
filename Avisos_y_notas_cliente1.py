import tkinter as tk
from tkinter import ttk, messagebox
import requests
import tkinter.scrolledtext as scrolledtext

class AvisosAppMini:
    def __init__(self, root):
        self.root = root
        self.API_URL = "http://172.21.112.1:8000/avisos"
        self.avisos = []
        
        self.setup_estilos()
        self.crear_interfaz()
        self.cargar_avisos()

    def setup_estilos(self):
        style = ttk.Style()
        style.configure('TButton', 
                      font=('Segoe UI', 10),
                      padding=6,
                      relief="flat",
                      foreground='black')
        style.map('TButton',
                background=[
                    ('pressed', '#005499'),
                    ('active', '#e1eef7')
                ],
                foreground=[
                    ('pressed', 'white'),
                    ('active', 'black')
                ])
        self.root.option_add('*Listbox*Font', ('Segoe UI', 10))
        self.root.option_add('*Listbox*selectBackground', '#0078d7')
        self.root.option_add('*Listbox*selectForeground', 'white')

    def crear_interfaz(self):
        self.root.title("Tablero de Avisos")
        self.root.geometry("600x400")
        self.root.minsize(500, 350)
        self.root.configure(bg='#f5f5f5')
        
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Campo de búsqueda
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(
            search_frame,
            text="Filtrar",
            command=self.buscar_avisos
        ).pack(side=tk.LEFT, padx=5)

        # Opción para mostrar emojis
        self.usar_emojis = tk.BooleanVar(value=True)
        emoji_check = ttk.Checkbutton(
            main_frame,
            text="Mostrar emojis",
            variable=self.usar_emojis,
            command=self.actualizar_lista_con_emojis
        )
        emoji_check.pack(anchor=tk.W, pady=(0, 5))

        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            bg='white',
            borderwidth=1,
            relief='solid',
            highlightthickness=0
        )
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", self.mostrar_detalles)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        botones = [
            ("Nuevo", self.nuevo_aviso),
            ("Editar", self.editar_aviso),
            ("Eliminar", self.eliminar_aviso),
            ("Actualizar", self.cargar_avisos)
        ]
        
        for text, cmd in botones:
            btn = ttk.Button(
                btn_frame,
                text=text,
                command=cmd,
                style='TButton'
            )
            btn.pack(side=tk.LEFT, padx=5, ipadx=5)

    def cargar_avisos(self):
        try:
            response = requests.get(self.API_URL, timeout=5)
            response.raise_for_status()
            self.avisos = response.json()
            self.actualizar_lista_con_emojis()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la lista:\n{str(e)}")

    def actualizar_lista_con_emojis(self):
        self.listbox.delete(0, tk.END)
        for aviso in self.avisos:
            texto = f"{aviso['id']} | {aviso['titulo']}"
            if self.usar_emojis.get():
                texto = f"{aviso['id']} | 📢 {aviso['titulo']}"
            self.listbox.insert(tk.END, texto)

    def mostrar_detalles(self, event=None):
        sel = self.listbox.curselection()
        if not sel: return
        
        aviso_id = self.listbox.get(sel[0]).split('|')[0].strip()
        try:
            response = requests.get(f"{self.API_URL}/{aviso_id}", timeout=5)
            response.raise_for_status()
            aviso = response.json()
            
            top = tk.Toplevel(self.root)
            top.title("Detalles del Aviso")
            top.geometry("450x350")
            
            frame = ttk.Frame(top, padding=15)
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(
                frame,
                text=aviso['titulo'],
                font=('Segoe UI', 12, 'bold'),
                foreground="#0078d7"
            ).pack(anchor=tk.W, pady=(0, 10))
            
            ttk.Label(frame, text="Contenido:").pack(anchor=tk.W)
            contenido = scrolledtext.ScrolledText(
                frame,
                wrap=tk.WORD,
                font=('Segoe UI', 10),
                padx=5,
                pady=5
            )
            contenido.pack(fill=tk.BOTH, expand=True)
            contenido.insert(tk.END, aviso['contenido'])
            contenido.config(state=tk.DISABLED)
            
            ttk.Label(
                frame,
                text=f"Creado: {aviso['creado_en']}\nEditado: {aviso['actualizado_en']}",
                font=('Segoe UI', 9),
                foreground="#555555"
            ).pack(anchor=tk.W, pady=(5, 10))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el aviso:\n{str(e)}")

    def nuevo_aviso(self):
        self.formulario_aviso()

    def editar_aviso(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Advertencia", "Seleccione un aviso para editar")
            return
            
        aviso_id = self.listbox.get(sel[0]).split('|')[0].strip()
        try:
            response = requests.get(f"{self.API_URL}/{aviso_id}", timeout=5)
            response.raise_for_status()
            self.formulario_aviso(response.json())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el aviso:\n{str(e)}")
    
    def buscar_avisos(self):
        consulta = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)
        for aviso in self.avisos:
            if consulta in aviso['titulo'].lower() or consulta in aviso['contenido'].lower():
                texto = f"{aviso['id']} | {aviso['titulo']}"
                if self.usar_emojis.get():
                    texto = f"{aviso['id']} | 📢 {aviso['titulo']}"
                self.listbox.insert(tk.END, texto)

    def eliminar_aviso(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Advertencia", "Seleccione un aviso para eliminar")
            return
            
        aviso_id = self.listbox.get(sel[0]).split('|')[0].strip()
        if messagebox.askyesno(
            "Confirmar eliminación",
            "¿Está seguro de eliminar este aviso?",
            icon="warning"
        ):
            try:
                response = requests.delete(f"{self.API_URL}/{aviso_id}", timeout=5)
                response.raise_for_status()
                self.cargar_avisos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{str(e)}")

    def formulario_aviso(self, aviso=None):
        top = tk.Toplevel(self.root)
        top.title("Editar Aviso" if aviso else "Nuevo Aviso")
        top.geometry("450x350")
        
        frame = ttk.Frame(top, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Título:").pack(anchor=tk.W)
        titulo = ttk.Entry(frame, font=('Segoe UI', 10))
        titulo.pack(fill=tk.X, pady=(0, 10))
        if aviso:
            titulo.insert(0, aviso['titulo'])
        
        ttk.Label(frame, text="Contenido:").pack(anchor=tk.W)
        contenido = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            height=8
        )
        contenido.pack(fill=tk.BOTH, expand=True)
        if aviso:
            contenido.insert(tk.END, aviso['contenido'])
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        def guardar():
            datos = {
                "titulo": titulo.get(),
                "contenido": contenido.get("1.0", tk.END).strip()
            }
            
            if not datos["titulo"] or not datos["contenido"]:
                messagebox.showwarning("Validación", "Todos los campos son requeridos")
                return
                
            try:
                if aviso:
                    response = requests.put(
                        f"{self.API_URL}/{aviso['id']}",
                        json=datos,
                        timeout=5
                    )
                else:
                    response = requests.post(
                        self.API_URL,
                        json=datos,
                        timeout=5
                    )
                
                response.raise_for_status()
                self.cargar_avisos()
                top.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")
        
        ttk.Button(
            btn_frame,
            text="Guardar",
            command=guardar
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=top.destroy
        ).pack(side=tk.RIGHT)

if __name__ == "__main__":
    root = tk.Tk()
    app = AvisosAppMini(root)
    root.mainloop()
