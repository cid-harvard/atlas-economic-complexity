function build_app(api_uri, type_of_app, dimensions, embed){

  // show loading icon and clear current HTML container
  d3.select("#viz").html("")
  d3.select("#loader").style("display", "block");


  // get data from server
  d3.json(api_uri, function(data){
    // build the app with data from server
    build(data, dimensions)
    // hide loading icon
    d3.select("#loader").style("display", "none");

  })

  // Given raw data from the server clean it and build an app
  function build(data, dimensions){

    // clean up attribute data
    data.attr_data = clean_attr_data(data.attr_data)
    var showing = data.item_type;

    // initialize the app (build it for the first time)
    app = App()
      .width(dimensions[0])
      .height(dimensions[1])
      .year(data.year)

    // call app function (depending on which is loaded with the page)
    // on the given selection(s)
    d3.select("#viz")
      .style("height", dimensions[1]+"px")
      .datum(data)
      .call(app);

    if(!embed){
      key = Key()
        .classification(data.other.product_classification)
        .showing(showing)

      timeline = Timeline()
        .app_type(type_of_app)
        .year(year)

      controls = Controls()
        .app_type(type_of_app)
        .year(year)

      d3.select(".key")
        .datum(data.attr_data)
        .call(key);

      d3.select("#timeline")
        .datum(data.data)
        .call(timeline);

      d3.select("#tool_pane")
        .datum(data)
        .call(controls);
    }
  }

}

function clean_attr_data(attrs){
  // replace certain keys with common names used generically throughout apps
  attrs.forEach(function(attr){
    var id_property = attr["community_id"] ? "community_id" : "region_id",
      name_property = attr["community__name"] ? "community__name" : "region__name",
      color_property = attr["community__color"] ? "community__color" : "region__color",
      text_color_property = attr["community__text_color"] ? "community__text_color" : "region__text_color";
      continent_property = attr["continent"] ? "continent" : "";
    attr["category_id"] = attr[id_property]; delete attr[id_property];
    attr["category_name"] = attr[name_property]; delete attr[name_property];
    attr["category_color"] = attr[color_property]; delete attr[color_property];
    attr["category_text_color"] = attr[text_color_property]; delete attr[text_color_property];
    attr["heirarchical_id"] = attr["category_id"].toString().substr(0,1) + "." + attr["category_id"] + "." + attr["id"];
    attr["category_continent"] = attr[continent_property]; delete attr[continent_property];
  })

  // turn flat attributes array into indexed object with ids
  // either country or products as the key
  attrs = d3.nest()
    .key(function(d) { return d["id"]; })
    .rollup(function(d){ return d[0] })
    .map(attrs);

  // return this cleaned up version
  return attrs
}

function find_parent(e, name){
  if(e.nodeName == name){
    return e;
  }
  return find_parent(e.parentNode, name);
}

function format_big_num(d){
  d = parseFloat(d);
  var n = d;
  var s = "";
  var sign = "";
  if(d < 0){
    sign = "-"
  }
  d = Math.abs(d);
  if(d >= 1e3){
    n = d3.format(".2r")(d/1e3);
    s = "k";
  }
  if(d >= 1e6){
    n = d3.format(".2r")(d/1e6);
    s = "M";
  }
  if(d >= 1e9){
    n = d3.format(".2r")(d/1e9);
    s = "B";
  }
  if(d >= 1e12){
    n = d3.format(".2r")(d/1e12);
    s = "T";
  }
  if(d == 0){
    n = 0;
  }
  return [sign+n, s];
}

