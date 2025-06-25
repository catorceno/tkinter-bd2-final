--registrar un producto 

select * from INVENTARIO


create or alter procedure sp_RegistrarNuevoProducto
	@TiendaID int,
	@SubcategoriaID int ,
	@DescuentoID int  = null,
	@Nombre nvarchar(100),
	@Precio decimal(10, 2),
	@Descripcion nvarchar(250),
	@Stock int
as 
begin 
	set nocount on;
	begin try 
	--validaciones del precio 
	if @Precio <= 0		
		throw 50001, 'El precio debe ser mayor a cero ', 1;

	--validar stock
	if @Stock < 0
		throw 50002, 'El Stock debe ser mayor a cero ', 1;

	begin transaction;
	--insertamos al producto
	insert into INVENTARIO(TiendaID, SubcategoriaID, DescuentoID, Nombre, Precio, Descripcion, Stock, Estado, ModifiedDate)
	values (@TiendaID, @SubcategoriaID, @DescuentoID, @Nombre, @Precio, @Descripcion,@Stock,
			case when @Stock < 0 then 'No disponible' else 'Disponible' end, GETDATE());

	commit transaction;
	select 'Producto Registrado exitosamente ' as Mensaje , SCOPE_IDENTITY() as ProductoID;

	end try 
	begin catch 
		if XACT_STATE() <> 0
			rollback transaction;
		Declare @ErrorMessage nvarchar(4000) = error_message();
		declare @ErrorState int = error_state();
		throw 50000, @ErrorMessage , @ErrorState;
	end catch 
end;
go