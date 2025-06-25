--ESTOS SON LOS INSRTS DE NUESTRA BASE DE DATOS ACTUALIZADA 15/06/2025

USE Tienda;
GO




-- 1. USERS
INSERT INTO USERS (Correo, Password, Tipo)
VALUES
    ('cliente1@example.com', 'pass123', 'Cliente'),
    ('tienda1@example.com', 'pass123', 'Tienda'),
    ('cliente2@example.com', 'pass123', 'Cliente'),
    ('tienda2@example.com', 'pass123', 'Tienda'),
    ('cliente3@example.com', 'pass123', 'Cliente');
-- UserID: 1 al 5

-- 2. CLIENTES
INSERT INTO CLIENTES (UserID, Nombre, Apellido, Telefono)
VALUES
    (1, 'Juan', 'Pérez', 12345678),
    (3, 'María', 'Gómez', 87654321),
    (5, 'Carlos', 'López', 11223344),
    (1, 'Ana', 'Martínez', 22334455),
    (3, 'Luis', 'Rodríguez', 33445566);
-- ClienteID: 1 al 5


--------------- TABLAS FIJAS - CATEGORIAS ---------------
-- 1.Categorias
SELECT * FROM CATEGORIAS
INSERT INTO CATEGORIAS(Nombre)
VALUES
	('Tecnolog a'),
	('Ropa y accesorios'),
	('Hogar y Jard n'),
	('Electrodom sticos'),
	('Cuidado Personal y Belleza'),
	('Entretenimiento'),
	('Mascotas'),
	('Otro');
GO

-- 2.Subcategorias
SELECT * FROM SUBCATEGORIAS
INSERT INTO SUBCATEGORIAS(CategoriaID, Nombre)
VALUES
	(1, 'Celulares'),
	(1, 'Accesorios para celulares'),
	(1, 'Laptops'),
	(1, 'PC de Escritorio'),
	(1, 'Accesorios de computo'),
	(1, 'Tablets'),
	(1, 'Smartwatches'),
	(1, 'Impresoras'),
	(1, 'Televisores'),
	(1, 'Consolas'),
	(1, 'Proyectores de Video'),
	(1, 'Parlantes'),
	(1, 'Audio Personal'),
	(1, 'Otros'),

	(2, 'Bolsos y Equipaje'),
	(2, 'Joyas'),
	(2, 'Accesorios'),
	(2, 'Calzados'),
	(2, 'Trajes de Ba o'),
	(2, 'Ropa para Mujer'),
	(2, 'Ropa para Hombre'),
	(2, 'Ropa para Ni os'),
	(2, 'Ropa deportiva'),
	(2, 'Otros'),
	
	(3, 'Muebles'),
	(3, 'Decoraci n'),
	(3, 'Jardiner a'),
	(3, 'Limpieza'),
	(3, 'Herramientas'),
	(3, 'Cama y colchones'),
	(3, 'Otros'),

	(4, 'Climatizaci n'),
	(4, 'Cocinas y Encimeras'),
	(4, 'Refrigeraci n'),
	(4, 'Hornos y Microondas'),
	(4, 'Lavadoras y Secadoras'),
	(4, 'Extractores'),
	(4, 'Parrillas El ctricas'),
	(4, 'Electrodom sticos Peque os'),
	(4, 'Otros'),

	(5, 'Cuidado Corporal'),
	(5, 'Cuidado de la Piel'),
	(5, 'Maquillaje'),
	(5, 'Planchas'),
	(5, 'Cuidado Capilar'),
	(5, 'Peines y Cepillos'),
	(5, 'Secadoras de cabello'),
	(5, 'Rasuradoras y Cortadoras de cabello'),
	(5, 'Otros'),

	(6, 'Juguetes'),
	(6, 'Juegos'),
	(6, 'Videojuegos'),
	(6, 'Pel culas'),
	(6, 'Libros'),
	(6, 'Artes y manualidades'),
	(6, 'Otros'),

	(7, 'Juguetes'),
	(7, 'Alimento'),
	(7, 'Higiene'),
	(7, 'Ropa'),
	(7, 'Otros art culos'),

	(8, 'Suministros de oficina'),
	(8, 'Decoraci n de eventos'),
	(8, 'Equipamiento M dico'),
	(8, 'Otros');
