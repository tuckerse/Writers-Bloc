var seconds = 0;	
var phase = "";
var votingDirections = "Voting Directions";
var gameRules = "Game rules";
var submissionDirections = "Submission Directions";
var submitted = false;
var currentChoice = "";
var currentWinner = "";
var updatedStory = "";
var xmlHttp = null;
var num_phases = 0;
var winningData;
var scoreInfo;
var oldPhase;
var refreshDelay = 5;
var stagger = Math.floor(Math.random()*5);
var recentlySubmitted = "";
var profiles;
var afks;
var hasSubmitted = false;
var hasVoted = false;
document.onkeypress = processKey;

function processKey(e)
{
 	if (e == null)
   		e = window.event;
  	if (e.keyCode == 13)  
	{
    	var element = document.activeElement;
		if(element.id == "button_input")
        {
            if(phase == "s")
			    submitNextPart();
            else if (phase == "v")
                submitVote();
        }
		return false;
  	}
}

function buttonPressed()
{
    if(phase == "s")
        submitNextPart();
    else if (phase == "v")
        submitVote();
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
				document.getElementById("button_input").disabled = "true";
                document.getElementById("submit_button").value = "Sentence Submitted";
                hasSubmitted = true;
			}
		}
	}
	var next_part = document.getElementById("button_input").value;
    if(next_part != "")
    {
        document.getElementById("submit_button").disabled = "true";
	    recentlySubmitted = next_part;
	    var url = "/game_screen";
	    var info = {"game_id": game_id, "next_part": next_part};
	    xmlHttp = new XMLHttpRequest();
	    xmlHttp.onreadystatechange = onResponseNextPart;
	    xmlHttp.open("POST", url, true);
	    xmlHttp.setRequestHeader("Content-type", "application/json");
	    xmlHttp.send(JSON.stringify(info));	
    }
}

