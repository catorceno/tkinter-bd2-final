import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from tkinter import ttk, messagebox
import pyodbc
from PIL import Image, ImageTk
from decimal import Decimal
from datetime import datetime

import guardar as guardar
import recuperar as recuperar
import editar as editar
import eliminar as eliminar

# ----------------- Configuración DB -----------------
CONN_STR = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=DESKTOP-6L6ASHP\\SQLEXPRESS;"
    "Database=TkMarketplace;"
    "Trusted_Connection=yes;"
)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mi Marketplace")
        self.conn = pyodbc.connect(CONN_STR)
        self.user_id = None
        self.user_tipo = None
        self.tienda_id = None

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
                  RegisterCardPage,
                  PaymentPage,
                  VendorPage,
                  RegisterProductPage,
                  EditProductPage):
            frame = F(parent=container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show_frame("StartPage")

    def show_frame(self, name):
        frame = self.frames[name]

        # Si vamos a VendorPage, cargamos el nombre de la tienda
        if name == "VendorPage" and self.user_tipo == 'Tienda' and self.tienda_id:
            cur = self.conn.cursor()
            cur.execute("SELECT Nombre FROM TIENDAS WHERE TiendaID = ?", self.tienda_id)
            row = cur.fetchone()
            self.tienda_nombre = row[0] if row else "tu Tienda"

        # Si vamos a CustomerPage, cargamos el nombre del cliente
        if name == "CustomerPage" and self.user_tipo == 'Cliente' and self.user_id:
            cur = self.conn.cursor()
            cur.execute("SELECT Nombre FROM CLIENTES WHERE ClienteID = ?", self.user_id)
            row = cur.fetchone()
            self.cliente_nombre = row[0] if row else "Cliente"

        if hasattr(frame, 'reset'):
            frame.reset()

        frame.tkraise()
        if name == "VendorPage" and self.user_tipo == 'Tienda' and self.user_id:
            try:
                frame.refresh_inventory()
            except Exception as e:
                print("Error cargando inventario:", e)

    def on_close(self):
        if self.user_id:
            try:
                cur = self.conn.cursor()
                cur.execute("EXEC sp_cerrarSesion @UserID = ?", self.user_id)
                self.conn.commit()
            except Exception:
                pass
        self.conn.close()
        self.destroy()
        
class PaymentPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.ctrl = controller

        tk.Label(self, text="Confirmar Pago", font=("Arial", 16)).pack(pady=10)

        # Resumen
        self.subtotal_var = tk.DoubleVar()
        self.fee_var      = tk.DoubleVar()
        self.total_var    = tk.DoubleVar()
        for lbl, var in [("Subtotal", self.subtotal_var),
                         ("Service fee", self.fee_var),
                         ("Total", self.total_var)]:
            row = tk.Frame(self)
            tk.Label(row, text=lbl + ":").pack(side="left")
            tk.Label(row, textvariable=var).pack(side="right")
            row.pack(fill="x", padx=20, pady=5)

        # Tarjetas del cliente
        tk.Label(self, text="Selecciona Tarjeta:").pack(pady=(20,0))
        self.card_var = tk.StringVar()
        self.card_combo = ttk.Combobox(self, textvariable=self.card_var, state="readonly")
        self.card_combo.pack(fill="x", padx=20, pady=5)

        # Botones
        btns = tk.Frame(self)
        tk.Button(btns, text="Cancelar",
                  command=lambda: controller.show_frame("CustomerPage")).pack(side="left", padx=10)
        tk.Button(btns, text="Comprar Ahora", command=self.on_pay).pack(side="right", padx=10)
        btns.pack(pady=20)

    def reset(self):
        # Al mostrar la página, cargamos las tarjetas y actualizamos totales
        cur = self.ctrl.conn.cursor()
        cur.execute("SELECT TarjetaID, NombreTitular + ' • ' + CAST(Numero AS VARCHAR(16)) FROM TARJETAS WHERE ClienteID = ? AND Estado = 'Activo'",
                    self.ctrl.user_id)
        cards = cur.fetchall()
        self.card_map = {f"{titular}": tid for tid, titular in cards}
        self.card_combo['values'] = list(self.card_map.keys())
        self.card_var.set('')

        # Totales desde la página CustomerPage
        cust = self.ctrl.frames['CustomerPage']
        self.subtotal_var.set(cust.subtotal_var.get())
        self.fee_var.set(cust.fee_var.get())
        self.total_var.set(cust.total_var.get())

    def on_pay(self):
        if not self.card_var.get():
            messagebox.showwarning("Tarjeta", "Selecciona una tarjeta para pagar.")
            return

        tid = self.card_map[self.card_var.get()]
        cust = self.ctrl.frames['CustomerPage']
        cliente_id   = self.ctrl.user_id
        direccion_id = None
        subtotal     = Decimal(str(cust.subtotal_var.get()))
        fee          = Decimal(str(cust.fee_var.get()))
        total        = Decimal(str(cust.total_var.get()))

        try:
            cur = self.ctrl.conn.cursor()

            # 1) Crear compra
            cur.execute(
                "EXEC dbo.sp_procesoVenta "
                "@ClienteID=?, @DireccionID=?, @Subtotal=?, @ServiceFee=?, @Total=?",
                cliente_id, direccion_id, subtotal, fee, total
            )
            row = cur.fetchone()
            compra_id = row.CompraID if hasattr(row, 'CompraID') else row[1]

            # 2) Detalles de venta
            for pid, ent in cust.cart.items():
                cantidad = ent['qty']
                precio_u = Decimal(str(ent['info']['Precio']))
                cur.execute(
                    "INSERT INTO VENTAS(CompraID, ProductoID, Cantidad, PrecioUnitario) VALUES (?,?,?,?)",
                    compra_id, pid, cantidad, precio_u
                )

                # ↓ DESCUESTA STOCK ↓
                cur.execute(
                    "UPDATE INVENTARIO SET Stock = Stock - ? WHERE ProductoID = ?",
                    cantidad, pid
                )

            # 3) Registro de pago
            cur.execute(
                "INSERT INTO PAGOS(CompraID, TarjetaID, MetodoPago, Monto) VALUES (?,?, 'Tarjeta', ?)",
                compra_id, tid, total
            )

            self.ctrl.conn.commit()

            messagebox.showinfo("¡Listo!",
                                f"Compra #{compra_id} y pago registrados correctamente.")
            cust.cart.clear()
            cust.refresh_cart_ui()
            self.ctrl.show_frame("CustomerPage")

        except Exception as e:
            self.ctrl.conn.rollback()
            messagebox.showerror("Error al pagar", str(e))

# ----------------- PÁGINA DE REGISTRO DE TARJETA -----------------
class RegisterCardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.ctrl = controller
        tk.Label(self, text="Registrar Tarjeta", font=("Arial", 16)).pack(pady=10)

        # Red (Visa / MasterCard)
        tk.Label(self, text="Red").pack()
        self.red_var = tk.StringVar()
        ttk.Combobox(self, textvariable=self.red_var,
                     values=["Visa", "MasterCard"], state="readonly").pack(pady=5)

        # Nombre del titular
        tk.Label(self, text="Nombre del Titular").pack()
        self.titular = tk.Entry(self)
        self.titular.pack(pady=5)

        # Número de tarjeta
        tk.Label(self, text="Número de Tarjeta").pack()
        self.numero = tk.Entry(self)
        self.numero.pack(pady=5)

        # CVC
        tk.Label(self, text="CVC").pack()
        self.cvc = tk.Entry(self)
        self.cvc.pack(pady=5)

        # Fecha de expiración (YYYY-MM)
        tk.Label(self, text="Fecha de Expiración (YYYY-MM)").pack()
        exp_frame = tk.Frame(self)
        tk.Label(exp_frame, text="Año").grid(row=0, column=0)
        self.exp_yyyy = tk.Entry(exp_frame, width=6)
        self.exp_yyyy.grid(row=1, column=0)
        tk.Label(exp_frame, text="Mes").grid(row=0, column=1)
        self.exp_mm = tk.Entry(exp_frame, width=4)
        self.exp_mm.grid(row=1, column=1)
        exp_frame.pack(pady=5)

        # Botones
        btn_frame = tk.Frame(self)
        tk.Button(btn_frame, text="Cancelar",
                  command=lambda: controller.show_frame("CustomerPage")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Guardar y Pagar", command=self.on_submit).pack(side="left")
        btn_frame.pack(pady=20, fill="x")

    def reset(self):
        self.red_var.set("")
        self.titular.delete(0, tk.END)
        self.numero.delete(0, tk.END)
        self.cvc.delete(0, tk.END)
        self.exp_yyyy.delete(0, tk.END)
        self.exp_mm.delete(0, tk.END)

    def on_submit(self):
        try:
            cliente_id = self.ctrl.user_id
            red = self.red_var.get()
            titular = self.titular.get()
            numero = int(self.numero.get())
            cvc = int(self.cvc.get())
            exp_date = f"{self.exp_yyyy.get()}-{self.exp_mm.get()}-01"

            cur = self.ctrl.conn.cursor()
            cur.execute(
                "EXEC usp_RegistrarTarjeta @ClienteID=?, @Red=?, @NombreTitular=?, @Numero=?, @CVC=?, @ExpDate=?",
                cliente_id, red, titular, numero, cvc, exp_date
            )
            mensaje, tarjeta_id = cur.fetchone()
            self.ctrl.conn.commit()

            messagebox.showinfo("Éxito", mensaje)
            # Tras registrar tarjeta, procedemos al pago
            # self.ctrl.frames['CustomerPage'].checkout(finalizar=True)
            self.ctrl.show_frame("PaymentPage")
        except Exception as e:
            messagebox.showerror("Error al registrar tarjeta", str(e))

# ----------------- StartPage -----------------
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Bienvenido, elige como quieres ingresar:").pack(pady=10)
        for text, target in [
            ("Iniciar Sesión", "LoginPage"),
            ("Registrarme como Cliente", "RegisterClientPage"),
            ("Registrar mi Tienda", "RegisterStorePage"),
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
        self.password = self._labeled_entry("Contraseña", show="*")
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
            row = cur.fetchone()
            self.ctrl.conn.commit()
         
            mensaje    = row[0]           # mensaje
            user_id    = int(row[1])     # UserID retornado por el SP

            # ***** Aquí conviertes UserID → ClienteID *****
            cur.execute(
                "SELECT ClienteID FROM CLIENTES WHERE UserID = ?",
                user_id
            )
            cl_row = cur.fetchone()
            if not cl_row:
                raise RuntimeError("No se encontró el ClienteID correspondiente al nuevo usuario.")
            cliente_id = int(cl_row[0])

            # Guardas el ClienteID (no el UserID)
            self.ctrl.user_id   = cliente_id
            self.ctrl.user_tipo = 'Cliente'

            print(f">>> Nuevo cliente registrado. user_id={cliente_id}")  # para debug
            messagebox.showinfo("OK", mensaje)

            # **Aquí** guardas el nuevo ID
            self.ctrl.user_id = cliente_id
            self.ctrl.user_tipo = 'Cliente'
            self.ctrl.show_frame("CustomerPage")

        except Exception as e:
            messagebox.showerror("Error", str(e))

# ----------------- RegisterStorePage -----------------
class RegisterStorePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.ctrl = controller

        tk.Label(self, text="Registrar Nueva Tienda").pack(pady=10)
        self.email     = self._labeled_entry("Correo electrónico")
        self.password  = self._labeled_entry("Contraseña", show="*")
        self.nombre    = self._labeled_entry("Marca de tu tienda")
        self.nombreJ   = self._labeled_entry("Nombre jurídico de tu tienda")
        self.nit       = self._labeled_entry("NIT")
        self.telefono  = self._labeled_entry("Telefono")

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
            # 1) Llamas a tu SP, que retorna el @UserID
            msg, user_id = cur.fetchone()
            self.ctrl.conn.commit()

            # 2) Ahora recuperas el TiendaID real:
            cur.execute("SELECT TiendaID FROM TIENDAS WHERE UserID = ?", user_id)
            row = cur.fetchone()
            if not row:
                raise RuntimeError("No se encontró la tienda recién creada")
            tienda_id = row[0]

            # 3) Guardas ambos
            self.ctrl.user_id   = user_id    # para tu lógica de sesiones
            self.ctrl.tienda_id = tienda_id  # para inventario/productos
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
        self.password = self._labeled_entry("Contraseña", show="*")

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
            # else:
            #     self.ctrl.show_frame("VendorPage")
            if tipo == 'Tienda':
                # después de que ya hiciste self.ctrl.user_id = uid
                cur.execute("SELECT TiendaID FROM TIENDAS WHERE UserID = ?", uid)
                row = cur.fetchone()
                self.ctrl.tienda_id = row[0] if row else None
                self.ctrl.show_frame("VendorPage")

        except Exception as e:
            messagebox.showerror("Error de login", e.args[1] if len(e.args)>1 else str(e))

# ----------------- CustomerPage -----------------
class CustomerPage(tk.Frame):
    SERVICE_FEE_RATE = 0.02  # 2%

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.ctrl = controller
        self.cart = {}  # { producto_id: {info: prod_dict, qty: int} }

        # ————— Bienvenida —————
        cliente = controller.cliente_nombre if hasattr(controller, 'cliente_nombre') else "Cliente"
        tk.Label(self, text=f"¡Bienvenido, {cliente}!", font=("Arial", 16)) \
          .grid(row=0, column=0, columnspan=2, pady=(10,5), sticky="ew")

        # ————— Cabecera botones —————
        header = tk.Frame(self)
        tk.Button(header, text="Productos Random ▼", command=self.load_random) \
           .pack(side="left", padx=5)
        tk.Button(header, text="Categorías ▼", command=self.toggle_categories) \
           .pack(side="left", padx=5)
        tk.Button(header, text="Mi Carrito 🛒", command=self.toggle_cart) \
           .pack(side="right", padx=5)
        header.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        # ————— Panel Categorías/Subcats —————
        self.cat_frame = tk.Frame(self, bd=1, relief="solid", padx=5, pady=5)
        # Categorías
        tk.Label(self.cat_frame, text="Categoría").grid(row=0, column=0, sticky="w")
        self.cat_var = tk.StringVar()
        self.cat_cb  = ttk.Combobox(self.cat_frame, textvariable=self.cat_var, state="readonly")
        self.cat_cb.grid(row=0, column=1, sticky="ew", padx=5)
        # Subcategorías
        tk.Label(self.cat_frame, text="Subcategoría").grid(row=1, column=0, sticky="w")
        self.sub_var = tk.StringVar()
        self.sub_cb  = ttk.Combobox(self.cat_frame, textvariable=self.sub_var, state="readonly")
        self.sub_cb.grid(row=1, column=1, sticky="ew", padx=5)
        tk.Button(self.cat_frame, text="Ver Productos", command=self.load_products) \
           .grid(row=2, column=0, columnspan=2, pady=5)
        self.cat_frame.grid_columnconfigure(1, weight=1)
        self.cat_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        self.cat_frame.grid_remove()

        # ————— Configuración del grid principal —————
        self.grid_columnconfigure(0, weight=4)  # productos
        self.grid_columnconfigure(1, weight=1)  # carrito
        self.grid_rowconfigure(3, weight=1)

        # ————— Panel Productos (columna 0) —————
        self.prod_container = tk.Frame(self)
        # canvas + scrollbar dentro de prod_container
        canvas = tk.Canvas(self.prod_container, height=300)
        scroll = tk.Scrollbar(self.prod_container, orient="vertical", command=canvas.yview)
        self.prod_frame = tk.Frame(canvas)
        self.prod_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0,0), window=self.prod_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.prod_container.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)

        # ————— Sidebar Carrito (columna 1) —————
        self.cart_frame = tk.Frame(self, bd=2, relief="ridge")
        self.cart_items_frame = tk.Frame(self.cart_frame)
        self.cart_items_frame.pack(fill="both", expand=True, pady=5)
        self.subtotal_var = tk.DoubleVar(value=0.0)
        self.fee_var      = tk.DoubleVar(value=0.0)
        self.total_var    = tk.DoubleVar(value=0.0)
        tot = tk.Frame(self.cart_frame)
        for lbl, var in [("Subtotal", self.subtotal_var),
                         ("Service fee", self.fee_var),
                         ("Total", self.total_var)]:
            tk.Label(tot, text=lbl).pack(anchor="w")
            tk.Label(tot, textvariable=var).pack(anchor="e", pady=(0,5))
        tot.pack(fill="x", padx=5)
        tk.Button(self.cart_frame, text="Realizar pago", command=self.checkout).pack(pady=10)
        self.cart_frame.grid(row=3, column=1, sticky="ns", padx=5, pady=5)
        self.cart_frame.grid_remove()

        # Cargo datos iniciales
        self.load_categories()
        self.load_random()


    def toggle_categories(self):
        if self.cat_frame.winfo_ismapped():
            self.cat_frame.grid_remove()
        else:
            self.cat_frame.grid()

    def toggle_cart(self):
        if self.cart_frame.winfo_ismapped():
            self.cart_frame.grid_remove()
        else:
            self.cart_frame.grid()

    def load_categories(self):
        # Cargo combobox categorías
        cur = self.ctrl.conn.cursor()
        cur.execute("SELECT CategoriaID, Nombre FROM CATEGORIAS")
        cats = cur.fetchall()
        self.cat_map = {nombre: cid for cid, nombre in cats}
        self.cat_cb['values'] = list(self.cat_map.keys())

        # Cuando cambie categoría, recargo subcategorías
        def on_cat_select(*_):
            cid = self.cat_map[self.cat_var.get()]
            cur.execute("SELECT SubcategoriaID, Nombre FROM SUBCATEGORIAS WHERE CategoriaID=?", cid)
            subs = cur.fetchall()
            self.sub_map = {nombre: sid for sid, nombre in subs}
            self.sub_cb['values'] = list(self.sub_map.keys())
            self.sub_var.set('')

        self.cat_cb.bind("<<ComboboxSelected>>", on_cat_select)

    def load_random(self):
        # Vista RandomProductsByStoreView
        cur = self.ctrl.conn.cursor()
        cur.execute("SELECT ProductoID, NombreTienda, NombreSubcategoria, NombreProducto, Precio "
                    "FROM RandomProductsByStoreView")
        cols = [c[0] for c in cur.description]
        rows = cur.fetchall()
        self._show_products([dict(zip(cols, r)) for r in rows])

    def load_products(self):
        # Llama a usp_BuscarPorSubcategoria con ID
        sel = self.sub_var.get()
        if not sel:
            messagebox.showwarning("Aviso", "Elija primero una subcategoría")
            return
        sid = self.sub_map[sel]
        cur = self.ctrl.conn.cursor()
        cur.execute("EXEC usp_BuscarPorSubcategoria @SubcategoriaID = ?", sid)
        cols = [c[0] for c in cur.description]
        rows = cur.fetchall()
        prods = [dict(zip(cols, r)) for r in rows]
        # puede venir un mensaje si no hay filas
        if len(prods)==1 and 'Mensaje' in prods[0]:
            messagebox.showinfo("Resultado", prods[0]['Mensaje'])
            return
        self._show_products(prods)

    def _show_products(self, products):
        for w in self.prod_frame.winfo_children():
            w.destroy()
        for i, prod in enumerate(products):
            card = tk.Frame(self.prod_frame, bd=1, relief="raised", padx=10, pady=5)
            img = recuperar.recuperar_imagen(prod['ProductoID'])
            thumb = img.resize((80,80))
            tkimg = ImageTk.PhotoImage(thumb)
            lbl = tk.Label(card, image=tkimg); lbl.image = tkimg
            lbl.pack()
            tk.Label(card, text=prod['NombreProducto']).pack()
            tk.Label(card, text=f"Bs. {prod['Precio']}").pack()
            tk.Button(card, text="Agregar",
                      command=lambda p=prod: self.add_to_cart(p)).pack(pady=5)
            card.grid(row=i//3, column=i%3, padx=5, pady=5)

    def add_to_cart(self, prod):
        pid = prod['ProductoID']
        if pid not in self.cart:
            self.cart[pid] = {'info': prod, 'qty': 0}
        self.cart[pid]['qty'] += 1
        self.refresh_cart_ui()

    def change_qty(self, pid, delta):
        ent = self.cart[pid]
        ent['qty'] = max(0, ent['qty'] + delta)
        if ent['qty']==0:
            del self.cart[pid]
        self.refresh_cart_ui()

    def refresh_cart_ui(self):
        for w in self.cart_items_frame.winfo_children():
            w.destroy()
        subtotal = 0
        for pid, ent in self.cart.items():
            prod, qty = ent['info'], ent['qty']
            frame = tk.Frame(self.cart_items_frame, bd=1, relief="solid", padx=5, pady=5)
            tk.Label(frame, text=prod['NombreProducto']).grid(row=0, column=0, columnspan=3)
            tk.Button(frame, text="-", command=lambda p=pid: self.change_qty(p,-1)).grid(row=1, column=0)
            tk.Label(frame, text=str(qty)).grid(row=1, column=1)
            tk.Button(frame, text="+", command=lambda p=pid: self.change_qty(p,+1)).grid(row=1, column=2)
            tk.Label(frame, text=f"Bs. {prod['Precio']}").grid(row=2, column=0, columnspan=3)
            frame.pack(fill="x", pady=3)
            subtotal += prod['Precio'] * qty
            
        subtotal = float(subtotal)

        fee   = round(subtotal * self.SERVICE_FEE_RATE, 2)
        total = round(subtotal + fee, 2)
        self.subtotal_var.set(subtotal)
        self.fee_var.set(fee)
        self.total_var.set(total)

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Carrito vacío", "Agrega algo antes de pagar.")
            return

        # 1) ¿Tiene tarjetas registradas?
        cur = self.ctrl.conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM TARJETAS WHERE ClienteID = ? AND Estado = 'Activo'",
            self.ctrl.user_id
        )
        (cnt,) = cur.fetchone()

        if cnt == 0:
            # Si no, vamos directo al registro de tarjeta
            self.ctrl.show_frame("RegisterCardPage")
        else:
            # Si sí, a la página de pago normal
            self.ctrl.show_frame("PaymentPage")

# ----------------- RegisterProductPage -----------------
class RegisterProductPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.ctrl = controller
        tk.Label(self, text="Registrar Nuevo Producto").pack(pady=10)
        # Subcategorías
        tk.Label(self, text="Subcategoría").pack()
        cur = self.ctrl.conn.cursor()
        cur.execute("SELECT SubcategoriaID, Nombre FROM SUBCATEGORIAS")
        subs = cur.fetchall()
        self.sub_map = {nombre: sid for sid, nombre in subs}
        self.sub_var = tk.StringVar()
        ttk.Combobox(self, textvariable=self.sub_var,
                     values=list(self.sub_map.keys()), state="readonly").pack()
        # Campos básicos
        self.nombre = self.labeled_entry("Nombre")
        self.precio = self.labeled_entry("Precio")
        self.stock  = self.labeled_entry("Stock")
        self.desc   = self.labeled_entry("Descripción")
        # Imagen
        tk.Button(self, text="Seleccionar imagen...", command=self.load_image).pack(pady=5)
        self.img_path = None
        # Botones
        btns = tk.Frame(self)
        tk.Button(btns, text="Guardar", command=self.on_submit).pack(side="left", padx=5)
        tk.Button(btns, text="Cancelar", command=lambda: controller.show_frame("VendorPage")).pack(side="left")
        btns.pack(pady=10)

    def labeled_entry(self, label):
        tk.Label(self, text=label).pack()
        e = tk.Entry(self)
        e.pack()
        return e

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("JPG", "*.jpg"),("PNG","*.png")])
        if path:
            self.img_path = path
            messagebox.showinfo("Imagen", f"Imagen seleccionada:\n{path}")

    def on_submit(self):
        try:
            cur = self.ctrl.conn.cursor()
            cur.execute(
                "EXEC sp_RegistrarNuevoProducto "
                "@TiendaID=?, @SubcategoriaID=?, @DescuentoID=?, "
                "@Nombre=?, @Precio=?, @Descripcion=?, @Stock=?",
                # self.ctrl.user_id,
                self.ctrl.tienda_id,
                self.sub_map[self.sub_var.get()],
                None,
                self.nombre.get(),
                float(self.precio.get()),
                self.desc.get(),
                int(self.stock.get())
            )
            # registrar nuevo producto
            msg, pid = cur.fetchone()
            self.ctrl.conn.commit()

            # guardar la imagen con la clave producto_id
            if self.img_path:
                guardar.guardar_imagen(self.img_path, pid)

            messagebox.showinfo("OK", msg)
            self.ctrl.show_frame("VendorPage")    
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def reset(self):
        for w in (self.sub_var, self.nombre, self.precio, self.stock, self.desc):
            try: w.set('') 
            except: w.delete(0, tk.END)
        self.img_path = None


