USE TkMarketplace
GO

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
	begin try -- AGREGADO

		IF EXISTS(SELECT 1 FROM USERS WHERE Correo = @Correo AND Tipo = 'Cliente')
		begin 
			throw 50001, 'Ya tienes una cuenta registrada' , 1;
		end 

		begin transaction;

		-- Insertamos al nuevo cliente '
		insert into USERS(Correo, Password, Tipo, Estado)
		values(@Correo, @Password, 'Cliente', 'Activo')

		-- no hacia commit en la tabla CLIENTES, entonces AGREGUE el insert:
		DECLARE @UserID INT = SCOPE_IDENTITY();
		insert into CLIENTES(UserID, Nombre, Apellido, Telefono)
		values (@UserID, @Nombre, @Apellido, @Telefono);
		-- AQUI TERMINA LO QUE AGREGUE

		commit transaction;

		SELECT
			'Cliente registrado existosamente.' AS Mensaje,
			@UserID AS UserID; -- CAMBIADO : ClienteID -> UserID

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
