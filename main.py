# instalar : pip install pyodbc
# si te da error : python -m pip install pyodbc

import tkinter as tk
from tkinter import messagebox
import pyodbc

# ----------------- Configuración DB -----------------
CONN_STR = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=DESKTOP-6L6ASHP\\SQLEXPRESS;"
    "Database=TkMarketplace;"
    "Trusted_Connection=yes;"
)

# ----------------- App principal -----------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mi Tienda / Cliente")
        # Abrimos conexión al iniciar app
        self.conn = pyodbc.connect(CONN_STR)
        self.user_id = None
        self.user_tipo = None  # 'Cliente' o 'Tienda'

        # Contenedor de frames
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Creamos e instanciamos todos los frames
        self.frames = {}
        for F in (StartPage,
                  RegisterClientPage,
                  RegisterStorePage,
                  LoginPage,
                  CustomerPage,
                  VendorPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Arrancamos mostrando la página de inicio
        self.show_frame("StartPage")

        # Al cerrar ventana, hacemos logout + close connection
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def on_close(self):
        # Si había sesión iniciada, la cerramos
        if self.user_id:
            try:
                cursor = self.conn.cursor()
                cursor.execute("EXEC sp_cerrarSesion @UserID = ?", self.user_id)
                self.conn.commit()
            except Exception as e:
                print("Error cerrando sesión:", e)
        # Cerramos conexión y salimos
        self.conn.close()
        self.destroy()


# ----------------- Página de inicio -----------------
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Bienvenido, elige una opción:").pack(pady=10)

        tk.Button(self, text="Registrarme como Cliente",
                  command=lambda: controller.show_frame("RegisterClientPage")
        ).pack(fill="x", padx=50, pady=5)

        tk.Button(self, text="Registrarme como Tienda",
                  command=lambda: controller.show_frame("RegisterStorePage")
        ).pack(fill="x", padx=50, pady=5)

        tk.Button(self, text="Iniciar Sesión",
                  command=lambda: controller.show_frame("LoginPage")
        ).pack(fill="x", padx=50, pady=5)


# ----------------- Registro Cliente -----------------
class RegisterClientPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.ctrl = controller

        tk.Label(self, text="Registrar Nuevo Cliente").pack(pady=10)
        # Campos
        self.email = tk.Entry(self);     tk.Label(self, text="Correo").pack();     self.email.pack()
        self.password = tk.Entry(self, show="*"); tk.Label(self, text="Password").pack(); self.password.pack()
        self.nombre = tk.Entry(self);    tk.Label(self, text="Nombre").pack();     self.nombre.pack()
        self.apellido = tk.Entry(self);  tk.Label(self, text="Apellido").pack();   self.apellido.pack()
        self.telefono = tk.Entry(self);  tk.Label(self, text="Teléfono").pack();   self.telefono.pack()

        tk.Button(self, text="Enviar",
                  command=self.on_submit).pack(pady=5)
        tk.Button(self, text="Cancelar",
                  command=lambda: controller.show_frame("StartPage")).pack()

    def on_submit(self):
        try:
            cursor = self.ctrl.conn.cursor()
            cursor.execute(
                """EXEC sp_RegistrarNuevosClientes
                   @Correo=?, @Password=?, @Nombre=?, @Apellido=?, @Telefono=?""",
                self.email.get(), self.password.get(),
                self.nombre.get(), self.apellido.get(),
                int(self.telefono.get())
            )
            row = cursor.fetchone()
            self.ctrl.conn.commit()
            messagebox.showinfo("OK", row.Mnesaje)
            self.ctrl.show_frame("StartPage")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ----------------- Registro Tienda -----------------
class RegisterStorePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.ctrl = controller

        tk.Label(self, text="Registrar Nueva Tienda").pack(pady=10)
        # Campos
        self.email = tk.Entry(self);       tk.Label(self, text="Correo").pack();     self.email.pack()
        self.password = tk.Entry(self, show="*"); tk.Label(self, text="Password").pack(); self.password.pack()
        self.nombre = tk.Entry(self);      tk.Label(self, text="Nombre Tienda").pack();   self.nombre.pack()
        self.nombreJ = tk.Entry(self);     tk.Label(self, text="Razón Social").pack();   self.nombreJ.pack()
        self.nit = tk.Entry(self);         tk.Label(self, text="NIT").pack();           self.nit.pack()
        self.telefono = tk.Entry(self);    tk.Label(self, text="Teléfono").pack();      self.telefono.pack()
        self.cat_id = tk.Entry(self);      tk.Label(self, text="CategoríaID").pack();   self.cat_id.pack()

        tk.Button(self, text="Enviar",
                  command=self.on_submit).pack(pady=5)
        tk.Button(self, text="Cancelar",
                  command=lambda: controller.show_frame("StartPage")).pack()

    def on_submit(self):
        try:
            cursor = self.ctrl.conn.cursor()
            cursor.execute(
                """EXEC sp_registrarNuevaTienda
                   @Correo=?, @Password=?, @Nombre=?, @NombreJuridico=?,
                   @NIT=?, @Teloefono=?, @CategoriaID=?""",
                self.email.get(), self.password.get(),
                self.nombre.get(), self.nombreJ.get(),
                int(self.nit.get()), int(self.telefono.get()),
                int(self.cat_id.get())
            )
            row = cursor.fetchone()
            self.ctrl.conn.commit()
            messagebox.showinfo("OK", row.Mensaje)
            self.ctrl.show_frame("StartPage")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ----------------- Login -----------------
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.ctrl = controller

        tk.Label(self, text="Iniciar Sesión").pack(pady=10)
        self.email = tk.Entry(self);     tk.Label(self, text="Correo").pack();     self.email.pack()
        self.password = tk.Entry(self, show="*"); tk.Label(self, text="Password").pack(); self.password.pack()

        tk.Button(self, text="Entrar", command=self.on_login).pack(pady=5)
        tk.Button(self, text="Cancelar",
                  command=lambda: controller.show_frame("StartPage")).pack()

    def on_login(self):
        try:
            cursor = self.ctrl.conn.cursor()
            cursor.execute(
                "EXEC sp_inicioSesion @Correo=?, @Password=?",
                self.email.get(), self.password.get()
            )
            row = cursor.fetchone()
            self.ctrl.conn.commit()
            self.ctrl.user_id = row.UserID
            # Determinamos tipo de usuario para mostrar la página adecuada
            # (podrías también devolverlo desde el SP o inferirlo con otra consulta)
            self.ctrl.user_tipo = 'Cliente'  # o 'Tienda', según lógica adicional

            if self.ctrl.user_tipo == 'Cliente':
                self.ctrl.show_frame("CustomerPage")
            else:
                self.ctrl.show_frame("VendorPage")

        except Exception as e:
            messagebox.showerror("Error de login", str(e))


# ----------------- Página Cliente -----------------
class CustomerPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="¡Bienvenido, Cliente!").pack(pady=20)
        # Aquí irían tu menú de categorías, vista de productos, botones de pago...
        tk.Button(self, text="Cerrar Sesión",
                  command=lambda: controller.on_close()).pack(pady=10)


# ----------------- Página Vendedor -----------------
class VendorPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Panel del Vendedor").pack(pady=20)
        # Aquí tus botones de registrar/editar/eliminar/ver ventas...
        tk.Button(self, text="Cerrar Sesión",
                  command=lambda: controller.on_close()).pack(pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()