# ----------------- EditProductPage -----------------
class EditProductPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.ctrl = controller
        tk.Label(self, text="Editar Producto").pack(pady=10)
        # ProductoID oculto
        self.prod_id = None

        # Reutilizamos combobox de subcategorías
        tk.Label(self, text="Subcategoría").pack()
        cur = self.ctrl.conn.cursor()
        cur.execute("SELECT SubcategoriaID, Nombre FROM SUBCATEGORIAS")
        subs = cur.fetchall()
        self.sub_map = {nombre: sid for sid, nombre in subs}
        self.sub_var = tk.StringVar()
        ttk.Combobox(self, textvariable=self.sub_var,
                     values=list(self.sub_map.keys()), state="readonly").pack()

        self.nombre = self.labeled_entry("Nombre")
        self.precio = self.labeled_entry("Precio")
        self.desc   = self.labeled_entry("Descripción")

        # --------------------------------------------
        # preview de la imagen actual
        self.preview_lbl = tk.Label(self)
        self.preview_lbl.pack(pady=5)
        # ---------------------------------------------

        # Imagen (opcional)
        tk.Button(self, text="Cambiar imagen...", command=self.load_image).pack(pady=5)
        self.img_path = None

        btns = tk.Frame(self)
        tk.Button(btns, text="Actualizar", command=self.on_submit).pack(side="left", padx=5)
        tk.Button(btns, text="Cancelar", command=lambda: controller.show_frame("VendorPage")).pack(side="left")
        btns.pack(pady=10)

    def labeled_entry(self, label):
        tk.Label(self, text=label).pack()
        e = tk.Entry(self)
        e.pack()
        return e

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("JPG", "*.jpg"),("PNG","*.png")])
        if path:
            self.img_path = path
            messagebox.showinfo("Imagen", f"Imagen seleccionada:\n{path}")

    def load_product(self, producto):
        self.prod_id = producto["ProductoID"]
        self.sub_var.set(producto["Subcategoria"])
        self.nombre.delete(0, tk.END); self.nombre.insert(0, producto["Nombre"])
        self.precio.delete(0, tk.END); self.precio.insert(0, producto["Precio"])
        self.desc.delete(0, tk.END);   self.desc.insert(0, producto["Descripcion"])
        # self.stock.delete(0, tk.END);  self.stock.insert(0, producto["Stock"])

        # cargar y mostrar imagen actual
        img = recuperar.recuperar_imagen(self.prod_id)
        thumb = img.resize((120,120))
        self.tkthumb = ImageTk.PhotoImage(thumb)
        self.preview_lbl.config(image=self.tkthumb)

    def on_submit(self):
        try:
            # Si cambiaron imagen, la guardamos
            if self.img_path:
                # guardar.guardar_imagen(self.img_path)
                editar.editar_imagen(self.prod_id, self.img_path)
            print("Debug – voy a editar ProductoID =", self.prod_id)

            cur = self.ctrl.conn.cursor()
            cur.execute(
                "EXEC sp_EditarProducto "
                "@ProductoID=?, @SubcategoriaID=?, @Nombre=?, "
                "@Precio=?, @Descripcion=?, @DescuentoID=?",
                self.prod_id,
                self.sub_map[self.sub_var.get()],
                self.nombre.get(),
                float(self.precio.get()),
                self.desc.get(),
                None
            )
            # Sólo un campo de salida (Mensaje)
            mensaje, = cur.fetchone()
            self.ctrl.conn.commit()

            messagebox.showinfo("OK", mensaje)
            self.ctrl.show_frame("VendorPage")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def reset(self):
        self.prod_id = None
        self.sub_var.set('')
        for w in (self.nombre, self.precio, self.desc):
            w.delete(0, tk.END)
        self.img_path = None

