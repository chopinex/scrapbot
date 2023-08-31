<?php
# Si no entiendes el código, primero mira a login.php
# Iniciar sesión para usar $_SESSION
session_start();
# Y ahora leer si NO hay algo llamado usuario en la sesión,
# usando empty (vacío, ¿está vacío?)
# Recomiendo: https://parzibyte.me/blog/2018/08/09/isset-vs-empty-en-php/
if (empty($_SESSION['Username'])) {
    # Lo redireccionamos al formulario de inicio de sesión
    header("Location: index.php");
    # Y salimos del script
    exit();
}
# No hace falta un else, pues si el usuario no se loguea, todo lo de abajo no se ejecuta
?>
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" type="text/css" href="styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300&display=swap" rel="stylesheet">
    <title>Scrapper</title>
</head>
<body>
<!-- Por cierto, también se puede usar HTML como en todos los scripts de PHP-->
<p>
    Control de scrapping
</p>

<?php
$lugares=array('Lima' => 0,'Arequipa' => 0,'Callao' => 0,'La Libertad' => 0,'Piura' => 0,'Ica' => 0,'Lambayeque' => 0,'Cusco' => 0,'Junin' => 0,'Ancash' => 0,'Cajamarca' => 0,'Puno' => 0);
$cnt=0;
foreach ($_POST['marcas'] as $selected) {
	if(array_key_exists($selected, $lugares))
		$lugares[$selected] = $_POST['valores'][$cnt];
		$cnt++;
}
$salida = implode(',',$lugares);
$output = shell_exec('which firefox');
if ($_POST['fuente']=="ct"){
	$cmd=escapeshellcmd("./realScrapper.py 1 '" . $salida . "' ".$_POST["bd"]);
}
if ($_POST['fuente']=="cv"){
	$cmd = escapeshellcmd("./realScrapper.py 2 ".$_POST["bd"]);
}
if ($_POST['fuente']=="bm"){
	$cmd = escapeshellcmd("./realScrapper.py 3 ".$_POST["valor"]. " ".$_POST["bd"]);
}
//$cmd=escapeshellcmd("xvfb-run ./seleniumTest.py");
if(isset($_POST['ejecutar'])) {

    echo "<div class='output'>";
    while (@ ob_end_flush());
    $proc = popen($cmd, 'r');
    echo '<pre>';
    while (!feof($proc))
    {
        echo fread($proc, 4096);
        @ flush();
    }
    echo '</pre>';
    /*ob_start();
    passthru($cmd);
    echo "<pre>" . htmlspecialchars(ob_get_clean()) . "</pre>";*/
    $_POST = array();
    echo "</div>";
}
?>
<!-- Y aprovechando, le indicamos al usuario un enlace para salir-->
<div class="tab">
	<button class="tablinks" onclick="openCity(event, 'Computrabajo')">Computrabajo</button>
	<button class="tablinks" onclick="openCity(event, 'Convocatorias')">Convocatorias</button>
	<button class="tablinks" onclick="openCity(event, 'Bumeran')">Bumeran</button>
</div>
<hr />