GO
-- 3. TIENDAS
INSERT INTO TIENDAS (UserID, CategoriaID, Nombre, NombreJuridico, NIT, Telefono)
VALUES
    (2, 1, 'Tienda Electrónica', 'Electro S.A.', 123456789, 98765432),
    (4, 2, 'Tienda de Ropa', 'Moda S.A.', 987654321, 12345678),
    (2, 3, 'Hogar Feliz', 'Hogar Ltda.', 111222333, 23456789),
    (4, 1, 'Gadgets Pro', 'Gadgets S.A.', 444555666, 34567890),
    (2, 2, 'Estilo Único', 'Estilo Ltda.', 777888999, 45678901);
-- TiendaID: 1 al 5

-- 4. DESCUENTOS
INSERT INTO DESCUENTOS (TiendaID, Nombre, Porcentaje, StartDate, EndDate)
VALUES
    (1, 'Promo Invierno', 10, '2025-06-01', '2025-08-31'),
    (2, 'Descuento Verano', 15, '2025-11-01', '2026-01-15'),
    (3, 'Oferta Flash', 20, '2025-07-01', '2025-07-10'),
    (4, 'Black Friday', 25, '2025-11-25', '2025-11-30'),
    (5, 'Liquidación', 30, '2025-12-01', '2025-12-31');
-- DescuentoID: 1 al 5

-- 5. INVENTARIO
INSERT INTO INVENTARIO (TiendaID, SubcategoriaID, DescuentoID, Nombre, Precio, Descripcion, Stock, Estado)
VALUES
    (1, 1, 1, 'Smartphone X', 500.00, 'Teléfono inteligente de última generación', 10, 'Disponible'),
    (1, 2, NULL, 'Funda Celular', 20.00, 'Funda protectora para smartphone', 30, 'Disponible'),
    (1, 3, 1, 'Laptop Pro 15"', 1200.00, 'Laptop de alto rendimiento', 5, 'Disponible'),
    (2, 18, 2, 'Zapatillas Running', 60.00, 'Zapatillas cómodas para correr', 25, 'Disponible'),
    (2, 20, NULL, 'Blusa Elegante', 35.00, 'Blusa para ocasiones especiales', 15, 'Disponible'),
    (3, 25, 3, 'Sofá 3 Cuerpos', 800.00, 'Sofá cómodo para sala', 3, 'Disponible'),
    (3, 26, NULL, 'Lámpara de Techo', 120.00, 'Lámpara moderna para decoración', 6, 'Disponible');
-- ProductoID: 1 al 7

-- 6. PRODUCTOS
INSERT INTO PRODUCTOS (Codigo, ProductoID, Estado)
VALUES
    (1001, 1, 'Disponible'),  -- Smartphone X
    (1002, 2, 'Disponible'),  -- Funda Celular
    (1003, 3, 'Disponible'),  -- Laptop Pro 15"
    (1004, 4, 'Disponible'),  -- Zapatillas Running
    (1005, 5, 'Disponible');  -- Blusa Elegante
-- ItemID: 1 al 5

-- 7. DIRECCIONES
INSERT INTO DIRECCIONES (ClienteID, Barrio, Calle, Numero)
VALUES
    (1, 'Barrio Centro', 'Av. Principal', 123),
    (2, 'Barrio Sur', 'Av. del Sur', 789),
    (3, 'Barrio Este', 'Calle Este', 101),
    (4, 'Barrio Norte', 'Calle Secundaria', 456),
    (5, 'Barrio Oeste', 'Av. Oeste', 202);
-- DireccionID: 1 al 5

