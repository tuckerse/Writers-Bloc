function statusCheck()
{
	var response = null;
	var xmlHttp = new XMLHttpRequest();

	function responseRecieved()
	{
		if(xmlHttp.readyState == 4)
		{
			response = JSON.parse(xmlHttp.responseText);
			var deleted = response.deleted;
			if(deleted)
				window.location.replace("/game_deleted_error");
			var num_players = response.num_players;
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

	var url = "/game_status";
	var info = {"game_id" : game_id};
	xmlHttp.open("POST", url, false);
	xmlHttp.setRequestHeader("Content-type", "application/json");
	xmlHttp.onreadystatechange = responseRecieved;
	xmlHttp.send(JSON.stringify(info));
	while(response == null){}
}

function startEarly()
{
	if(game_id == null)
		return;
	window.location.replace("/start_early?game_id=" + encodeURIComponent(game_id));
	return;
}

function returnToMenu()
{
	var xmlHttp = new XMLHttpRequest();
	var url = "/cancel_game";
	var info = {"game_id" : game_id};
	xmlHttp.open("POST", url, false);
	xmlHttp.setRequestHeader("Content-type", "application/json");
	xmlHttp.send(JSON.stringify(info));
	window.location.replace('/');
}

var intervalID = window.setInterval(statusCheck, 5000);
