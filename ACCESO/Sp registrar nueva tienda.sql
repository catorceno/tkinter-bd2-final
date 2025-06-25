--sp para registrar nueva tienda 
create or alter procedure sp_registrarNuevaTienda
	@Correo   nvarchar(100),
	@Password  nvarchar(200),
	@Nombre nvarchar(50),
	@NombreJuridico nvarchar(50),
	@NIT int,
	@Teloefono int,
	@CategoriaID int

as 
begin 
	set nocount on;

	begin try 
	--verificar si ya existe una tienda con este correo
		if exists (select 1 from USERS where Correo = @Correo and Tipo = 'Tienda')
		begin 
			throw 50001, 'Ya tienes una cuenta registrada ', 1;
		end

	begin transaction;

	--insertamos en users
	insert into USERS (Correo, Password, Tipo, Estado)
	values(@Correo, @Password, 'Tienda', 'Activo');

	--obtenemos el nuevo user id 
	declare @UserID int = scope_identity();

	--insertamos en tiendas 
	insert into TIENDAS(UserID, Nombre, NombreJuridico, NIT, Telefono, CategoriaID)
	values(@UserID, @Nombre, @NombreJuridico, @NIT, @Teloefono, @CategoriaID);

	commit transaction;

	select 'Tienda registrada exitosamente ' as Mensaje, @UserID as UserId;

END TRY 
BEGIN CATCH 
	IF XACT_STATE() <> 0
		ROLLBACK TRANSACTION;

	DECLARE @ErrorMessage nvarchar(4000) = Error_Message();
	declare @ErrorState int = Error_State();
	throw 50000, @ErrorMessage, @ErrorState;
end catch
end;
go

	