function statusCheck()
{
	var response = null;

	function onResponseStatusCheck()
	{
		if(xmlHttp.readyState == 4)
		{
			response = JSON.parse(xmlHttp.responseText);
			if(response.deleted)
				window.location.replace("/game_deleted_error");
            if(phase == "")
            {
                if (phase == "s")
                    setToSubmissionPhase();
                else if(response.phase == "v")
                    setToVotingPhase();
                else if(response.phase == "d")
                    setToDisplayPhase(); 
                phase = response.phase;
            }
            else
			    phase = response.phase;
			seconds = response.seconds_left + 1;
			num_phases = response.num_phases;
            if(phase == "s" || phase == "v")
            {
                try
                {
                    document.getElementById("waiting_on").innerHTML = "Still waiting on " + response.waiting_on + " player(s).";
                }
                catch(err){}
            }
            else
                document.getElementById("waiting_on").innerHTML = "";
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
	if(phase == "e")
		window.clearInterval(timerID);
	seconds = seconds - 1;
	if(seconds == 0)
	{
		phaseChangeLogic();
	}
	else if(seconds%(refreshDelay+stagger) == 0)
	{
		oldPhase = phase;
		statusCheck();
		if(phase != oldPhase)
		{
            getUpdatedUserInfo();
            updateUserInfo();
            hasSubmitted = false;
            hasVoted = false;
			oldPhaseChangeLogic();	
		}
	}	
	if(phase == "s")
	{
		document.getElementById("timer").innerHTML = "Submission Time Remaining: " + seconds + " second(s).";
        if(seconds == 1 && !hasSubmitted)
        {
            submitNextPart();
        }
	}
	else if(phase == "v")
	{
		document.getElementById("timer").innerHTML = "Voting Time Remaining: " + seconds + " second(s).";
        if(seconds == 1  && !hasVoted && (currentChoice != ""))
        {
            submitVote();
        }
	}
	else if(phase == "d")
	{
		document.getElementById("timer").innerHTML = "Displaying Winning Segment: " + seconds + " second(s).";
	}
}

function oldPhaseChangeLogic()
{
	if(oldPhase == "s")
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
	else if(oldPhase == "v")
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
	else if(oldPhase == "d")
	{
		var response = acknowledgeFinishDisplay();
		if(response == "v")
		{
			statusCheck();
			if(phase == "e")
			{
                endGame();
			}
			else if(phase == "s")
				setToSubmissionPhase();		
		}

		else
		{
			document.getElementById("timer").innerHTML = "Your game seems to have finished before everyone else... Time Lord?";
			seconds = 1;
		}
	}	
}

function phaseChangeLogic()
{
	if(phase == "s")
	{	
		var response = acknowledgeFinishSubmission();
		if(response == "v")
		{
			statusCheck();
			setToVotingPhase();
		}	
        else if(response == "d")
            window.location.replace("/game_deleted_error")
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
			statusCheck();
			if(phase == "e")
			{
                endGame();
			}
			else if(phase == "s")
				setToSubmissionPhase();		
		}
		else
		{
			document.getElementById("timer").innerHTML = "Your game seems to have finished before everyone else... Time Lord?";
			seconds = 1;
		}
	}	
}

function endGame()
{
	phase = "e";
    var data = getWinner();
	document.getElementById("story_title").innerHTML = "And so it was written...";
	document.getElementById("submit_button").disabled = true;
    //document.getElementById("infobox").innerHTML = getEndGameText();
    document.getElementById("infobox").innerHTML = data.winner + "is first author with " + data.points + " points!";
	document.getElementById("button_input").value = "Story Finished.";
	document.getElementById("button_input").disabled = true;
	document.getElementById("timer").innerHTML = "<form><INPUT TYPE=\"button\" VALUE=\"Return to Menu\" onClick=\"window.location.replace(\'/\')\"></form>";
    getUpdatedUserInfo();
    updateUserInfo();
}

/*
Removed for release

function getEndGameText()
{
    var response = null;
    function onResponseEndGameText()
    {
        if(xmlHttp.readyState == 4)
        {
             response = JSON.parse(xmlHttp.responseText);
        }
    }

    var url = "/get_end_text?game_id=" + encodeURIComponent(game_id);
    xmlHttp = new XMLHttpRequest();
    xmlHttp.open("POST", url, false);
    xmlHttp.onreadystatechange = onResponseEndGameText;
    xmlHttp.setRequestHeader("Content-type", "application/json");
    xmlHttp.send(null);
    while(response == null){}
    return response.end_text;
}
*/

function getWinner()
{
    var response = null;
    function onResponseWinner()
    {
        if(xmlHttp.readyState == 4)
            reponse = JSON.parse(xmlHttp.responseText);
    }

    var url = "/get_winner?game_id=" + encodeURIComponent(game_id);
    xmlHttp = new XMLHttpRequest();
    xmlHtpp.open("POST", url, false);
    xmlHttp.onreadystatechange = onResponseWinner;
    xmlHttp.setRequestHeader("Content-type", "application/json");
    xmlHttp.send(null);
    while(response == null){}
    return response;
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
    if(currentChoice != "")
    {
	    var url = "/vote?game_id=" + encodeURIComponent(game_id) + "&part_voted=" + encodeURIComponent(currentChoice);
	    xmlHttp = new XMLHttpRequest();
	    xmlHttp.open("POST", url, false);
	    xmlHttp.send(null);
	    var response = xmlHttp.getResponseHeader("response");
	    if(response == "s")
	    {
		    document.getElementById("submit_button").value = "Vote cast - Change vote?";
            hasVoted = true;
	    }
	    else
		    alert("Vote not recieved properly, try again?");
    }
}

function clickedSelection(val)
{
	currentChoice = val;
}

function setToVotingPhase()
{
	document.getElementById("button_input").value = votingDirections;
    document.getElementById("submit_button").value = "Cast Vote";
    document.getElementById("submit_button").disabled = false;
	var choices = getChoices();
    var hasSelected = false;
	document.getElementById("infobox").innerHTML = "<form>";
	for(i = 0; i < choices.length; i++)
	{
		if(choices[i] == recentlySubmitted)
			document.getElementById("infobox").innerHTML += "<input type=\"radio\" name=\"vote_selection\" value=\"" + i + "\" onclick=\"clickedSelection(this.value)\" disabled=\"true\"/>" + choices[i]  + "<br>";
		else
        {
            if(!hasSelected)
            {
			    document.getElementById("infobox").innerHTML += "<input type=\"radio\" name=\"vote_selection\" value=\"" + i + "\" onclick=\"clickedSelection(this.value)\" selected=\"selected\"/>" + choices[i]  + "<br>";
                hasSelected = true;
            }
            else
                document.getElementById("infobox").innerHTML += "<input type=\"radio\" name=\"vote_selection\" value=\"" + i + "\" onclick=\"clickedSelection(this.value)\"/>" + choices[i]  + "<br>";
        }
	}
	document.getElementById("infobox").innerHTML += "<form/>";
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
	document.getElementById("infobox").innerHTML = "Winning Segment: " + currentWinner + "<br>";
    document.getElementById("button_input").value = "";
    document.getElementById("submit_button").value = "Display Phase";
    document.getElementById("submit_button").disabled = true;
	var list = new Array();
	for(entry in winningData)
	{
		list[winningData[entry].position - 1] = "<b>" + winningData[entry].position + "</b>. " + winningData[entry].sentence + " | Score: " + winningData[entry].score_votes + "(Votes) + " + winningData[entry].score_bonus + "(Bonus)  = " + winningData[entry].score + "(Total) | Author: " + winningData[entry].user_name;
	}
	for(user_entry in list)
	{
		document.getElementById("infobox").innerHTML += list[user_entry] + "<br>";
	}
}

function setToSubmissionPhase()
{
	document.getElementById("infobox").innerHTML = gameRules + "<br>" + submissionDirections;
	storedChat = "";
    if(phase != "")
	    document.getElementById("story").innerHTML = updatedStory;
	document.getElementById("button_input").value = "";
	document.getElementById("button_input").disabled = false;
	document.getElementById("submit_button").disabled = false;
    document.getElementById("submit_button").value = "Submit";
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
				profiles = parsed.profiles;
                afks = parsed.afks;
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

function getUpdatedUserInfo()
{
    var parsed = null;
    
    function recievedUpdateResponse()
    {
        if(xmlHttp.readyState == 4)
        {
            parsed = JSON.parse(xmlHttp.responseText);
            scoreInfo = parsed.scores;
            profiles = parsed.profiles;
            afks = parsed.afks;
        }
    }

    var url = "/update_user_info?game_id=" + encodeURIComponent(game_id);
    xmlHttp = new XMLHttpRequest();
    xmlHttp.open("POST", url, false);
    xmlHttp.onreadystatechange = recievedUpdateResponse;
    xmlHttp.send(null);
    while(parsed  == null) {}
}

function updateUserInfo()
{
	var list = new Array();
	for(entry in scoreInfo)
	{
        if(afks[entry])
		    list[scoreInfo[entry].position - 1] = "<img src=\"" + profiles[entry] + "\" width=\"25\" height=\"25\"/><b>" + scoreInfo[entry].position + ".</b> (AFK)(" + scoreInfo[entry].score + ") " + scoreInfo[entry].user_name;
        else
            list[scoreInfo[entry].position - 1] = "<img src=\"" + profiles[entry] + "\" width=\"25\" height=\"25\"/><b>" + scoreInfo[entry].position + ".</b> (" + scoreInfo[entry].score + ") " + scoreInfo[entry].user_name;
	}
	document.getElementById("userbartext").innerHTML = "Scoreboard:<br>";
	for(user_entry in list)
	{
		document.getElementById("userbartext").innerHTML += list[user_entry] + "<br>";
	}	
}

var timerID = window.setInterval(tick, 1000);
statusCheck();	

