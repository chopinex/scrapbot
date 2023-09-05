<?php
# Si no entiendes el código, primero mira a login.php
# Iniciar sesión para usar $_SESSION
session_start();
# Y ahora leer si NO hay algo llamado usuario en la sesión,
# usando empty (vacío, ¿está vacío?)
# Recomiendo: https://parzibyte.me/blog/2018/08/09/isset-vs-empty-en-php/
if (empty($_SESSION['email'])) {
    # Lo redireccionamos al formulario de inicio de sesión
    header("Location: index.php");
    # Y salimos del script
    exit();
}
if($_SESSION['rol']!=0)
    header("Location: main.php");
# No hace falta un else, pues si el usuario no se loguea, todo lo de abajo no se ejecuta
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Registro de usuarios</title>
    <link rel="stylesheet" type="text/css" href="styles.css">
</head>
<body>
<div><a href="main.php" class="form-button">Atrás</a></div>
<div class="frm">
<div class="form-titulo">Registro de usuarios</div>
<form action="registro.php" method="post">
    <div class="form-line">
        <label>Nombre</label>
        <input type="text" name="nombre" placeholder="Nombre" required>
    </div>
    <div class="form-line">
        <label>Correo electrónico</label>
        <input type="email" name="email" pattern="[^@]+@[^@\.]+\.[a-z]+" placeholder="Correo Electrónico" required>
    </div>
    <div class="form-line">
        <label>Contraseña</label>
        <input type="password" name="password" id="password" placeholder="Contraseña" required>
    </div>
    <div class="form-line">
        <label>Confirmar Contraseña</label>
        <input type="password" name="password2" id="password2" placeholder="Repetir contraseña" onkeyup="verificarPasswords();" required>
    </div>
    <div class="form-line">
        <div class="error-msg ocultar" id="error" role="alert">
            Las Contraseñas no coinciden, vuelve a intentar !
        </div>
        <div class="ok-msg ocultar" id="ok" role="alert">
            Las Contraseñas coinciden !
        </div>
    </div>
    <div class="form-line">
        <input type="submit" value="Registrarse" >
    </div>
</form>

<script type="text/javascript">
    function verificarPasswords(){
        pass1 = document.getElementById('password');
        pass2 = document.getElementById('password2');
        console.log(pass1.value+" "+pass2.value);
        if (pass1.value != pass2.value) {
 
            // Si las constraseñas no coinciden mostramos un mensaje
            document.getElementById("error").classList.add("mostrar");
            document.getElementById("ok").classList.remove("mostrar");
            document.getElementById("ok").classList.add("ocultar");
         
            return false;
        }
         
        else {
         
            // Si las contraseñas coinciden ocultamos el mensaje de error
            document.getElementById("error").classList.remove("mostrar");
         
            // Mostramos un mensaje mencionando que las Contraseñas coinciden
            document.getElementById("ok").classList.remove("ocultar");
              
            return true;
    }

    }
</script>
</body>
</html>