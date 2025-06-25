USE Marketplace;
GO
SELECT * FROM INVENTARIO;
SELECT * FROM SUBCATEGORIAS;
SELECT * FROM CATEGORIAS;
-- Prueba 1: Buscar productos en SubcategoriaID 1 (Celulares)
EXEC usp_BuscarPorSubcategoria @SubcategoriaID = 1;
-- Resultado esperado: Muestra productos como "Smartphone X" (ProductoID 1) si está vinculado a SubcategoriaID 1

-- Prueba 2: Buscar productos en SubcategoriaID 2 (Accesorios para celulares)
EXEC usp_BuscarPorSubcategoria @SubcategoriaID = 2;
-- Resultado esperado: Muestra productos como "Funda Celular" (ProductoID 2) si está vinculado a SubcategoriaID 2

-- Prueba 3: Buscar productos en SubcategoriaID 10 (Ropa para Niños)
EXEC usp_BuscarPorSubcategoria @SubcategoriaID = 25;

-- Resultado esperado: Muestra un mensaje "No se encontraron productos en esta subcategoría." si no hay productos vinculados

-- Prueba 4: Buscar con SubcategoriaID inválido
EXEC usp_BuscarPorSubcategoria @SubcategoriaID = 999;
-- Resultado esperado: Error 50001 (La subcategoría especificada no existe.)
GO

EXEC usp_BuscarPorSubcategoria @SubcategoriaID = 4