-- 8. COMPRAS
INSERT INTO COMPRAS (ClienteID, DireccionID, Subtotal, ServiceFee, Total)
VALUES
    (1, 1, 520.00, 10.00, 530.00),
    (2, 2, 60.00, 5.00, 65.00),
    (3, 3, 1200.00, 15.00, 1215.00),
    (4, 4, 35.00, 5.00, 40.00),
    (5, 5, 800.00, 10.00, 810.00);
-- CompraID: 1 al 5

-- 9. VENTAS
INSERT INTO VENTAS (CompraID, ProductoID, Cantidad, PrecioUnitario)
VALUES
    (1, 1, 1, 500.00),  -- Smartphone X
    (1, 2, 1, 20.00),   -- Funda Celular
    (2, 4, 1, 60.00),   -- Zapatillas Running
    (3, 3, 1, 1200.00), -- Laptop Pro 15"
    (4, 5, 1, 35.00);   -- Blusa Elegante
-- VentaID: 1 al 5

-- 10. DETALLE_VENTA
INSERT INTO DETALLE_VENTA (VentaID, ItemID)
VALUES
    (1, 1),  -- Smartphone X
    (2, 2),  -- Funda Celular
    (3, 4),  -- Zapatillas Running
    (4, 3),  -- Laptop Pro 15"
    (5, 5);  -- Blusa Elegante
-- DetalleVentaID: 1 al 5

-- 11. TARJETAS
INSERT INTO TARJETAS (ClienteID, Red, NombreTitular, Numero, CVC, ExpDate)
VALUES
    (1, 'Visa', 'Juan Pérez', 4111111111111111, 123, '2026-12-01'),
    (2, 'MasterCard', 'María Gómez', 5111111111111111, 456, '2027-01-01'),
    (3, 'Visa', 'Carlos López', 6111111111111111, 789, '2026-11-01'),
    (4, 'MasterCard', 'Ana Martínez', 7111111111111111, 321, '2027-02-01'),
    (5, 'Visa', 'Luis Rodríguez', 8111111111111111, 654, '2026-10-01');
-- TarjetaID: 1 al 5

-- 12. DATOS_FACTURA
INSERT INTO DATOS_FACTURA (ClienteID, RazonSocial, NitCi)
VALUES
    (1, 'Juan Pérez', 1234567),
    (2, 'María Gómez', 7654321),
    (3, 'Carlos López', 1122334),
    (4, 'Ana Martínez', 9876543),
    (5, 'Luis Rodríguez', 5432167);
-- FacturaID: 1 al 5

-- 13. PAGOS
INSERT INTO PAGOS (CompraID, FacturaID, TarjetaID, MetodoPago, Monto)
VALUES
    (1, 1, 1, 'Tarjeta', 530.00),
    (2, 2, NULL, 'Efectivo', 65.00),
    (3, 3, 3, 'Tarjeta', 1215.00),
    (4, 4, NULL, 'QR', 40.00),
    (5, 5, 5, 'Tarjeta', 810.00);
-- PagoID: 1 al 5

-- Verificaciones
SELECT 'Users', COUNT(*) AS Total FROM USERS;
SELECT 'Clientes', COUNT(*) AS Total FROM CLIENTES;
SELECT 'Tiendas', COUNT(*) AS Total FROM TIENDAS;
SELECT 'Descuentos', COUNT(*) AS Total FROM DESCUENTOS;
SELECT 'Inventario', COUNT(*) AS Total FROM INVENTARIO;
SELECT 'Productos', COUNT(*) AS Total FROM PRODUCTOS;
SELECT 'Direcciones', COUNT(*) AS Total FROM DIRECCIONES;
SELECT 'Compras', COUNT(*) AS Total FROM COMPRAS;
SELECT 'Ventas', COUNT(*) AS Total FROM VENTAS;
SELECT 'Detalle_Venta', COUNT(*) AS Total FROM DETALLE_VENTA;
SELECT 'Tarjetas', COUNT(*) AS Total FROM TARJETAS;
SELECT 'Datos_Factura', COUNT(*) AS Total FROM DATOS_FACTURA;
SELECT 'Pagos', COUNT(*) AS Total FROM PAGOS;
GO