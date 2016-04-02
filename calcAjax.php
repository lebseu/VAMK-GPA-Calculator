<?php
putenv('LANG=en_US.UTF-8'); 
$username = $_REQUEST['username'];
$password = $_REQUEST['password'];
$isSubscribed = $_REQUEST['is_subscribed'];
$cmd = "python3 py/calcGPAByWeb.py $username $password $isSubscribed";

echo shell_exec($cmd);
?> 

