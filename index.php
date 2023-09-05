<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Login</title>
    <link rel="stylesheet" type="text/css" href="styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300&display=swap" rel="stylesheet">
</head>
<body>

<div class="frm">
<div class="form-titulo">Acceso</div>
<form action="logged.php" method="post">
    <div class="form-line">
        <label>Correo electrónico</label>
        <input type="email" name="email" pattern="[^@]+@[^@\.]+\.[a-z]+" placeholder="Correo Electrónico" required>
    </div>
    <div class="form-line">
        <label>Contraseña</label>
        <input type="password" name="password" placeholder="Contraseña" required>
    </div>
    <div class="form-line">
        <input class="form-button" type="submit" value="Iniciar sesión"/>
    </div>
</form>
</body>
</html>