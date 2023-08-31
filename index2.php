<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" type="text/css" href="styles.css">
    <title>Scrapbot</title>
</head>
<body>
<p>
    Scrapping Bumeran
</p>

<?php
#$cmd="cd .. && source myenv/bin/activate && cd scrapper && python -u realScrapper.py " .$_POST["ligas"];
#$cmd = escapeshellcmd("./realScrapper.py " .$_POST["ligas"]);
$cmd = escapeshellcmd("./realScrapper.py");
if(isset($_POST['ejecutar'])) {
    /*echo '<div class="output"><pre>';
    ob_start();
    passthru($cmd);
    echo "<pre>" . htmlspecialchars(ob_get_clean()) . "</pre>";
    $_POST = array();
    echo '</div>';*/
    echo '<div class="output">';
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
    echo '</div>';
}
?>

<form action="" method="post" id="wrapper">
    <!--<input type="number" min="1" max="100" value="10" name="ligas"/>-->
    <button type="submit" name="ejecutar">Realizar scrapping</button>
</form>
</body>
</html>
