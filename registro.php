<?php

// Conexión a la base de datos
$db = new PDO('sqlite:db/users.sqlite');

// Validar el formulario
if (isset($_POST['nombre']) && isset($_POST['email']) && isset($_POST['password'])) {
;
    // Hashear la contraseña
    $password = password_hash($_POST['password'], PASSWORD_DEFAULT);

    // Insertar el usuario en la base de datos
    $stmt = $db->prepare('INSERT INTO users (Nombre, Email, Password, Rol) VALUES (?, ?, ?, ?)');
    $stmt->execute(array($_POST['nombre'], $_POST['email'], $password, 1));

    echo "<div class='ok-msg'> Usuario creado </div>";
    // Redirigir al usuario a la página de inicio
    header('refresh:3;url=main.php');
}

?>