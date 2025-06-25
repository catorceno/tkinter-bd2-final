USE Marcket_P;

-- 1. Populate CATEGORIAS
DECLARE @i INT = 1;
WHILE @i <= 500
BEGIN
    INSERT INTO CATEGORIAS (Nombre, ModifiedDate)
    VALUES (CONCAT('Categoria_', @i), GETDATE());
    SET @i = @i + 1;
END;

-- 2. Populate SUBCATEGORIAS
DECLARE @i INT;
SET @i = 1;
WHILE @i <= 500
BEGIN
    INSERT INTO SUBCATEGORIAS (CategoriaID, Nombre, ModifiedDate)
    VALUES (
        (SELECT TOP 1 CategoriaID FROM CATEGORIAS ORDER BY NEWID()), -- Random CategoriaID
        CONCAT('Subcategoria_', @i),
			GETDATE()
		);
		SET @i = @i + 1;
	END;



-- 3. Populate USERS
DECLARE @i INT;
SET @i = 1;
WHILE @i <= 500
BEGIN
    DECLARE @Tipo NVARCHAR(20) = CASE WHEN @i % 2 = 0 THEN 'Cliente' ELSE 'Tienda' END;
    DECLARE @Correo NVARCHAR(100) = CONCAT('user', @i, '@marketp.com');
    INSERT INTO USERS (Correo, Password, Tipo, Estado, ModifiedDate)
    VALUES (
        @Correo,
        CONCAT('password_', @i), -- In real scenarios, use hashed passwords
        @Tipo,
        'Activo',
        GETDATE()
    );
    SET @i = @i + 1;
END;

-- 4. Populate CLIENTES
DECLARE @i INT;
SET @i = 1;
WHILE @i <= 500
BEGIN
    DECLARE @UserID INT = (SELECT TOP 1 UserID FROM USERS WHERE Tipo = 'Cliente' ORDER BY NEWID());
    IF @UserID IS NOT NULL
    BEGIN
        INSERT INTO CLIENTES (UserID, Nombre, Apellido, Telefono, ModifiedDate)
        VALUES (
            @UserID,
            CONCAT('Nombre_', @i),
            CONCAT('Apellido_', @i),
            30000000 + (@i % 9999999), -- Generates valid 8-digit phone number
            GETDATE()
        );
    END;
    SET @i = @i + 1;
END;

-- 5. Populate TIENDAS
DECLARE @i INT;
SET @i = 1;
WHILE @i <= 500
BEGIN
    DECLARE @UserID_Tienda INT = (SELECT TOP 1 UserID FROM USERS WHERE Tipo = 'Tienda' ORDER BY NEWID());
    IF @UserID_Tienda IS NOT NULL
    BEGIN
        INSERT INTO TIENDAS (UserID, CategoriaID, Nombre, NombreJuridico, NIT, Telefono, ModifiedDate)
        VALUES (
            @UserID_Tienda,
            (SELECT TOP 1 CategoriaID FROM CATEGORIAS ORDER BY NEWID()),
            CONCAT('Tienda_', @i),
            CONCAT('Juridico_', @i),
            100000000 + (@i % 899999999), -- Generates valid 9-digit NIT
            30000000 + (@i % 9999999), -- Generates valid 8-digit phone number
            GETDATE()
        );
    END;
    SET @i = @i + 1;
END;

-- 6. Populate DESCUENTOS
DECLARE @i INT;
SET @i = 1;
WHILE @i <= 500
BEGIN
    DECLARE @StartDate DATETIME = DATEADD(DAY, -30, GETDATE());
    DECLARE @EndDate DATETIME = DATEADD(DAY, 30, GETDATE());
    INSERT INTO DESCUENTOS (TiendaID, Nombre, Porcentaje, StartDate, EndDate, ModifiedDate)
    VALUES (
        (SELECT TOP 1 TiendaID FROM TIENDAS ORDER BY NEWID()),
        CONCAT('Descuento_', @i),
        1 + (@i % 100), -- Random percentage between 1 and 100
        @StartDate,
        @EndDate,
        GETDATE()
    );
    SET @i = @i + 1;
