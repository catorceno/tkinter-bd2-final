--creacion del sp agragar clientes
create or alter procedure sp_RegistrarNuevosClientes 
	@Correo NVARCHAR(100),
	@Password NVARCHAR(200),
	@Nombre NVARCHAR(50),
	@Apellido NVARCHAR(50),
	@Telefono INT 
AS 
BEGIN 
	SET NOCOUNT ON;

	--1. VERIFICACION SI YA EXISTE ESE CORREO
	IF EXISTS(SELECT 1 FROM USERS WHERE Correo = @Correo AND Tipo = 'Cliente')
	begin 
		throw 50001, 'Ya tienes una cuenta registrada' , 1;
	end 

	begin transaction;

	--2.insertamos al nuevo cliente '
	insert into USERS(Correo, Password, Tipo, Estado)
	values(@Correo, @Password, 'Cliente', 'Activo')

	commit transaction;

	--confirmacion de exito 
	select 'Cliente registrado existosamente. ' as Mnesaje, 
	SCOPE_IDENTITY () as ClienteID;

	end try 
	begin catch 
		if XACT_STATE() <> 0
		rollback transaction;

		declare @ErrorMessage nvarchar(4000) = Error_Message();
		declare @ErrorState int = ERROR_STATE();
		THROW 50000, @ErrorMessage, @ErrorState;
	end catch 
end;
go