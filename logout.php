<?php
# Si no entiendes esto, primero mira a login.php
# Iniciar sesión (sí, aunque la vamos a destruir, primero se debe iniciar)
session_start();
# Después, destruirla
# Eso va a eliminar todo lo que haya en $_SESSION
session_destroy();
# Finalmente lo redireccionamos al formulario
echo "<div class='ok-msg'> Sesión finalizada </div>";
header('refresh:3;url=index.php');
?>