END;

-- 7. Populate INVENTARIO
DECLARE @i INT;
SET @i = 1;
WHILE @i <= 500
BEGIN
    DECLARE @Precio DECIMAL(20,2) = 10.00 + (@i % 990) + (RAND() * 100);
    DECLARE @DescuentoID INT = (SELECT TOP 1 DescuentoID FROM DESCUENTOS ORDER BY NEWID());
    DECLARE @Porcentaje INT = (SELECT Porcentaje FROM DESCUENTOS WHERE DescuentoID = @DescuentoID);
    DECLARE @PrecioDescuento DECIMAL(20,2) = @Precio * (1 - (@Porcentaje / 100.0));
    INSERT INTO INVENTARIO (TiendaID, SubcategoriaID, DescuentoID, Nombre, Precio, Descripcion, PrecioDescuento, Stock, Estado, ModifiedDate)
    VALUES (
        (SELECT TOP 1 TiendaID FROM TIENDAS ORDER BY NEWID()),
        (SELECT TOP 1 SubcategoriaID FROM SUBCATEGORIAS ORDER BY NEWID()),
        @DescuentoID,
        CONCAT('Producto_', @i),
        @Precio,
        CONCAT('Descripción del producto ', @i),
        @PrecioDescuento,
        10 + (@i % 90), -- Random stock between 10 and 99
        'Disponible',
        GETDATE()
    );
    SET @i = @i + 1;
END;

-- 8. Populate PRODUCTOS
DECLARE @i INT;
SET @i = 1;
WHILE @i <= 500
BEGIN
    INSERT INTO PRODUCTOS (Codigo, ProductoID, Estado, ModifiedDate)
    VALUES (
        1000 + (@i % 9999), -- Unique code
        (SELECT TOP 1 ProductoID FROM INVENTARIO ORDER BY NEWID()),
        'Disponible',
        GETDATE()
    );
    SET @i = @i + 1;
END;

-- 9. Populate DIRECCIONES
DECLARE @i INT;
SET @i = 1;
WHILE @i <= 500
BEGIN
    INSERT INTO DIRECCIONES (ClienteID, Barrio, Calle, Numero, Estado, ModifiedDate)
    VALUES (
        (SELECT TOP 1 ClienteID FROM CLIENTES ORDER BY NEWID()),
        CONCAT('Barrio_', @i),
        CONCAT('Calle_', @i),
        1 + (@i % 999),
        'Activo',
        GETDATE()
    );
    SET @i = @i + 1;
END;

-- 10. Populate COMPRAS
DECLARE @i INT;
SET @i = 1;
WHILE @i <= 500
BEGIN
    DECLARE @Subtotal DECIMAL(20,2) = 50.00 + (@i % 950) + (RAND() * 100);
    DECLARE @ServiceFee DECIMAL(4,2) = 5.00 + (RAND() * 5);
    DECLARE @Total DECIMAL(20,2) = @Subtotal + @ServiceFee;
    INSERT INTO COMPRAS (ClienteID, DireccionID, Subtotal, ServiceFee, Total, ModifiedDate)
    VALUES (
        (SELECT TOP 1 ClienteID FROM CLIENTES ORDER BY NEWID()),
        (SELECT TOP 1 DireccionID FROM DIRECCIONES ORDER BY NEWID()),
        @Subtotal,
        @ServiceFee,
        @Total,
        GETDATE()
    );
    SET @i = @i + 1;
END;

