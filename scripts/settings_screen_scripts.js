var currentChoice = 2;

function addLoadEvent(func) 
{
    var oldonload = window.onload;
    if (typeof window.onload != 'function') 
    {    
        window.onload = func;
    } 
    else 
    {
        window.onload = function() 
        {
            if (oldonload) 
            {
                oldonload();
            }
            func();
        };
    }
}

function returnToMenu()
{
	window.location.replace('/');
}

function submitChanges()
{
    var response = null;
    var xmlHttp = new XMLHttpRequest();
    
    function onSubmitResponse()
    {
        if(xmlHttp.readyState==4)
        {
            response = JSON.parse(xmlHttp.responseText);
            if(response.success)
                document.getElementById("change_ack").innerHTML = "Changes Recieved!";
            else
                document.getElementById("change_ack").innerHTML = "Changes not Recieved"; 
        }
    }

    var url = "/set_visibility";
    xmlHttp.open("POST", url, false);
    var info = {"visibility" : currentChoice};
    xmlHttp.onreadystatechange = onSubmitResponse;
	xmlHttp.send(JSON.stringify(info));
    while(response==null){}
}

function getSelection()
{
    var response = null;
    var xmlHttp = new XMLHttpRequest();
    
    function onResponse()
    {
        if(xmlHttp.readyState==4)
        {
            response = JSON.parse(xmlHttp.responseText);
            currentChoice = response.visibility;
            setSelection(response.visibility);
        }
    }

    var url = "/get_visibility";
    xmlHttp.open("POST", url, false);
    xmlHttp.onreadystatechange = onResponse;
	xmlHttp.send(null);
    while(response==null){}
}

function setSelection(visibility)
{
    document.getElementById(visibility.toString()).checked = true;
}

function clickedSelection(val)
{
    if(val == "anon")
        currentChoice = 0;
    else if(val == "initials")
        currentChoice = 1;
    else if(val == "first_initials")
        currentChoice = 2;
    else
        currentChoice = 3;
}

addLoadEvent(getSelection);
