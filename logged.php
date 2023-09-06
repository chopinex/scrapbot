<?php

// Conexión a la base de datos

$db = new PDO('sqlite:db/users.sqlite');
// Validar el formulario
if (isset($_POST['email']) && isset($_POST['password'])) {
    // Obtener el usuario de la base de datos
    $stmt = $db->prepare('SELECT * FROM users WHERE Email = ?');
    $stmt->execute(array($_POST['email']));
    $user = $stmt->fetch();

    // Comprobar la contraseña
    if ($user && password_verify($_POST['password'], $user['Password'])) {

        // Iniciar sesión al usuario
        session_start();
        $_SESSION['email'] = $user['Email'];
        $_SESSION['rol'] = $user['Rol'];

        // Redirigir al usuario a la página principal
        header('Location: main.php');
    }
    else{
        echo "<div class='error-msg'>Invalid Login Details</div>";
        header( 'refresh:3;url=index.php' );
    }
}

?>