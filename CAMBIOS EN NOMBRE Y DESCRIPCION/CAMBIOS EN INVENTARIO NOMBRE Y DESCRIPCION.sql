USE Marcket_P;

-- Paso 1: Eliminar las columnas Nombre y Descripcion
ALTER TABLE INVENTARIO
DROP COLUMN Nombre;

ALTER TABLE INVENTARIO
DROP COLUMN Descripcion;

-- Paso 2: Agregar las columnas (Nombre permite NULL inicialmente)
ALTER TABLE INVENTARIO
ADD Nombre NVARCHAR(50);

ALTER TABLE INVENTARIO
ADD Descripcion NVARCHAR(200);

-- Paso 3: Actualizar los registros de INVENTARIO con nombres y descripciones
DECLARE @i INT;
SET @i = 1; -- Inicializar la variable @i

WHILE @i <= 500
BEGIN
    DECLARE @Nombre NVARCHAR(50);
    DECLARE @Descripcion NVARCHAR(200);

    -- Asignar productos y descripciones c�clicamente (20 productos)
    SET @Nombre = CASE ((@i - 1) % 20) + 1
        WHEN 1 THEN 'Smartphone X'
        WHEN 2 THEN 'Funda Celular'
        WHEN 3 THEN 'Laptop Pro 15"'
        WHEN 4 THEN 'Zapatillas Running'
        WHEN 5 THEN 'Blusa Elegante'
        WHEN 6 THEN 'Sof� 3 Cuerpos'
        WHEN 7 THEN 'L�mpara de Techo'
        WHEN 8 THEN 'Auriculares Bluetooth'
        WHEN 9 THEN 'Televisor 4K 55"'
        WHEN 10 THEN 'Cafetera Autom�tica'
        WHEN 11 THEN 'Reloj Deportivo'
        WHEN 12 THEN 'Mochila Viajera'
        WHEN 13 THEN 'Tablet 10"'
        WHEN 14 THEN 'Silla Ergon�mica'
        WHEN 15 THEN 'C�mara Digital'
        WHEN 16 THEN 'Pantalones Jeans'
        WHEN 17 THEN 'Parlante Bluetooth'
        WHEN 18 THEN 'Microondas 30L'
        WHEN 19 THEN 'Bicicleta Urbana'
        WHEN 20 THEN 'Bolso de Mano'
    END;

    SET @Descripcion = CASE ((@i - 1) % 20) + 1
        WHEN 1 THEN 'Tel�fono inteligente de �ltima generaci�n'
        WHEN 2 THEN 'Funda protectora para smartphone'
        WHEN 3 THEN 'Laptop de alto rendimiento'
        WHEN 4 THEN 'Zapatillas c�modas para correr'
        WHEN 5 THEN 'Blusa para ocasiones especiales'
        WHEN 6 THEN 'Sof� c�modo para sala'
        WHEN 7 THEN 'L�mpara moderna para decoraci�n'
        WHEN 8 THEN 'Auriculares inal�mbricos con cancelaci�n de ruido'
        WHEN 9 THEN 'Televisor LED de alta resoluci�n'
        WHEN 10 THEN 'M�quina de caf� con molinillo integrado'
        WHEN 11 THEN 'Reloj inteligente para monitoreo de actividad'
        WHEN 12 THEN 'Mochila resistente para viajes'
        WHEN 13 THEN 'Tablet ligera para trabajo y entretenimiento'
        WHEN 14 THEN 'Silla ajustable para oficina'
        WHEN 15 THEN 'C�mara compacta con alta resoluci�n'
        WHEN 16 THEN 'Jeans modernos y c�modos'
        WHEN 17 THEN 'Altavoz port�til con gran calidad de sonido'
        WHEN 18 THEN 'Microondas con funciones avanzadas'
        WHEN 19 THEN 'Bicicleta ideal para la ciudad'
        WHEN 20 THEN 'Bolso elegante para uso diario'
    END;

    -- Actualizar el registro en INVENTARIO
    UPDATE INVENTARIO
    SET 
        Nombre = @Nombre,
        Descripcion = @Descripcion
    WHERE ProductoID = @i;

    SET @i = @i + 1; -- Incrementar el contador
END;




select * from INVENTARIO
