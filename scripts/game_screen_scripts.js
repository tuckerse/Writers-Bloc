var seconds = 0;	
var phase = "";
var storedChat = "";
var submitted = false;
var currentChoice = "";
var currentWinner = "";
var updatedStory = "";
var xmlHttp = null;
var num_phases = 0;
var winningData;
var scoreInfo;
document.onkeypress = processKey;

function processKey(e)
{
 	if (e == null)
   		e = window.event;
  	if (e.keyCode == 13)  
	{
    	var element = document.activeElement;
		if(element.id == "next_part")
			submitNextPart();
		return false;
  	}
}

function submitNextPart()
{
	function onResponseNextPart()
	{
		if(xmlHttp.readyState == 4)
		{
			var response = xmlHttp.getResponseHeader("success");
			if(response == "s")
			{
				document.getElementById("submit_button").disabled = "true";
				document.getElementById("next_part").value = "The Moving Finger writes; and, having writ, Moves on.";
				document.getElementById("next_part").disabled = "true";
			}
		}
	}
	var next_part = document.getElementById("next_part").value;
	var url = "/game_screen";
	var info = {"game_id": game_id, "next_part": next_part};
	xmlHttp = new XMLHttpRequest();
	xmlHttp.onreadystatechange = onResponseNextPart;
	xmlHttp.open("POST", url, true);
	xmlHttp.setRequestHeader("Content-type", "application/json");
	xmlHttp.send(JSON.stringify(info));	
}

function statusCheck()
{
	var response = null;

	function onResponseStatusCheck()
	{
		if(xmlHttp.readyState == 4)
		{
			response = JSON.parse(xmlHttp.responseText);
			phase = response.phase;
			seconds = response.seconds_left + 1;
			num_phases = response.num_phases;
		}
	}
	

	var url = "/game_status";
	var info = {"game_id" : game_id};
	xmlHttp = new XMLHttpRequest();
	xmlHttp.open("POST", url, false);
	xmlHttp.onreadystatechange = onResponseStatusCheck;
	xmlHttp.setRequestHeader("Content-type", "application/json");
	xmlHttp.send(JSON.stringify(info));
	while(response == null) {}
	if(num_phases != 0)
		document.getElementById("story_title").innerHTML = "The Story So Far... Turn " + (num_phases);
	return;
}

function tick()
{
	seconds = seconds - 1;
	if(seconds == 0)
	{
		if(phase == "s")
		{	
			var response = acknowledgeFinishSubmission();
			if(response == "v")
			{
				statusCheck();
				setToVotingPhase();
			}	
			else
			{
				document.getElementById("timer").innerHTML = "Your game seems to have finished before everyone else... Time Lord?";
				seconds = 1;
			}								
		}	
		else if(phase == "v")
		{
			var response = acknowledgeFinishVote();
			if(response == "v")
			{
				statusCheck();
				setToDisplayPhase();
			}
			else
			{
				document.getElementById("timer").innerHTML = "Your game seems to have finished before everyone else... Time Lord?";
				seconds = 1;
			}
		}	
		else if(phase == "d")
		{
			var response = acknowledgeFinishDisplay();
			if(response == "v")
			{
				updateUserInfo();
				statusCheck();
				if(num_phases > 10)
				{
					setToEndVotingPhase();
				}
				else
					setToSubmissionPhase();		
			}

			else
			{
				document.getElementById("timer").innerHTML = "Your game seems to have finished before everyone else... Time Lord?";
				seconds = 1;
			}
		}	
		else if(phase == "f")
		{
			var response = acknowledgeFinishEndVote();
			if(response == "e")
				endGame();
			else if(response == "c")
			{
				statusCheck();
				setToSubmissionPhase();
			}
			else
			{
				document.getElementById("timer").innerHTML = "Your game seems to have finished before everyone else... Time Lord?";
				seconds = 1;
			}
		}
	}	
	if(phase == "s")
	{
		document.getElementById("timer").innerHTML = "Submission Time Remaining: " + seconds + " seconds.";
	}
	else if(phase == "v")
	{
		document.getElementById("timer").innerHTML = "Voting Time Remaining: " + seconds + " seconds.";
	}
	else if(phase == "d")
	{
		document.getElementById("timer").innerHTML = "Displaying Winning Segment: " + seconds + " seconds.";
	}
	else if(phase == "f")
	{
		document.getElementById("timer").innerHTML = "End Voting Time Remaining: " + seconds + " seconds.";
	}
}