function make_mouseover(options){
  if(!options){
    $("#mouseover").remove();
    return;
  }
  if($("#mouseover").length){
    $("#mouseover").remove();
  }

  var cont = $("<div id='mouseover'>").appendTo("#viz");

  var cat = $("<div id='mouseover_cat'>").appendTo("#mouseover");
  cat.css("background", options.category_color)
  cat.css("color", options.category_text_color)
  cat.text(options.category)

  var title = $("<div id='mouseover_title'>").appendTo("#mouseover");
  title.text(options.title)

  if(options.values){
    var table = $("<table id='mouseover_table'>").appendTo("#mouseover");
    options.values.forEach(function(v){
      var tr = $("<tr>").appendTo(table);
      tr.append("<td>"+v[0]+"</td>")
      tr.append("<td>"+v[1]+"</td>")
    })
  }

  var left = d3.mouse(d3.select("#viz").node())[0];
  left = (left + $("#mouseover").width()/2) > options.width ? options.width - $("#mouseover").width()/2 : left;
  left = (left - $("#mouseover").width()/2) < 0 ? $("#mouseover").width()/2 : left;

  var top = d3.mouse(d3.select("#viz").node())[1] - $("#mouseover").height() - 40;
  top = top < 0 ? d3.mouse(d3.select("#viz").node())[1] + 40 : top;

  cont.css({
    "left": left - ($("#mouseover").width()/2),
    "top":  top
  })
}

function get_root(d){
  if(!d.parent){
    return d
  }
  return get_root(d.parent)
}


