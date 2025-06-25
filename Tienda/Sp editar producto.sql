-- sp editar nuevo producto 
CREATE OR ALTER PROCEDURE sp_EditarProducto
    @ProductoID     INT,
    @SubcategoriaID INT,
    @Nombre         NVARCHAR(100),
    @Precio         DECIMAL(10,2),
    @Descripcion    NVARCHAR(200),
    @DescuentoID    INT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        -- Validar existencia del producto
        IF NOT EXISTS (SELECT 1 FROM INVENTARIO WHERE ProductoID = @ProductoID)
        BEGIN
            THROW 50001, 'El producto especificado no existe.', 1;
        END

        -- Validar precio positivo
        IF @Precio <= 0
        BEGIN
            THROW 50002, 'El precio debe ser mayor a cero.', 1;
        END

        BEGIN TRANSACTION;

        -- Actualizar los datos del producto
        UPDATE INVENTARIO
        SET
            SubcategoriaID = @SubcategoriaID,
            Nombre = @Nombre,
            Precio = @Precio,
            Descripcion = @Descripcion,
            DescuentoID = @DescuentoID,
            ModifiedDate = GETDATE()
        WHERE ProductoID = @ProductoID;

        COMMIT TRANSACTION;

        SELECT 'Producto actualizado exitosamente.' AS Mensaje;

    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0
            ROLLBACK TRANSACTION;

        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorState INT = ERROR_STATE();
        THROW 50000, @ErrorMessage, @ErrorState;
    END CATCH
END;
GO
