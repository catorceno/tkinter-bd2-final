--sp iniciar seseion 
select * from USERS

create or alter procedure sp_InicioSesion
	@Correo nvarchar(200),
	@Password int
as 
begin 
	set nocount on;
	begin try
		if not exists(select 1 from USERS where Correo = @Correo and Password = @Password)
		begin 
			throw 50001, 'Correo o Contraseña incorrectos ', 1;
		end

		if exists (select 1 from USERS where Correo = @Correo and Estado = 'Inactivo')
		begin 
			throw 50002, 'La cuenta esta inactiva. ', 1;
		end 

	--devolvemos los datos del usuario si todo esta bien 
	select UserID, Correo, Tipo, Estado from USERS
	where Correo = @Correo and Password = @Password

	end try 
	begin catch 
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorState INT = ERROR_STATE();
        THROW 50000, @ErrorMessage, @ErrorState;
    END CATCH
END;
GO