-- 11. Populate VENTAS
DECLARE @i INT;
SET @i = 1;
WHILE @i <= 500
BEGIN
    DECLARE @ProductoID INT = (SELECT TOP 1 ProductoID FROM INVENTARIO ORDER BY NEWID());
    DECLARE @PrecioUnitario DECIMAL(20,2) = (SELECT Precio FROM INVENTARIO WHERE ProductoID = @ProductoID);
    INSERT INTO VENTAS (CompraID, ProductoID, Cantidad, PrecioUnitario, OrderDate, ShipDate, ModifiedDate)
    VALUES (
        (SELECT TOP 1 CompraID FROM COMPRAS ORDER BY NEWID()),
        @ProductoID,
        1 + (@i % 5), -- Random quantity between 1 and 5
        @PrecioUnitario,
        GETDATE(),
        DATEADD(DAY, 1, GETDATE()),
        GETDATE()
    );
    SET @i = @i + 1;
END;

-- 12. Populate DETALLE_VENTA
DECLARE @i INT;
SET @i = 1;
WHILE @i <= 500
BEGIN
    INSERT INTO DETALLE_VENTA (VentaID, ItemID, ModifiedDate)
    VALUES (
        (SELECT TOP 1 VentaID FROM VENTAS ORDER BY NEWID()),
        (SELECT TOP 1 ItemID FROM PRODUCTOS ORDER BY NEWID()),
        GETDATE()
    );
    SET @i = @i + 1;
END;

-- 13. Populate TARJETAS
DECLARE @i INT;
SET @i = 1;
WHILE @i <= 500
BEGIN
    INSERT INTO TARJETAS (ClienteID, Red, NombreTitular, Numero, CVC, ExpDate, ModifiedDate)
    VALUES (
        (SELECT TOP 1 ClienteID FROM CLIENTES ORDER BY NEWID()),
        CASE WHEN @i % 2 = 0 THEN 'Visa' ELSE 'MasterCard' END,
        CONCAT('Titular_', @i),
        4000000000000000 + (@i % 9999999999999999), -- 16-digit card number
        100 + (@i % 900), -- 3-digit CVC
        DATEADD(YEAR, 1 + (@i % 5), GETDATE()), -- Valid expiration date
        GETDATE()
    );
    SET @i = @i + 1;
END;

-- 14. Populate DATOS_FACTURA
DECLARE @i INT;
SET @i = 1;
WHILE @i <= 500
BEGIN
    INSERT INTO DATOS_FACTURA (ClienteID, RazonSocial, NitCi, Estado, ModifiedDate)
    VALUES (
        (SELECT TOP 1 ClienteID FROM CLIENTES ORDER BY NEWID()),
        CONCAT('RazonSocial_', @i),
        1000000 + (@i % 9999999), -- Valid NitCi
        'Activo',
        GETDATE()
    );
    SET @i = @i + 1;
END;

-- 15. Populate PAGOS
DECLARE @i INT;
SET @i = 1;
WHILE @i <= 500
BEGIN
    DECLARE @MetodoPago NVARCHAR(20) = CASE 
        WHEN @i % 3 = 0 THEN 'Tarjeta'
        WHEN @i % 3 = 1 THEN 'QR'
        ELSE 'Efectivo' 
    END;
    DECLARE @TarjetaID INT = CASE 
        WHEN @MetodoPago = 'Tarjeta' THEN (SELECT TOP 1 TarjetaID FROM TARJETAS ORDER BY NEWID())
        ELSE NULL 
    END;
    INSERT INTO PAGOS (CompraID, FacturaID, TarjetaID, MetodoPago, Monto, Fecha, ModifiedDate)
    VALUES (
        (SELECT TOP 1 CompraID FROM COMPRAS ORDER BY NEWID()),
        (SELECT TOP 1 FacturaID FROM DATOS_FACTURA ORDER BY NEWID()),
        @TarjetaID,
        @MetodoPago,
        50.00 + (@i % 950) + (RAND() * 100), -- Random payment amount
        GETDATE(),
        GETDATE()
    );
    SET @i = @i + 1;
END;