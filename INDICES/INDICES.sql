-- Índices para tabla INVENTARIO
CREATE NONCLUSTERED INDEX IX_Inventario_ProductoID ON INVENTARIO (ProductoID);
CREATE NONCLUSTERED INDEX IX_Inventario_TiendaID ON INVENTARIO (TiendaID);
CREATE NONCLUSTERED INDEX IX_Inventario_SubcategoriaID ON INVENTARIO (SubcategoriaID);

-- Índices para tabla VENTAS
CREATE NONCLUSTERED INDEX IX_Ventas_ProductoID ON VENTAS (ProductoID);
CREATE NONCLUSTERED INDEX IX_Ventas_CompraID ON VENTAS (CompraID);

-- Índice para tabla PRODUCTOS
CREATE NONCLUSTERED INDEX IX_Productos_ProductoID ON PRODUCTOS (ProductoID);

-- Índices para tabla COMPRAS
CREATE NONCLUSTERED INDEX IX_Compras_ClienteID ON COMPRAS (ClienteID);
CREATE NONCLUSTERED INDEX IX_Compras_DireccionID ON COMPRAS (DireccionID);

-- Índices para tabla PAGOS
CREATE NONCLUSTERED INDEX IX_Pagos_CompraID ON PAGOS (CompraID);
CREATE NONCLUSTERED INDEX IX_Pagos_FacturaID ON PAGOS (FacturaID);

-- Índices para tabla TIENDAS
CREATE NONCLUSTERED INDEX IX_Tiendas_UserID ON TIENDAS (UserID);
CREATE NONCLUSTERED INDEX IX_Tiendas_CategoriaID ON TIENDAS (CategoriaID);

-- Índice para tabla CLIENTES
CREATE NONCLUSTERED INDEX IX_Clientes_UserID ON CLIENTES (UserID);

-- Índice para tabla USERS
CREATE NONCLUSTERED INDEX IX_Users_Tipo ON USERS (Tipo);

-- Índice para tabla DIRECCIONES
CREATE NONCLUSTERED INDEX IX_Direcciones_ClienteID ON DIRECCIONES (ClienteID);

-- Índice para tabla DATOS_FACTURA
CREATE NONCLUSTERED INDEX IX_DatosFactura_ClienteID ON DATOS_FACTURA (ClienteID);
