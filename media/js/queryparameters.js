

// Variables from query string
var queryParameters = {}, queryString = location.search.substring(1),
    re = /([^&=]+)=([^&]*)/g, m, queryActivated = true;

// Creates a map with the query string parameters
while (m = re.exec(queryString)) {
    queryParameters[decodeURIComponent(m[1])] = decodeURIComponent(m[2]);
}



function updateURLQueryParameters() {
  history.replaceState({}, "Title", window.location.origin+window.location.pathname+"?"+$.param(queryParameters));
}

  // Add new parameters or update existing ones
  queryParameters['prod_class'] = prod_class;
  //queryParameters['details_treemap'] = queryParameters['details_treemap'] || 2;
  //queryParameters['cat_id'] = queryParameters['cat_id'] || "";
  //queryParameters['cont_id'] = queryParameters['cont_id'] || "";
  //queryParameters['show_related'] = Boolean(queryParameters['show_related']) || false;
  //queryParameters['trade_flow'] = queryParameters['trade_flow'] || "net";
  //queryParameters['highlight'] = queryParameters['highlight'] || "";