function endGame()
{
	document.getElementById("story_title").innerHTML = "And so it was written...";
	document.getElementById("submit_button").disabled = true;
	document.getElementById("next_part").value = "Chat will remain open for five minutes.";
	document.getElementById("next_part").disabled = true;
	document.getElementById("chatbox").innerHTML = storedChat;
	document.getElementById("timer").innerHTML = "";
	window.clearInterval(timerID);
}

function acknowledgeFinishEndVote()
{
	var response = null;
	function onResponseFinishSubmission()
	{
		if(xmlHttp.readyState == 4)
		{
			response = xmlHttp.getResponseHeader("response");
		}
	}
	var url = "/end_vote_complete_verification?game_id=" + encodeURIComponent(game_id);
	var info = {"game_id" : game_id};
	xmlHttp = new XMLHttpRequest();
	xmlHttp.open("POST", url, false);
	xmlHttp.onreadystatechange = onResponseFinishSubmission;
	xmlHttp.setRequestHeader("Content-type", "application/json");
	xmlHttp.send(JSON.stringify(info));
	while(response == null){}
	return response;
}

function setToEndVotingPhase()
{
	document.getElementById("story").innerHTML = updatedStory;
	document.getElementById("chatbox").innerHTML = "<form>";
	document.getElementById("chatbox").innerHTML += "Would you like to continue the story?<br>";
	document.getElementById("chatbox").innerHTML += "<input type=\"radio\" name=\"end_vote_selection\" value=\"0\" onclick=\"clickedSelection(this.value)\" /> Yes<br>";
	document.getElementById("chatbox").innerHTML += "<input type=\"radio\" name=\"vote_selection\" value=\"1\" onclick=\"clickedSelection(this.value)\" /> No<br>";
	document.getElementById("chatbox").innerHTML += "<form/>";
	document.getElementById("chatbox").innerHTML += "<input id=\"end_vote_button\" type=\"button\" value=\"Vote\" onclick=\"submitEndVote()\"/>";
}

function submitEndVote()
{
	var response = null;
	function onResponseEndVote()
	{
		if(xmlHttp.readyState == 4)
		{
			response = xmlHttp.getResponseHeader("response");
		}
	}
	var url = "/cast_end_vote?game_id=" + encodeURIComponent(game_id) + "&selection=" + encodeURIComponent(currentChoice);
	xmlHttp = new XMLHttpRequest();
	xmlHttp.open("POST", url, false);
	xmlHttp.onreadystatechange = onResponseEndVote;
	xmlHttp.send(null);
	while(response == null){}
	if(response == "s")
	{
		document.getElementById("end_vote_button").disabled = true;
		document.getElementById("end_vote_button").value = "Vote cast";
	}
	else
		alert("Vote not recieved properly, try again?");
}

function acknowledgeFinishSubmission()
{
	var response = null;
	function onResponseFinishSubmission()
	{
		if(xmlHttp.readyState == 4)
		{
			response = xmlHttp.getResponseHeader("completed");
		}
	}
	var url = "/submission_complete_verification";
	var info = {"game_id" : game_id};
	xmlHttp = new XMLHttpRequest();
	xmlHttp.open("POST", url, false);
	xmlHttp.onreadystatechange = onResponseFinishSubmission;
	xmlHttp.setRequestHeader("Content-type", "application/json");
	xmlHttp.send(JSON.stringify(info));
	while(response == null){}
	return response;			
}

function getChoices()
{
	var choices = null;
	var response;

	function onChoicesResponse()
	{
		if(xmlHttp.readyState == 4)
		{
			response = JSON.parse(xmlHttp.responseText);
			choices = response.choices;				
		}
	}

	var url = "/get_choices";
	var info = {"game_id" : game_id};
	xmlHttp = new XMLHttpRequest();
	xmlHttp.open("POST", url, false);
	xmlHttp.onreadystatechange = onChoicesResponse;
	xmlHttp.setRequestHeader("Content-type", "application/json");
	xmlHttp.send(JSON.stringify(info));
	while(choices == null){}
	return choices;
}