# ----------------- VendorPage -----------------
class VendorPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.ctrl = controller

        header = tk.Frame(self)
        tienda = controller.tienda_nombre if hasattr(controller, 'tienda_nombre') else "tu Tienda"
        tk.Label(header,
                text=f"¡Bienvenido a tu panel de control!",
                font=("Arial", 16)
        ).pack(side="left", padx=10)
        tk.Button(header, text="Registrar producto",
                  command=lambda: controller.show_frame("RegisterProductPage")).pack(side="left", padx=5)
        tk.Button(header, text="Ver mis ventas", command=self.ver_ventas).pack(side="left", padx=5)
        tk.Button(header, text="Cerrar Sesión", command=controller.on_close).pack(side="right", padx=10)
        header.pack(fill="x", pady=10)

        # Frame scrollable para inventario
        container = tk.Frame(self, bd=2, relief="sunken")
        canvas = tk.Canvas(container, height=400)
        scroll = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.list_frame = tk.Frame(canvas)

        self.list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0,0), window=self.list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Se cargará al mostrar
        # self.bind("<Visibility>", lambda e: self.refresh_inventory())

    def refresh_inventory(self):
        # limpia tarjetas previas
        for w in self.list_frame.winfo_children():
            w.destroy()

        cur = self.ctrl.conn.cursor()
        cur.execute("EXEC sp_verInventario @TiendaID=?", self.ctrl.tienda_id)

        cols = [col[0] for col in cur.description]
        for row in cur.fetchall():
            prod = dict(zip(cols, row))
            print("DEBUG prod keys:", prod.keys())
            print("DEBUG prod ProductoID raw:", prod.get("ProductoID"))
            card = tk.Frame(self.list_frame, bd=1, relief="raised", padx=10, pady=5)
            """
            """
            # —— Imagen con fallback —— 
            try:
                img = recuperar.recuperar_imagen(prod['ProductoID'])
                imgtk = ImageTk.PhotoImage(img.resize((80,80)))
            except Exception as ex:
                # si algo falla, usamos un placeholder en blanco
                placeholder = Image.new('RGB', (80,80), (240,240,240))
                imgtk = ImageTk.PhotoImage(placeholder)

            lbl_img = tk.Label(card, image=imgtk)
            lbl_img.image = imgtk
            lbl_img.pack(side="left")

            # —— Resto de info —— 
            info = tk.Frame(card)
            for k in ("Nombre","Categoria","Subcategoria","Precio","Stock","Descripcion"):
                tk.Label(info, text=f"{k}: {prod.get(k)}").pack(anchor="w")
            btns = tk.Frame(info)
            tk.Button(btns, text="Editar",
                      command=lambda p=prod: self._edit(p)).pack(side="left", padx=5)
            tk.Button(btns, text="Eliminar",
                      command=lambda pid=prod['ProductoID']: self._delete(pid)).pack(side="left")
            btns.pack(pady=5)
            info.pack(side="left", padx=10)

            card.pack(fill="x", pady=5)

    def _edit(self, prod):
        page = self.ctrl.frames["EditProductPage"]
        self.ctrl.show_frame("EditProductPage")
        page.load_product(prod)

    def _delete(self, pid):
        if messagebox.askyesno("Confirmar", "¿Descontinuar este producto?"):
            cur = self.ctrl.conn.cursor()
            cur.execute(
                "EXEC sp_EliminarProducto @TiendaID=?, @ProductoID=?", 
                self.ctrl.tienda_id,  # antes pusiste user_id aquí
                pid
            )
            from eliminar import eliminar_imagen
            eliminar_imagen(pid)

            msg, = cur.fetchone()
            self.ctrl.conn.commit()
            messagebox.showinfo("OK", msg)
            self.refresh_inventory()

    def ver_ventas(self):
        # crea ventana o frame para mostrar la tabla
        ventas_win = tk.Toplevel(self)
        ventas_win.title("Ventas - Top 10 productos")

        # Treeview para top10
        cols = ("Producto", "CantidadVendida", "PrecioUnitario", "Ingresos", "Categoria", "Subcategoria")
        tree = ttk.Treeview(ventas_win, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center")
        tree.pack(fill="both", expand=True)

        # consulta SP
        cur = self.ctrl.conn.cursor()
        cur.execute("EXEC sp_verProductosMasVendidosTop10 @TiendaID=?", self.ctrl.tienda_id)
        # dentro de ver_ventas (y análogo en _ver_todas):
        for row in cur.fetchall():
            # row es tupla: (VentaID, CompraID, ...)
            display = []
            for cell in row:
                if isinstance(cell, Decimal):
                    # saca la parte numérica sin paréntesis
                    display.append(f"{float(cell):.2f}")
                elif isinstance(cell, datetime):
                    # fecha limpia YYYY-MM-DD
                    display.append(cell.strftime("%Y-%m-%d"))
                else:
                    display.append(str(cell))
            # ahora insertamos la fila formateada
            tree.insert("", "end", values=tuple(display))

        # botón para ver todas las ventas
        btn_all = tk.Button(ventas_win, text="Ver todas las ventas", command=lambda: self._ver_todas(ventas_win))
        btn_all.pack(pady=10)

    def _ver_todas(self, parent_win):
        # nueva ventana para todas las ventas
        win = tk.Toplevel(self)
        win.title("Todas las Ventas de la Tienda")

        cols = ("VentaID", "CompraID", "ProductoID", "Producto", "Cantidad", "PrecioUnitario", "OrderDate", "ShipDate", "TotalVenta")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center")
        tree.pack(fill="both", expand=True)

        cur = self.ctrl.conn.cursor()
        cur.execute("EXEC sp_verTodasVentasDeTienda @TiendaID=?", self.ctrl.tienda_id)
        for row in cur.fetchall():
            tree.insert("", "end", values=row)

        # cerrar ventana principal de top10 si aún abierta
        parent_win.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
