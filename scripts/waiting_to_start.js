var intervalID = window.setInterval(statusCheck, 5000);

function statusCheck()
{
	var repsonse = null;
	var xmlHttp = new XMLHttpRequest();

	function responseRecieved()
	{
		if(xmlHttp.readyState == 4)
		{
			response = JSON.parse(xmlHttp.responseText);
			var num_players = response.num_players;
			var deleted = response.deleted;
			if(deleted)
				window.location.replace("/game_deleted_error");
			document.getElementById("current_players").innerHTML = num_players + "/" + MAX_PLAYERS + " Players<br>Current Players:<br>";
			var players = response.players;
			for(i in players)
			{
				document.getElementById("current_players").innerHTML += players[i] + "<br>";
			}
			var started = response.started;
			if(started == "y")
			{
                forward = true;
				window.location.replace("/game_screen?game_id=" + encodeURIComponent(game_id));
			}
		}
	}

	var url = "/game_status?anonymous=1";
	var info = {"game_id" : game_id};
	xmlHttp.open("POST", url, false);
	xmlHttp.setRequestHeader("Content-type", "application/json");
	xmlHttp.onreadystatechange = responseRecieved;
	xmlHttp.send(JSON.stringify(info));
	while(response==null){}
}

function returnToMenu()
{
    forward = true;
	var xmlHttp = new XMLHttpRequest();
	var url = "/leave_before_start";
	var info = {"game_id" : game_id, "user_id" : user_id};
	xmlHttp.open("POST", url, false);
	xmlHttp.setRequestHeader("Content-type", "application/json");
	xmlHttp.send(JSON.stringify(info));
	window.location.replace('/');
}

function unload()
{
    var xmlHttp = new XMLHttpRequest();
    var url = "/leave_before_start";
    var info = {"game_id" : game_id, "user_id" : user_id};
    xmlHttp.open("POST", url, false);
    xmlHttp.setRequestHeader("Content-type", "application/json");
    xmlHttp.send(JSON.stringify(info));
}
