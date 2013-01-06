function buttonClicked()
{
	if(document.getElementById("selection").value != null)
	{
		joined = joinGame(document.getElementById("selection").value);
	}
	else
		document.getElementById("error_area").innerHTML = "Invalid Game Selection";	
}

function joinGame(game_id)
{
	var response = null;
	function onResponse()
	{
		if(xmlHttp.readyState == 4)
		{
			response = JSON.parse(xmlHttp.responseText);
			response = response.valid;
		}
	}
	var xmlHttp = new XMLHttpRequest();
	var info = {"game_id" : game_id};
	var url = "/join_game";
	xmlHttp.open("POST", url, false);
	xmlHttp.onreadystatechange = onResponse;
	xmlHttp.send(JSON.stringify(info));
	while(response == null) {}
	if(response == "v")
		window.location.replace("/waiting_to_start?game_id=" + encodeURIComponent(game_id));
	else
		document.getElementById("error_area").innerHTML = "Couldn't join that game";		
}

function returnToMenu()
{
	window.location.replace('/');
}

function refreshLobby()
{
	var response = null;
	
	function refreshLobbyRecieved()
	{
		if(xmlHttp.readyState == 4)
		{
			response = JSON.parse(xmlHttp.responseText);
			updateLobby(response.games);
		}
	}

	var xmlHttp = new XMLHttpRequest();
	var url = "/get_lobby";
	xmlHttp.open("POST", url, false);
	xmlHttp.onreadystatechange = refreshLobbyRecieved;
	xmlHttp.send(null);
	while(response == null){}
}

function updateLobby(gameList)
{
	var tempString = "";
	tempString= "<select id=\"selection\" size=\"10\" style=\"height:350px;width:500px;overflow-y: scroll;overflow-x: scroll;border-style: solid; border-width: 1px;\">";
	for(entry in gameList)
		tempString += "<option value=\"" + gameList[entry].game_id + "\"> <b>Game ID: " + gameList[entry].game_id + " | Length: " + gameList[entry].length + " | Current Players: " + gameList[entry].current_players + "/8 | End Sentence: " + gameList[entry].end_sentence + " </b></option>";

	document.getElementById("select_game").innerHTML = tempString;
}
