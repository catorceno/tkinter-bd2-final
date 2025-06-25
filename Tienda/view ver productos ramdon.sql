use Marcket_Actualizado

SELECT * FROM RandomProductsByStoreView;


CREATE VIEW RandomProductsByStoreView AS
WITH RankedProducts AS (
    SELECT 
        i.ProductoID,
        i.TiendaID,
        t.Nombre AS NombreTienda,
        i.SubcategoriaID,
        s.Nombre AS NombreSubcategoria,
        i.Nombre AS NombreProducto,
        i.Precio,
        i.Descripcion,
        i.PrecioDescuento,
        d.Porcentaje AS PorcentajeDescuento,
        ROW_NUMBER() OVER (PARTITION BY i.TiendaID ORDER BY NEWID()) AS RowNum
    FROM INVENTARIO i
    INNER JOIN TIENDAS t ON i.TiendaID = t.TiendaID
    INNER JOIN SUBCATEGORIAS s ON i.SubcategoriaID = s.SubcategoriaID
    LEFT JOIN DESCUENTOS d ON i.DescuentoID = d.DescuentoID
    WHERE 
        i.Estado = 'Disponible'
        AND (d.DescuentoID IS NULL OR (d.StartDate <= GETDATE() AND (d.EndDate IS NULL OR d.EndDate >= GETDATE())))
)
SELECT 
    ProductoID,
    TiendaID,
    NombreTienda,
    SubcategoriaID,
    NombreSubcategoria,
    NombreProducto,
    Precio,
    Descripcion,
    PrecioDescuento,
    PorcentajeDescuento
FROM RankedProducts
WHERE RowNum <= 5;

