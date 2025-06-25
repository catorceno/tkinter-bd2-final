--sp eliminar producto 
CREATE OR ALTER PROCEDURE sp_EliminarProducto
    @TiendaID   INT,
    @ProductoID INT
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        -- Validar que el producto exista y pertenezca a la tienda
        IF NOT EXISTS (
            SELECT 1 FROM INVENTARIO
            WHERE ProductoID = @ProductoID AND TiendaID = @TiendaID
        )
        BEGIN
            THROW 50001, 'El producto no existe o no pertenece a esta tienda.', 1;
        END

        -- Validar que el producto esté disponible
        IF NOT EXISTS (
            SELECT 1 FROM INVENTARIO
            WHERE ProductoID = @ProductoID AND Estado = 'Disponible'
        )
        BEGIN
            THROW 50002, 'El producto no está disponible o ya fue descontinuado.', 1;
        END

        BEGIN TRANSACTION;

        -- Cambiar el estado a descontinuado
        UPDATE INVENTARIO 
        SET Estado = 'Descontinuado',
            ModifiedDate = GETDATE()
        WHERE ProductoID = @ProductoID;

        COMMIT TRANSACTION;

        SELECT 'Producto descontinuado exitosamente.' AS Mensaje;

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
