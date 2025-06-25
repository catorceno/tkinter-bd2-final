--sp proceso venta practcando 


--este sp esta actualizado 

create or alter procedure sp_RegistrarVenta
	@CompraID int,
	@ProductoID int,
	@Cantidad int
as 
begin 
	set nocount on;
	begin try 

	if not exists(select 1 from INVENTARIO where ProductoID = @ProductoID) --verifica si el produc exite en la tabla inventario
	begin 
		throw 50001, 'El Producto no existe', 1;
	end 

	--verificacion del stock
	declare @StockDisponible int; 
	select @StockDisponible = Stock from INVENTARIO where ProductoID = @ProductoID; --consultamos el stock disponible

	if @StockDisponible < @Cantidad --verifica si tenemos sotck suficiente para vender 
		throw 50002, 'No tenemos stock sufuciente', 1;

	--obtencion del precio unitario
	declare @PrecioUnitario decimal(10,2);
	select @PrecioUnitario = Precio from INVENTARIO where ProductoID = @ProductoID; --consulta el precio del producto
	---transation 
	begin transaction;
	--insertamos las ventas 
	insert into VENTAS(CompraID, ProductoID, Cantidad, PrecioUnitario, OrderDate, ShipDate
	, ModifiedDate)
	values (@CompraID, @ProductoID, @Cantidad, @PrecioUnitario,GETDATE(), GETDATE(), GETDATE()); --inserta en tabla ventas 
	--actualizamos las tablas
	update INVENTARIO  --actualiza el inventaro 
	set Stock = Stock - @Cantidad --resta la cantidad vendida al stock del producto 
	where ProductoID = @ProductoID;

	if exists (select 1 from INVENTARIO where ProductoID = @ProductoID and Stock = 0)
	begin 
		update INVENTARIO   --si el stock en ese producto llega a cero lo marca como no disponible
		set Estado = 'No disponible'
		where ProductoID = @ProductoID;
	end


	commit transaction;

	select 'Venta registrada exitosamente' as mensaje , SCOPE_IDENTITY() as VentaID;

	END TRY
	BEGIN CATCH 
		IF XACT_STATE() <> 0
			ROLLBACK TRANSACTION;
		DECLARE @ERRORMESS NVARCHAR(4000) = ERROR_MESSAGE();
		DECLARE @ERRORST INT = ERROR_STATE();
		THROW 50000, @ERRORMESS, @ERRORST;
	END CATCH
END;
GO

