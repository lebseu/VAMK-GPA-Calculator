$(document).ready(function() 
		{
			$("#submit").click(function(event)
			{
				$("#form").hide();
				$("#notice").hide();
				$("#loading").show();

				if($("#is_subscribed").is(':checked')){
					is_subscribed = 1;
				}else{
					is_subscribed = 0;
				}
				$.post("calcAjax.php", 
				{
					username: $("#username").val(),
					password: $("#password").val(),
					is_subscribed: is_subscribed
				},
				function(data, status){
					$("#result").html(data);
					$("#loading").hide();
					//GPA Counting Animation
					var options = {
						  useEasing : true,
						  useGrouping : true,
						  separator : ',',
						  decimal : '.',
						  prefix : '',
						  suffix : ''
					};
					var gpa = $("#getGpa").text();
					var gpaCountUp = new CountUp("gpaValue", 0, gpa, 3, 3, options);
					gpaCountUp.start();

					//Courses Table Sorting
					$("#coursesTable").tablesorter(); 
				}
				
				);


			}
			);




			
		} 
		); 