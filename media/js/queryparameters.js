
// Variables from query string
var queryParameters = {}, queryString = location.search.substring(1),
    re = /([^&=]+)=([^&]*)/g, m, queryActivated = false;

// Creates a map with the query string parameters
while (m = re.exec(queryString)) {
  queryParameters[decodeURIComponent(m[1])] = decodeURIComponent(m[2]);
}

if(typeof(queryParameters["queryActivated"]) != "undefined")
  queryActivated = true;

function updateURLQueryParameters() {

  // Remove empty query parameters
  for(var k in queryParameters){
    if(queryParameters.hasOwnProperty(k) && !queryParameters[k] && queryParameters[k] != 0){
      delete queryParameters[k];
    }
  }

  history.replaceState({}, "Title", window.location.origin+window.location.pathname+"?"+$.param(queryParameters));
}

// Add new parameters or update existing ones
queryParameters['prod_class'] = prod_class;
queryParameters['details_treemap'] = parseInt(queryParameters['details_treemap']) || 2;
queryParameters['disable_widgets'] = typeof queryParameters['disable_widgets'] !== 'undefined' ? queryParameters['disable_widgets']=="true" : false;
queryParameters['disable_search'] = typeof queryParameters['disable_search'] !== 'undefined' ? queryParameters['disable_search']=="true" : false;
//queryParameters['cat_id'] = queryParameters['cat_id'] || "";
//queryParameters['cont_id'] = queryParameters['cont_id'] || "";
//queryParameters['show_related'] = Boolean(queryParameters['show_related']) || false;
//queryParameters['trade_flow'] = queryParameters['trade_flow'] || "net";
//queryParameters['highlight'] = queryParameters['highlight'] || "";