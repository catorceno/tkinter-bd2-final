--pruebas para los indices
```sql
USE Marcket_P;

-- Habilitar la visualización del plan de ejecución en texto
SET SHOWPLAN_TEXT ON;

-- 1. Pruebas para índices en INVENTARIO
-- IX_Inventario_ProductoID
SELECT ProductoID, Nombre, Precio
FROM INVENTARIO
WHERE ProductoID = 100;
-- Verifica el plan de ejecución: Debería mostrar un 'Index Seek' en IX_Inventario_ProductoID.

-- IX_Inventario_TiendaID
SELECT TiendaID, Nombre, Stock
FROM INVENTARIO
WHERE TiendaID = 50;
-- Verifica: Busca un 'Index Seek' o 'Index Scan' en IX_Inventario_TiendaID.

-- IX_Inventario_SubcategoriaID
SELECT SubcategoriaID, Nombre, Precio
FROM INVENTARIO
WHERE SubcategoriaID = 25
ORDER BY Precio;
-- Verifica: Debería usar IX_Inventario_SubcategoriaID para el filtro.

-- 2. Pruebas para índices en VENTAS
-- IX_Ventas_ProductoID
SELECT V.VentaID, V.ProductoID, V.Cantidad
FROM VENTAS V
WHERE V.ProductoID = 200;
-- Verifica: Busca un 'Index Seek' en IX_Ventas_ProductoID.

-- IX_Ventas_CompraID
SELECT V.CompraID, V.ProductoID, V.PrecioUnitario
FROM VENTAS V
JOIN COMPRAS C ON V.CompraID = C.CompraID
WHERE V.CompraID = 10;
-- Verifica: Debería usar IX_Ventas_CompraID en la condición o unión.

-- 3. Prueba para índice en PRODUCTOS
-- IX_Productos_ProductoID
SELECT P.ItemID, P.Codigo, I.Nombre
FROM PRODUCTOS P
JOIN INVENTARIO I ON P.ProductoID = I.ProductoID
WHERE P.ProductoID = 150;
-- Verifica: Busca un 'Index Seek' en IX_Productos_ProductoID.

-- 4. Pruebas para índices en COMPRAS
-- IX_Compras_ClienteID
SELECT CompraID, ClienteID, Total
FROM COMPRAS
WHERE ClienteID = 30;
-- Verifica: Debería usar IX_Compras_ClienteID para el filtro.

-- IX_Compras_DireccionID
SELECT C.CompraID, C.DireccionID, D.Barrio
FROM COMPRAS C
JOIN DIRECCIONES D ON C.DireccionID = D.DireccionID
WHERE C.DireccionID = 20;
-- Verifica: Busca un 'Index Seek' en IX_Compras_DireccionID.

-- 5. Pruebas para índices en PAGOS
-- IX_Pagos_CompraID
SELECT PagoID, CompraID, Monto
FROM PAGOS
WHERE CompraID = 40;
-- Verifica: Debería usar IX_Pagos_CompraID para el filtro.

-- IX_Pagos_FacturaID
SELECT P.PagoID, P.FacturaID, DF.RazonSocial
FROM PAGOS P
JOIN DATOS_FACTURA DF ON P.FacturaID = DF.FacturaID
WHERE P.FacturaID = 15;
-- Verifica: Busca un 'Index Seek' en IX_Pagos_FacturaID.

-- 6. Pruebas para índices en TIENDAS
-- IX_Tiendas_UserID
SELECT TiendaID, UserID, Nombre
FROM TIENDAS
WHERE UserID = 60;
-- Verifica: Debería usar IX_Tiendas_UserID para el filtro.

-- IX_Tiendas_CategoriaID
SELECT T.TiendaID, T.Nombre, C.Nombre AS Categoria
FROM TIENDAS T
JOIN CATEGORIAS C ON T.CategoriaID = C.CategoriaID
WHERE T.CategoriaID = 5;
-- Verifica: Busca un 'Index Seek' en IX_Tiendas_CategoriaID.

-- 7. Prueba para índice en CLIENTES
-- IX_Clientes_UserID
SELECT ClienteID, UserID, Nombre, Apellido
FROM CLIENTES
WHERE UserID = 70;
-- Verifica: Debería usar IX_Clientes_UserID para el filtro.

-- 8. Prueba para índice en USERS
-- IX_Users_Tipo
SELECT UserID, Correo, Tipo
FROM USERS
WHERE Tipo = 'Cliente'
ORDER BY Correo;
-- Verifica: Debería usar IX_Users_Tipo para el filtro.

```