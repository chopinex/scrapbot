<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" type="text/css" href="styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300&display=swap" rel="stylesheet">
    <title>Scrapper Login</title>
</head>
<body>
<div class="frm">
<div class="form-titulo">Acceso</div>
<form action="logged.php" method="post" name="login">
    <div class="form-line">
        <label>Usuario</label>
        <input type="text" name="usuario" required/>
    </div>
    <div class="form-line">
        <label>Contraseña</label>
        <input type="password" name="pass" required/>
    </div>
    <div class="form-line">
        <input type="submit" value="Ingresar"/>
    </div>
</form>
</div>
</body>
</html>