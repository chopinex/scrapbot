<?php 

$logins = array('player1' => 'ch0053_wi531y');

$Username = isset($_POST['usuario']) ? $_POST['usuario'] : '';
$Password = isset($_POST['pass']) ? $_POST['pass'] : '';
if (isset($logins[$Username]) && $logins[$Username] == $Password){
  session_start();
  $_SESSION['Username']=$logins[$Username];
  header("Location: main.php");
  exit();
} else {

/* Login failed display message */
echo "<span style='color:red'>Invalid Login Details</span>";
}

?>