function update_viz(viz) {

  // Make sure we don't keep some parameter
  queryParameters['highlight'] = "";
  var queryString = "";
  if(queryActivated)
    queryString = "?"+$.param(queryParameters);

  // Fix for Firefox
  var url = $('base')[0].href + "explore/";

  var current_viz = (typeof viz != "undefined" )  ? viz : app_name;
  var current_year1 = parseInt($("#year1_select").val());

  // Import or Export
  var current_flow = $(".flow-direction").find(".active").index() == 0 ? "export": "import";
  current_flow = $(".flow-net-gross").find(".active").index() == 0 || $(".flow-net-gross").find(".active").index() == -1 ? current_flow: "net_"+current_flow;

  if(current_viz=="product_space" || current_viz=="pie_scatter" || current_viz=="rings")
    current_flow = "export";

  var current_country1 = $("#country1").find(":selected").val();
  current_country1 = (typeof current_country1 == "undefined" || current_country1 == "") ? "all" : current_country1;

  var current_country2 = $("#country-trade-partner").find(":selected").val();
  current_country2 = (typeof current_country2 == "undefined" || current_country2 == "") ? "all" : current_country2;

  var current_product = $("#country_product_select").find(":selected").val();
  current_product = (typeof current_product == "undefined" || current_product == "") ? "all" : current_product;

  var current_year2 = $("#year2_select").find(":selected").val();
  current_year2 = (typeof current_year2 == "undefined" || current_year2 == "") ? "" : parseInt(current_year2);

  // From trade partner to map
  if(typeof(viz)=="undefined" && current_country2!="all")
    current_viz = "tree_map";

  if(current_year2=="" && current_viz == "stacked")
    current_viz = "tree_map";

  if(viz=="tree_map" || viz=="map" || viz=="scatterplot" || viz=="rankings" || viz=="pie_scatter" || viz=="product_space"|| viz=="rings") {

    current_year1 = Math.max(current_year2, current_year1);
    current_year2 = "";
    current_viz = viz;
  }

  if(viz=="stacked" && current_year2=="") {

    if(prod_class=="hs4") {

      current_year1 = 1995;
      current_year2 = 2015;

    } else { // "sitc"

      current_year1 = 1962;
      current_year2 = 2015;

    }
    current_viz = viz;
  }

  // Making sure we stay in the boundaries
  if(viz=="stacked") {

    if(prod_class=="hs4") {

      current_year1 = 1995;
      current_year2 = 2015;

    } else { // "sitc"


      current_year1 = 1962;
      current_year2 = 2015;
    }
  }


  // Where does United States export Crude Petroleum to?
  // http://atlas.cid.harvard.edu/beta/explore/tree_map/export/usa/show/2709/2011/
  if($(".tab-trade-partner-product").find(".active").index()==0) {

    // if a country is not selected..
    if(current_country1=="all") {

      if(current_year2=="") {

        url += current_viz+"/"+current_flow+"/show/"+current_country1+"/"+current_product+"/"+current_year1+"/";

      } else {

        url += current_viz+"/"+current_flow+"/show/"+current_country1+"/"+current_product+"/"+current_year1+"."+current_year2+".2/";
      }


    } else if(current_product=="all") {

      // What did United States export in 2011?
      // http://127.0.0.1:8000/explore/tree_map/export/usa/all/show/2011/
      if(current_year2=="") {

        if(current_viz == "tree_map" || current_viz == "scatterplot" || current_viz == "rankings" || current_viz == "pie_scatter" || current_viz == "product_space" || viz=="rings")
          url += current_viz+"/"+current_flow+"/"+current_country1+"/all/show/"+current_year1+"/";
        else if(current_viz == "map") // Can't be a map of products
          url += current_viz+"/"+current_flow+"/"+current_country1+"/show/all/"+current_year1+"/";
        else
          console.log("Should not be here")
        // http://atlas.cid.harvard.edu/explore/map/export/usa/show/all/2011/

      } else {


        // http://atlas.cid.harvard.edu/beta/explore/stacked/export/usa/show/all/1995.2011.2/
        url += current_viz+"/"+current_flow+"/"+current_country1+"/all/show/"+current_year1+"."+current_year2+".2/"

      }

    } else {

      if(current_year2=="") {

        url += current_viz+"/"+current_flow+"/"+current_country1+"/show/"+current_product+"/"+current_year1+"/"

      } else {


        // Where does United States export Crude Petroleum to?
        // http://atlas.cid.harvard.edu/beta/explore/stacked/export/usa/show/2709/1995.2011.2/
        url += current_viz+"/"+current_flow+"/"+current_country1+"/show/"+current_product+"/"+current_year1+"."+current_year2+".2/"

      }
    }

  // http://atlas.cid.harvard.edu/beta/explore/tree_map/export/usa/show/2709/2011/
  } else if($(".tab-trade-partner-product").find(".active").index()==1) {

    if(current_country1 == current_country2) {

      alert("A country cannot trade with itself. Please select another country.")
      return;
    }


    if(current_country2=="all") {

      if(current_year2=="") {

       if(current_viz == "pie_scatter" || current_viz == "product_space" || current_viz=="rings"){
          url += current_viz+"/"+current_flow+"/"+current_country1+"/all/show/"+current_year1+"/";
       } else {
          url += current_viz+"/"+current_flow+"/"+current_country1+"/show/"+current_country2+"/"+current_year1+"/";
      }

      } else {

        // http://127.0.0.1:8000/explore/stacked/export/alb/show/all/1995.2011.2/

        url += current_viz+"/"+current_flow+"/"+current_country1+"/show/all/"+current_year1+"."+current_year2+".2/"
      }

    } else {

      if(current_year2=="") {

        // What did Albania export to Italy in 1995?
        // http://127.0.0.1:8000/explore/tree_map/export/alb/ita/show/1995/
        if(current_viz == "tree_map" || current_viz == "scatterplot" || current_viz == "rankings")
          url += current_viz+"/"+current_flow+"/"+current_country1+"/"+current_country2+"/show/"+current_year1+"/";
        else if(current_viz == "map") // Can't be a map of products
          url += current_viz+"/"+current_flow+"/"+current_country1+"/show/all/"+current_year1+"/";
        else if(current_viz == "pie_scatter" || current_viz == "product_space" || current_viz=="rings")
            url += current_viz+"/"+current_flow+"/"+current_country1+"/all/show/"+current_year1+"/";
        else
          console.log("Should not be here")

      } else {

        // http://atlas.cid.harvard.edu/beta/explore/stacked/export/usa/chn/show/1995.2011.2/
        url += current_viz+"/"+current_flow+"/"+current_country1+"/"+current_country2+"/show/"+current_year1+"."+current_year2+".2/"
      }
    }

  } else {

    console.log("error");
  }

  if(current_country1=="all" && current_product=="all") {
    alert("Please, select at least one country or one product");
    return;

  } else  if(current_country1=="all" && current_country2=="all" && $(".tab-trade-partner-product").find(".active").index()==1) {

    alert("Please, select at least one country");
    return;

  }

   else if (current_country2!="all" && current_year2 != "") {

    window.location.assign(url+queryString);

  } else {

    window.location.assign(url+queryString);
  }

  window.location.assign(url+queryString);
}
