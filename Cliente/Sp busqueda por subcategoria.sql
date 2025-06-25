--Este es el buscador por sub categorias 
--ejecutado 
CREATE OR ALTER PROCEDURE usp_BuscarPorSubcategoria
    @SubcategoriaID INT
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        -- Validar que SubcategoriaID existe
        IF NOT EXISTS (SELECT 1 FROM SUBCATEGORIAS WHERE SubcategoriaID = @SubcategoriaID)
        BEGIN
            THROW 50001, 'La subcategoría especificada no existe.', 1;
        END

        -- Buscar productos por SubcategoriaID
        SELECT 
            I.ProductoID,
            I.Nombre,
            I.Precio,
            I.PrecioDescuento,
            I.Stock,
            I.Estado,
            S.Nombre AS Subcategoria,
            C.Nombre AS Categoria
        FROM INVENTARIO I
        INNER JOIN SUBCATEGORIAS S ON I.SubcategoriaID = S.SubcategoriaID
        INNER JOIN CATEGORIAS C ON S.CategoriaID = C.CategoriaID
        WHERE I.SubcategoriaID = @SubcategoriaID
        ORDER BY I.Nombre;

        -- Devolver mensaje si no hay productos
        IF @@ROWCOUNT = 0
        BEGIN
            SELECT 'No se encontraron productos en esta subcategoría.' AS Mensaje;
        END
    END TRY
    BEGIN CATCH
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        THROW 50000, @ErrorMessage, @ErrorState;
    END CATCH
END;
GO

select * from INVENTARIO
