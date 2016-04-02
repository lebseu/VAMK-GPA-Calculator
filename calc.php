<!DOCTYPE html>
<html>

<head>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<meta charset="utf-8">

	<meta property="fb:app_id"        content="780878985307315" />
	<meta property="og:url"           content="https://likai.ren/vamk-gpa/" />
	<meta property="og:type"          content="website" />
	<meta property="og:title"         content="VAMK GPA Calculator" />
	<meta property="og:description"   content="An easy way to check and save your transcript." />
	<meta property="og:image"         content="https://likai.ren/vamk-gpa/img/vamk_share.jpg" />
	
	<link rel="stylesheet" type="text/css" href="css/vamk.css">
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css">

	<script src="https://code.jquery.com/jquery-1.11.3.min.js"></script>
	<script src="js/jquery.tablesorter.min.js"></script>
	<script src="js/countUp.min.js"></script>
	<script src="js/vamk.js"></script>
	<script src="js/jquery.base64.js"></script>
	<script src="js/tableExport.js"></script>
	<title>VAMK GPA Calculator</title>
</head>

<body>
	<div id="fb-root"></div>
	<script>
		<!-- Load Facebook SDK for JavaScript -->
		(function(d, s, id) {
			var js, fjs = d.getElementsByTagName(s)[0];
			if (d.getElementById(id)) return;
			js = d.createElement(s); js.id = id;
			js.src = "//connect.facebook.net/en_GB/sdk.js#xfbml=1&version=v2.4&appId=780878985307315";
			fjs.parentNode.insertBefore(js, fjs);
		}(document, 'script', 'facebook-jssdk'));

		<!-- Show password -->
	</script>
	
	<div class="header">
		<h1>REPORT CARD <i class="fa fa-table fa" onclick="$('#coursesTable').tableExport({type:'excel',escape:'false', tableName:'transcript_vamk'});"></i></h1>
		<p><a href="http://www.puv.fi/en/"><img src="img/vamk.png"></a></p>
		<div class="fb-like" data-href="https://likai.ren/vamk-gpa/" data-layout="standard" data-action="like" data-show-faces="true" data-share="true" data-colorscheme="dark" data-width="250"></div>
	</div>

	<?php
	putenv('LANG=en_US.UTF-8'); 
	$stuNum = $_POST['stu_id'];
	$password = $_POST['password'];

	if(!empty($_POST['is_subscribed'])){
		$isSubscribed = 1;
	}else{
		$isSubscribed = 0;
	}
	$cmd = "python3 py/calcGPAByWeb.py $stuNum $password $isSubscribed";

	echo shell_exec($cmd);
	?> 


	<div class="footer">
		<p>© Copyright 2015 <a href="https://likai.ren">Likai Ren</a></p>
	</div>

</body>
</html>
