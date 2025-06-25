USE TkMarketplace
GO
select * from USERS
select * from CLIENTES
-- 3.Inicio Sesión
CREATE PROCEDURE sp_inicioSesion
@Correo   NVARCHAR(100),
@Password NVARCHAR(200)
AS
BEGIN
	BEGIN TRY
	BEGIN TRANSACTION
		DECLARE @UserID INT;

		SELECT @UserID = UserID
		FROM USERS
		WHERE Correo = @Correo AND [Password] = @Password

		IF @UserID IS NULL
			THROW 50001, 'Correo o contraseña incorrectos.', 1;
		IF EXISTS (
			select 1 from users
			where UserID = @UserID and Estado = 'Activo'
		) THROW 50002, 'El usuario tiene una sesión abierta.', 1;

			UPDATE USERS
			SET Estado = 'Activo'
			WHERE UserID = @UserID

		SELECT UserID FROM USERS WHERE UserID = @UserID

		COMMIT TRANSACTION;
	END TRY
	BEGIN CATCH
		IF XACT_STATE() <> 0
            ROLLBACK TRANSACTION;
        THROW;	
	END CATCH
END;
GO

-- 4.Cerrar Sesión
CREATE PROCEDURE sp_cerrarSesion
@UserID INT
AS
BEGIN
	BEGIN TRY
	BEGIN TRANSACTION
		IF NOT EXISTS(
			SELECT 1
			FROM USERS
			WHERE UserID = @UserID
		) THROW 50004, 'Esta cuenta no existe', 1;
		IF EXISTS (
			select 1 from users
			where UserID = @UserID and Estado = 'Inactivo'
		) THROW 50002, 'El usuario no tiene ninguna sesión abierta.', 1;

			UPDATE USERS
			SET Estado = 'Inactivo'
			WHERE UserID = @UserID

		COMMIT TRANSACTION;
	END TRY
	BEGIN CATCH
		IF XACT_STATE() <> 0
            ROLLBACK TRANSACTION;
        THROW;	
	END CATCH
END;