

/**
 * capture javaScript visualization and add it to DB
 */
function addVisualizationToDB() {
	var finalData = "{";
	for(var i=0, len=sessionStorage.length; i<len; i++) {
		var key = sessionStorage.key(i);
		var value = sessionStorage[key];
		finalData = finalData + "\""+ key + "\""+ ":" + "\""+value + "\"";
		finalData = finalData + ",";
	}
	finalData = finalData.substring(0,finalData.length-1);
	finalData = finalData + "}";
	if (finalData.length < 2) {
		finalData = "";
	}
	$("#JSVisualizationDetails").val(finalData);
	return true;
}


/**
 * check chapter count to enable/disable next and prev buttons
*/
function checkChapterCount(index)
{
	var count;
	if(index==1)
	{
		count=(parseInt(localStorage.getItem("chapterCount"))+1).toString();
		localStorage.setItem("chapterCount",count)
	}
	else
	{
		count=(parseInt(localStorage.getItem("chapterCount"))-1).toString();
		localStorage.setItem("chapterCount",count)
	}
}

/**
 * clear local storage 
 */
function clearLocalStorage()
{
	localStorage.clear();
}

/**
 *  google and facebook login functionalities
 */
var OAUTHURL    =   'https://accounts.google.com/o/oauth2/auth?';
var VALIDURL    =   'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=';
var SCOPE       =   'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email';
var CLIENTID    =   '448770529527.apps.googleusercontent.com';
var REDIRECT    =   'http://localhost:8080/stories/'
	var LOGOUT      =   'http://accounts.google.com/Logout';
var TYPE        =   'token';
var _url        =   OAUTHURL + 'scope=' + SCOPE + '&client_id=' + CLIENTID + '&redirect_uri=' + REDIRECT + '&response_type=' + TYPE;
var acToken;
var tokenType;
var expiresIn;
var user;
var loggedIn    =   false;

/**
 *  login using google
 */
function googleLogin() {
	var win         =   window.open(_url, "windowname1", 'width=800, height=600'); 
	var pollTimer   =   window.setInterval(function() { 
		try {
			if (win.document.URL.indexOf(REDIRECT) != -1) {
				window.clearInterval(pollTimer);
				var url =   win.document.URL;
				acToken =   gup(url, 'access_token');
				tokenType = gup(url, 'token_type');
				expiresIn = gup(url, 'expires_in');
				win.close();
				validateToken(acToken);
			}
		}
		catch(e) {
		}
	}, 500);
}

/**
 *  validate  google auth_token 
 */
function validateToken(token) {
	$.ajax({
		url: VALIDURL + token,
		data: null,
		success: function(responseText){  
			getUserInfo();
			loggedIn = true;
		},  
		dataType: "jsonp"  
	});
}
/**
 *   retrieve user information from google api
 */
function getUserInfo() {
	$.ajax({
		url: 'https://www.googleapis.com/oauth2/v1/userinfo?access_token=' + acToken,
		data: null,
		success: function(resp) {
			user    =   resp;
			var jsonObj = [];
			var item={};
			item["name"]=user.name;
			item["email"]=user.email;
			item["source"]='google';
			jsonObj.push(item);
			if (typeof user.name != 'undefined') {
				$("#socialMediaIntegrationData").val(JSON.stringify(jsonObj));
				$("#saveDataInDB").submit();
			}
		},
		dataType: "jsonp"
	});
}

/**
 *   regular expression checker to validate auth_token
 */
function gup(url, name) {
	name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
	var regexS = "[\\#&]"+name+"=([^&#]*)";
	var regex = new RegExp( regexS );
	var results = regex.exec( url );
	if( results == null )
		return "";
	else
		return results[1];
}

/**
 *   login using facebook
 */
function fbLogin() {
	var appID = "453239931458692";
	var path = 'http://www.facebook.com/dialog/oauth?';
	var REDIRECT1    =   'http://localhost:8080/explore/'
		var queryParams = ['client_id=' + appID,
		                   'redirect_uri=' + window.location,
		                   'response_type=token'];
	var query = queryParams.join('&');
	var url = path + query;

	var win = window.open(url, "windowname1", 'width=800, height=600');
	var pollTimer   =   window.setInterval(function() { 
		try {
			if (win.document.URL.indexOf(REDIRECT1) != -1) {
				window.clearInterval(pollTimer);
				var hash = win.location.hash.substring(1);
				if(hash.split('=')[0] == 'access_token')
				{
					var path = "https://graph.facebook.com/me?";
					var queryParams = [hash, 'callback=displayUser'];
					var query = queryParams.join('&');
					var url = path + query;

					// use jsonp to call the graph
					var script = document.createElement('script');
					script.src = url;
					document.body.appendChild(script);
					win.close();
				}
			}
		}
		catch(e) {
		}
	}, 300);
}
/**
 *   retrieve user information from facebook api
 */
function displayUser(user) {
	setTimeout(function () { }, 1000);
	if (user.id != null && user.id != "undefined") {
		var jsonObj = [];
		var item={};
		item["name"]=user.name;
		item["email"]=user.link;
		item["source"]='facebook';
		jsonObj.push(item);
		if (typeof user.name != 'undefined') {
			$("#socialMediaIntegrationData").val(JSON.stringify(jsonObj));
			$("#saveDataInDB").submit();
		}
	}
	else {
		alert('user error');
	}
}