<form action="" method="post" id="wrapper">
    <label>Base de datos</label>
    <select name="bd">
        <option value="1" selected>Staging</option>
        <option value="2">Principal</option>
    </select>

	<div id="Computrabajo" class="tabcontent">
	    <table>
			<tr>
				<td><input type="checkbox" name="marcas[]" value="Lima" checked/></td><td><label>Lima</label></td><td><input type="number" name ="valores[]" min="0" max="100" value="10"/></td>
			</tr>
			<tr>
				<td><input type="checkbox" name="marcas[]" value="Arequipa" checked/></td><td><label>Arequipa</label></td><td><input type="number" name ="valores[]" min="0" max="100" value="10"/></td>
			</tr>
			<tr>
				<td><input type="checkbox" name="marcas[]" value="Callao" checked/></td><td><label>Callao</label></td><td><input type="number" name ="valores[]" min="0" max="100" value="10"/></td>
			</tr>
			<tr>
				<td><input type="checkbox" name="marcas[]" value="La Libertad" checked/></td><td><label>La Libertad</label></td><td><input type="number" name ="valores[]" min="0" max="100" value="10"/></td>
			</tr>
			<tr>
				<td><input type="checkbox" name="marcas[]" value="Piura" checked/></td><td><label>Piura</label></td><td><input type="number" name ="valores[]" min="0" max="100" value="10"/></td>
			</tr>
			<tr>
				<td><input type="checkbox" name="marcas[]" value="Ica" checked/></td><td><label>Ica</label></td><td><input type="number" name ="valores[]" min="0" max="100" value="10"/></td>
			</tr>
			<tr>
				<td><input type="checkbox" name="marcas[]" value="Lambayeque" checked/></td><td><label>Lambayeque</label></td><td><input type="number" name ="valores[]" min="0" max="100" value="10"/></td>
			</tr>
			<tr>
				<td><input type="checkbox" name="marcas[]" value="Cusco" checked/></td><td><label>Cusco</label></td><td><input type="number" name ="valores[]" min="0" max="100" value="10"/></td>
			</tr>
			<tr>
				<td><input type="checkbox" name="marcas[]" value="Junin" checked/></td><td><label>Junin</label></td><td><input type="number" name ="valores[]" min="0" max="100" value="10"/></td>
			</tr>
			<tr>
				<td><input type="checkbox" name="marcas[]" value="Ancash" checked/></td><td><label>Ancash</label></td><td><input type="number" name ="valores[]" min="0" max="100" value="10"/></td>
			</tr>
			<tr>
				<td><input type="checkbox" name="marcas[]" value="Cajamarca" checked/></td><td><label>Cajamarca</label></td><td><input type="number" name ="valores[]" min="0" max="100" value="10"/></td>
			</tr>
			<tr>
				<td><input type="checkbox" name="marcas[]" value="Puno" checked/></td><td><label>Puno</label></td><td><input type="number" name ="valores[]" min="0" max="100" value="10"/></td>
			</tr>
		</table>
	    <input type="hidden" name="fuente" value="ct"/>
	    <button type="submit" name="ejecutar">Realizar scrapping</button>
	</div>

	<div id="Convocatorias" class="tabcontent">
		<input type="hidden" name="fuente" value="cv"/>
		<button type="submit" name="ejecutar">Realizar scrapping</button>
	</div>

	<div id="Bumeran" class="tabcontent">
		<input type="hidden" name="fuente" id="stigma" value="bm"/>
		<input type="number" name ="valor" min="0" max="100" value="20"/>
		<button type="submit" name="ejecutar">Realizar scrapping</button>
	</div>	

</form>
<a href="logout.php">Cerrar sesión</a>
<script>
	document.getElementById('wrapper').addEventListener('change', function(event){
	    var elem = event.target;
	    const colas = new Array("Lima","Arequipa","Callao","La Libertad","Piura","Ica","Lambayeque","Cusco","Junin","Ancash","Cajamarca","Puno");
	    if(elem.name === "marcas[]"){
	         numero=colas.indexOf(elem.value);
	         document.getElementsByName('valores[]')[numero].disabled = !elem.checked;
	    }   
	});
	
	function openCity(evt, cityName) {
	  	// Declare all variables
	  	var i, tabcontent, tablinks;

	  	// Get all elements with class="tabcontent" and hide them
	  	tabcontent = document.getElementsByClassName("tabcontent");
	  	for (i = 0; i < tabcontent.length; i++) {
	    	tabcontent[i].style.display = "none";
	  	}

	  	// Get all elements with class="tablinks" and remove the class "active"
	  	tablinks = document.getElementsByClassName("tablinks");
	  	for (i = 0; i < tablinks.length; i++) {
	    	tablinks[i].className = tablinks[i].className.replace(" active", "");
	  	}

	  	// Show the current tab, and add an "active" class to the button that opened the tab
	  	document.getElementById(cityName).style.display = "block";
	  	evt.currentTarget.className += " active";
	  	if(cityName=="Computrabajo")
	  		document.getElementById('stigma').value="ct";
	  	if(cityName=="Convocatorias")
	  		document.getElementById('stigma').value="cv";
	  	if(cityName=="Bumeran")
	  		document.getElementById('stigma').value="bm";

	} 
</script>
</body>
</html>
