
// Variables from query string
var queryParameters = {}, queryString = location.search.substring(1),
    re = /([^&=]+)=([^&]*)/g, m, queryActivated = true; // Making it true as lang has to picked up from here instead of coockie 

// Creates a map with the query string parameters
while (m = re.exec(queryString)) {
  queryParameters[decodeURIComponent(m[1])] = decodeURIComponent(m[2]);
}

if(typeof(queryParameters["queryActivated"]) != "undefined")
  queryActivated = true;

function checkParameterExists(parameter) {
   //Get Query String from url
   fullQString = window.location.search.substring(1);
   
   paramCount = 0;
   queryStringComplete = "?";

   if(fullQString.length > 0)
   {
       //Split Query String into separate parameters
       paramArray = fullQString.split("&");
       
       //Loop through params, check if parameter exists.  
       for (i=0;i<paramArray.length;i++)
       {
         currentParameter = paramArray[i].split("=");
         if(currentParameter[0] == parameter) //Parameter already exists in current url
         {
            return true;
         }
       }
   }
   
   return false;
}

function updateURLQueryParameters() {

  queryParameters['lang'] = lang;
  // Remove empty query parameters
  for(var k in queryParameters){
    if(queryParameters.hasOwnProperty(k) && !queryParameters[k] && queryParameters[k] != 0){
      delete queryParameters[k];
    }
  }
  if(queryActivated)
  
    history.replaceState({}, "Title", window.location.origin+window.location.pathname+"?"+$.param(queryParameters));
}

// Add new parameters or update existing ones
if(typeof(prod_class) != "undefined")
  queryParameters['prod_class'] = prod_class;

queryParameters['details_treemap'] = parseInt(queryParameters['details_treemap']) || 2;
queryParameters['disable_widgets'] = typeof queryParameters['disable_widgets'] !== 'undefined' ? queryParameters['disable_widgets']=="true" : false;
queryParameters['disable_search'] = typeof queryParameters['disable_search'] !== 'undefined' ? queryParameters['disable_search']=="true" : false;
queryParameters['node_size'] = queryParameters['node_size'] || "none";

queryParameters["queryActivated"] = queryActivated || false;

if(typeof(app_name) != "undefined") {
  if(app_name == "stacked") {
    queryParameters['yaxis'] = queryParameters['yaxis'] || "current";
    queryParameters['yaxis'] = ["current", "notpc_constant", "pc_constant", "pc_current"].indexOf(queryParameters['yaxis']) < 0 ? "current" : queryParameters['yaxis'];
  } else if(app_name == "pie_scatter") {
    queryParameters['yaxis'] = queryParameters['yaxis'] || "complexity";
    queryParameters['yaxis'] = ["complexity", "opp_gain"].indexOf(queryParameters['yaxis']) < 0 ? "complexity" : queryParameters['yaxis'];
  }
}

//queryParameters['cat_id'] = queryParameters['cat_id'] || "";
//queryParameters['cont_id'] = queryParameters['cont_id'] || "";
//queryParameters['show_related'] = Boolean(queryParameters['show_related']) || false;
//queryParameters['trade_flow'] = queryParameters['trade_flow'] || "net";
//queryParameters['highlight'] = queryParameters['highlight'] || "";
