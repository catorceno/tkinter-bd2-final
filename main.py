import tkinter as tk
from tkinter import messagebox, ttk
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
        self.conn = pyodbc.connect(CONN_STR)
        self.user_id = None
        self.user_tipo = None  # 'Cliente' o 'Tienda'

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage,
                  RegisterClientPage,
                  RegisterStorePage,
                  LoginPage,
                  CustomerPage,
                  VendorPage):
            frame = F(parent=container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show_frame("StartPage")

    def show_frame(self, name):
        frame = self.frames[name]
        # Si el frame tiene reset(), lo limpio
        if hasattr(frame, 'reset'):
            frame.reset()
        frame.tkraise()

    def on_close(self):
        if self.user_id:
            print(">>> Cerrando sesión del user_id =", self.user_id)    # <—— agrega esto
            try:
                cur = self.conn.cursor()
                cur.execute("EXEC sp_cerrarSesion @UserID = ?", self.user_id)
                self.conn.commit()
            except Exception as e:
                print("Error al cerrar sesión:", e)
        self.conn.close()
        self.destroy()


# ----------------- StartPage -----------------
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Bienvenido, elige una opción:").pack(pady=10)
        for text, target in [
            ("Registrarme como Cliente", "RegisterClientPage"),
            ("Registrarme como Tienda", "RegisterStorePage"),
            ("Iniciar Sesión", "LoginPage"),
        ]:
            tk.Button(self, text=text,
                      command=lambda t=target: controller.show_frame(t)
            ).pack(fill="x", padx=50, pady=5)


# ----------------- RegisterClientPage -----------------
class RegisterClientPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.ctrl = controller

        tk.Label(self, text="Registrar Nuevo Cliente").pack(pady=10)
        self.email = self._labeled_entry("Correo")
        self.password = self._labeled_entry("Password", show="*")
        self.nombre = self._labeled_entry("Nombre")
        self.apellido = self._labeled_entry("Apellido")
        self.telefono = self._labeled_entry("Teléfono")

        tk.Button(self, text="Enviar", command=self.on_submit).pack(pady=5)
        tk.Button(self, text="Cancelar",
                  command=lambda: controller.show_frame("StartPage")).pack()

    def _labeled_entry(self, label, **opts):
        tk.Label(self, text=label).pack()
        ent = tk.Entry(self, **opts)
        ent.pack()
        return ent

    def reset(self):
        for widget in (self.email, self.password,
                       self.nombre, self.apellido, self.telefono):
            widget.delete(0, tk.END)

    def on_submit(self):
        try:
            cur = self.ctrl.conn.cursor()
            cur.execute(
                "EXEC sp_RegistrarNuevosClientes "
                "@Correo=?,@Password=?,@Nombre=?,@Apellido=?,@Telefono=?",
                self.email.get(), self.password.get(),
                self.nombre.get(), self.apellido.get(),
                int(self.telefono.get())
            )
            msg, uid = cur.fetchone()
            self.ctrl.conn.commit()
            messagebox.showinfo("OK", msg)
            # Auto-login parcial como Cliente:
            self.ctrl.user_id = uid
            self.ctrl.user_tipo = 'Cliente'
            self.ctrl.show_frame("CustomerPage")
        except Exception as e:
            messagebox.showerror("Error", e.args[1] if len(e.args)>1 else str(e))


# ----------------- RegisterStorePage -----------------
class RegisterStorePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.ctrl = controller

        tk.Label(self, text="Registrar Nueva Tienda").pack(pady=10)
        self.email     = self._labeled_entry("Correo")
        self.password  = self._labeled_entry("Password", show="*")
        self.nombre    = self._labeled_entry("Nombre Tienda")
        self.nombreJ   = self._labeled_entry("Razón Social")
        self.nit       = self._labeled_entry("NIT")
        self.telefono  = self._labeled_entry("Teléfono")

        # Ahora cargamos categorías desde la BD
        tk.Label(self, text="Categoría").pack()
        cur = self.ctrl.conn.cursor()
        cur.execute("SELECT CategoriaID, Nombre FROM CATEGORIAS")
        cats = cur.fetchall()  # lista de tuplas (id, nombre)
        self.cat_map = {nombre: cid for cid, nombre in cats}
        nombres = list(self.cat_map.keys())

        self.cat_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(self, textvariable=self.cat_var,
                                      values=nombres, state="readonly")
        self.cat_combo.pack()

        tk.Button(self, text="Enviar", command=self.on_submit).pack(pady=5)
        tk.Button(self, text="Cancelar",
                  command=lambda: controller.show_frame("StartPage")).pack()

    def _labeled_entry(self, label, **opts):
        tk.Label(self, text=label).pack()
        ent = tk.Entry(self, **opts)
        ent.pack()
        return ent

    def reset(self):
        for w in (self.email, self.password,
                  self.nombre, self.nombreJ,
                  self.nit, self.telefono):
            w.delete(0, tk.END)
        self.cat_var.set('')

    def on_submit(self):
        try:
            cid = self.cat_map[self.cat_var.get()]
            cur = self.ctrl.conn.cursor()
            cur.execute(
                "EXEC sp_registrarNuevaTienda "
                "@Correo=?,@Password=?,@Nombre=?,@NombreJuridico=?,"
                "@NIT=?,@Teloefono=?,@CategoriaID=?",
                self.email.get(), self.password.get(),
                self.nombre.get(), self.nombreJ.get(),
                int(self.nit.get()), int(self.telefono.get()),
                cid
            )
            msg, uid = cur.fetchone()
            self.ctrl.conn.commit()
            messagebox.showinfo("OK", msg)
            # Auto-login parcial como Tienda:
            self.ctrl.user_id = uid
            self.ctrl.user_tipo = 'Tienda'
            self.ctrl.show_frame("VendorPage")
        except Exception as e:
            messagebox.showerror("Error", e.args[1] if len(e.args)>1 else str(e))


# ----------------- LoginPage -----------------
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.ctrl = controller

        tk.Label(self, text="Iniciar Sesión").pack(pady=10)
        self.email    = self._labeled_entry("Correo")
        self.password = self._labeled_entry("Password", show="*")

        tk.Button(self, text="Entrar", command=self.on_login).pack(pady=5)
        tk.Button(self, text="Cancelar",
                  command=lambda: controller.show_frame("StartPage")).pack()

    def _labeled_entry(self, label, **opts):
        tk.Label(self, text=label).pack()
        ent = tk.Entry(self, **opts)
        ent.pack()
        return ent

    def reset(self):
        self.email.delete(0, tk.END)
        self.password.delete(0, tk.END)

    def on_login(self):
        try:
            cur = self.ctrl.conn.cursor()
            cur.execute(
                "EXEC sp_inicioSesion @Correo=?, @Password=?",
                self.email.get(), self.password.get()
            )
            (uid,) = cur.fetchone()
            self.ctrl.conn.commit()
            self.ctrl.user_id = uid
            # Determinamos tipo real de usuario
            cur.execute("SELECT Tipo FROM USERS WHERE UserID=?", uid)
            (tipo,) = cur.fetchone()
            self.ctrl.user_tipo = tipo

            if tipo == 'Cliente':
                self.ctrl.show_frame("CustomerPage")
            else:
                self.ctrl.show_frame("VendorPage")

        except Exception as e:
            messagebox.showerror("Error de login", e.args[1] if len(e.args)>1 else str(e))


# ----------------- CustomerPage -----------------
class CustomerPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="¡Bienvenido, Cliente!").pack(pady=20)
        # Aquí tu lógica de productos & pagos...
        tk.Button(self, text="Cerrar Sesión",
                  command=controller.on_close).pack(pady=10)


# ----------------- VendorPage -----------------
class VendorPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Panel del Vendedor").pack(pady=20)
        # Aquí tus botones de gestión...
        tk.Button(self, text="Cerrar Sesión",
                  command=controller.on_close).pack(pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()

"""
    def on_close(self):
        if self.user_id:
            try:
                cur = self.conn.cursor()
                cur.execute("EXEC sp_cerrarSesion @UserID = ?", self.user_id)
                self.conn.commit()
            except Exception as e:
                print("Error al cerrar sesión:", e)
""" 