function submitVote()
{
	var url = "/vote?game_id=" + encodeURIComponent(game_id) + "&part_voted=" + encodeURIComponent(currentChoice);
	xmlHttp = new XMLHttpRequest();
	xmlHttp.open("POST", url, false);
	xmlHttp.send(null);
	var response = xmlHttp.getResponseHeader("response");
	if(response == "s")
	{
		document.getElementById("submit_vote_button").disabled = true;
		document.getElementById("submit_vote_button").value = "Vote cast";
	}
	else
		alert("Vote not recieved properly, try again?");
}

function clickedSelection(val)
{
	currentChoice = val;
}

function setToVotingPhase()
{
	storedChat = document.getElementById("chatbox").innerHTML;
	document.getElementById("next_part").value = "Chat Disabled During Voting Phase.";
	var choices = getChoices();
	document.getElementById("chatbox").innerHTML = "<form>";
	for(i = 0; i < choices.length; i++)
	{
		document.getElementById("chatbox").innerHTML += "<input type=\"radio\" name=\"vote_selection\" value=\"" + i + "\" onclick=\"clickedSelection(this.value)\" />" + choices[i]  + "<br>";
	}
	document.getElementById("chatbox").innerHTML += "<form/>";
	document.getElementById("chatbox").innerHTML += "<input id=\"submit_vote_button\" type=\"button\" value=\"Vote\" onclick=\"submitVote()\"/>";
}

function acknowledgeFinishVote()
{
	var response = null;

	function recievedAckFinishVote()
	{
		if(xmlHttp.readyState == 4)
		{
			if(xmlHttp.getResponseHeader("completed") == "v")
			{
				response = JSON.parse(xmlHttp.responseText);
				winningData = response.winning_data;
				currentWinner = xmlHttp.getResponseHeader("recent_winner");
			}
			else
				response = 0;
		}
	}
	var url = "/vote_complete_verification?game_id=" + encodeURIComponent(game_id);
	xmlHttp = new XMLHttpRequest();
	xmlHttp.open("POST", url, false);
	xmlHttp.onreadystatechange = recievedAckFinishVote;
	xmlHttp.send(null);
	while(response == null) {}
	return xmlHttp.getResponseHeader("completed");			
}

function setToDisplayPhase()
{
	document.getElementById("chatbox").innerHTML = "Winning Segment: " + currentWinner + "<br>";
	var list = new Array();
	for(entry in winningData)
	{
		list[winningData[entry].position] = "<b>" + winningData[entry].position + "</b>. " + winningData[entry].sentence + " | Score: " + winningData[entry].score + " | Author: " + winningData[entry].user_name;
	}
	for(user_entry in list)
	{
		document.getElementById("chatbox").innerHTML += list[user_entry] + "<br>";
	}
}

function setToSubmissionPhase()
{
	document.getElementById("chatbox").innerHTML = storedChat;
	storedChat = "";
	document.getElementById("story").innerHTML = updatedStory;
	document.getElementById("next_part").value = "";
	document.getElementById("next_part").disabled = false;
	document.getElementById("submit_button").disabled = false;
}

function acknowledgeFinishDisplay()
{
	var response = null;
	var parsed = null;
	function recievedResponseFinishDisplay()
	{
		if(xmlHttp.readyState == 4)
		{
			response = 	xmlHttp.getResponseHeader("response");
			if(response == "v")
			{
				parsed = JSON.parse(xmlHttp.responseText);
				updatedStory = parsed.updated_story;
				scoreInfo = parsed.scores;
				updateUserInfo();
			}
		}
	}
	var url = "/display_complete_verification?game_id=" + encodeURIComponent(game_id);
	xmlHttp = new XMLHttpRequest();
	xmlHttp.open("POST", url, false);
	xmlHttp.onreadystatechange = recievedResponseFinishDisplay;
	xmlHttp.send(null);
	while(response == null) {}
	return response;			
}

function updateUserInfo()
{
	var list = new Array();
	for(entry in scoreInfo)
	{
		list[scoreInfo[entry].position - 1] = "<b>" + (scoreInfo[entry].position - 1) + ".</b> (" + scoreInfo[entry].score + ") " + scoreInfo[entry].user_name;
	}
	document.getElementById("userbartext").innerHTML = "Scoreboard:<br>";
	for(user_entry in list)
	{
		document.getElementById("userbartext").innerHTML += list[user_entry] + "<br>";
	}	
}

var timerID = window.setInterval(tick, 1000);
statusCheck();	

