 function highlight(value) {

  if(typeof(value) != "undefined")
    highlight();

  var v = value ? value : $("#highlight_select").select2("val").trim();

  if(app_name == "product_space" || app_name == "rings" || app_type == "cspy") {

    d3.select("#viz").call(chart.highlight([]));
    d3.select("#viz").call(chart.highlight(v));

    queryParameters['highlight'] = v;
    if(queryActivated)
      updateURLQueryParameters();

  }

  if(app_name == "pie_scatter" || app_name == "tree_map" || app_name == "stacked") {

    if(app_type == "casy") {

    if(v.length>0)
      d3.select("#viz").call(viz.solo([v]));
    else
      d3.select("#viz").call(viz.solo([]));

    } else if(app_type == "csay" || app_type == "ccsy" || app_type == "cspy" || app_type == "sapy") {

    d3.select("#viz").call(viz.solo(flat_data.filter(function(dd) {
      if(dd.abbrv.toLowerCase() == v)// && dd.year==year)
        return dd;
    }).map(function(ddd) {
        return ddd.id
    })));

    }

    queryParameters['highlight'] = v;

    if(queryActivated)
      updateURLQueryParameters();

  }

}

function reset_highlight() {

  $("#highlight_select").select2("val", "");

  if(queryActivated) {
    queryParameters["highlight"] = "";
    updateURLQueryParameters();
  }

}