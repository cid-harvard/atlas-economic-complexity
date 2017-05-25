var flat_data,
      attr,
      complexity,
      viz,
      timeline,
      rawData,
      where = [];

  // Sort array by year helper
  function compareYears(a, b) {
    return a.year - b.year;
  }

  // Change the node size for network app
  function change_node_size(v) {

    change_size_node = v;

    d3.select("#viz").call(viz.solo([]));

    queryParameters['node_size'] = v;
    updateURLQueryParameters();

  }

  // Change the node color for network app
  function change_node_color(v) {

    if(v == "category")
      d3.selectAll(".node").attr("fill", function(d) { return find_color(d.id); }).style("stroke", "#333")
    else if(v == "pci") {
      var pci_extent = d3.extent(flat_data, function(d) { return d.complexity });

      var pci_color_scale = d3.scale.linear()
                              .domain(pci_extent)
                              .range(["red", "black"]);

      d3.selectAll(".node").attr("fill", function(d) { return pci_color_scale(d.complexity); }).style("stroke", "#333")
    }

  }

  function nest_drop_report(nest_level) {

    // Find Out app_type
    switch (app_name) {
      case "tree_map":
        // Use tree_nesting
        if (nest_level == "nesting_0") {
          if (item_type=="country"){
            set_depth("nesting_1");
          }
          else
          {
            set_depth("nesting_0");
          }

        }
        else if (nest_level == "nesting_1"){
          set_depth("nesting_1");
        }
        else {
          set_depth("nesting_2");
        }
        break;

      case "stacked":

        // Use stack_nesting
        // var x=timeline.positions()
//             start = x[0].handle[0][0].textContent
//             finish = x[1].handle[0][0].textContent
//         set_stack_year([start,finish]);
        if (nest_level == "nesting_0") {
          (app_type=="csay"||app_type=="cspy"||app_type=="sapy") ?
            set_depth("nesting_1") :
            set_depth("nesting_0");
        }
        else if (nest_level == "nesting_1"){
          set_depth("nesting_1");
        }
        else {
          set_depth("nesting_2");
        }
        break;

      case "pie_scatter":
      case "scatterplot":

        set_depth(nest_level)
        break;
    }

  }

  // Change the app nesting level
  set_depth = function(arg) {
    d3.select('#viz').call(viz.depth(arg))
  }

  check_category_presence = function(arg) {
    missing = []
    current = []
    arg.forEach(function(d){
      current.push(d.name)
    })

    if (prod_class=="sitc4"){
      $.each(sitcs,function(key,val){
          if(current.contains(val.name)){
            return true;
          }
          missing.push(val);
          return false;
        })
    }
    else
    {
      $.each(cats,function(key,val){
          if(current.contains(val.name)){
            return true;
          }
          missing.push(val);
          return false;
        })
    }
    return missing;
  }

  set_stack_layout = function(arg) {

    if (arg=="share") {
      // set_stack_nesting(nest0_val);
      d3.select("#viz").call(viz.layout("share"));
      // d3.select("#viz").call(viz.value_var("my_share"));
    }
    else if(arg=="value")
    {
      // Just double check if this app has adjustment values
      d3.select("#viz").call(viz.layout("value"));

      if(app_type=="casy") {
        var adjust = d3.select('input[name=capita]:checked').attr("id")
        switch(adjust) {

         case "current":
            d3.select("#viz").call(viz.value_var("value"));
            break;
         case "pc_current": //Per Capita Current (USD)
            d3.select("#viz").call(viz.value_var("pc_current"));
            break;
         case "pc_constant": //Per Capita Constant (USD)
            d3.select("#viz").call(viz.value_var("pc_constant"));
            break;
         case "notpc_constant": //Per Capita Constant (USD)
            d3.select("#viz").call(viz.value_var("pc_constant"));
            break;
        }

        queryParameters['yaxis'] = adjust;


      } else {
        d3.select("#viz").call(viz.value_var("value"));
        queryParameters['yaxis'] = "current";
      }
    } else if(arg=="current") {
      d3.select("#viz").call(viz.value_var("value"));
      queryParameters['yaxis'] = "current";
    } else if(arg=="pc_current") {
      d3.select("#viz").call(viz.value_var("pc_current"));
      queryParameters['yaxis'] = "pc_current";
    } else if(arg=="pc_constant") {
      d3.select("#viz").call(viz.value_var("pc_constant"));
      queryParameters['yaxis'] = "pc_constant";
    } else if(arg=="notpc_constant") {
      d3.select("#viz").call(viz.value_var("notpc_constant"));
      queryParameters['yaxis'] = "notpc_constant";
    }

    updateURLQueryParameters();
  }

  set_stack_year = function(arg) {

    var stacked_title = d3.select('#atlas-search-js').text();
    stacked_title = stacked_title.replace(viz.year()[0], arg[0]);
    stacked_title = stacked_title.replace(viz.year()[1], arg[1]);
    d3.select('#atlas-search-js').text(stacked_title);

    var href = window.location.href;
    href = href.replace(viz.year()[0], arg[0]);
    href = href.replace(viz.year()[1], arg[1]);

    // TODO: Check if IE compliant
    update_url('The Atlas', d3.select('#atlas-search-js').text(), href);

    d3.select("#viz").call(viz.year([arg[0],arg[1]]))

    $(".dropdown_container#year_start select").val(arg[0]);
    $(".dropdown_container#year_end select").val(arg[1]);

    $(".dropdown_container#year_start select").trigger("liszt:updated");
    $(".dropdown_container#year_end select").trigger("liszt:updated");

    year_title = arg[0] + " " + arg[1]
    // var year_title = ''+year;
//     if(year_title.indexOf(".") > -1){
//       year_title = year_title.replace(".", " ")
//       year_title = year_title.substr(0, year_title.indexOf("."))
//     }
    $(".app_title#icons h2").text(year_title)

    // Update the year drowdown
    $("#year1_select > options").attr("selected", false);
    $("#year1_select > [value='"+arg[0]+"']").attr("selected", true);
    $("#year2_select > options").attr("selected", false);
    $("#year2_select > [value='"+arg[1]+"']").attr("selected", true);
    $('select').trigger("chosen:updated");

  }

  set_scatter_year = function(arg) {

    var nest_level = ($("#nesting_level").val());
    year=arg

    // Why are we doing that?
    //set_depth(nest_level)

    var scatter_title = d3.select('#atlas-search-js').text();

    scatter_title = scatter_title.replace(viz.year(), arg);
    d3.select('#atlas-search-js').text(scatter_title);

    // Update the URL
    update_url('The Atlas', d3.select('#atlas-search-js').text(),  window.location.href.replace(viz.year(), arg));

    d3.select("#viz").call(viz.year(arg));

  }

  set_scatterplot_year = function(arg) {

    year_data = flat_data.filter(function(d){ return d.year == arg})
    // d3.select("#viz").call(viz.time("year", 2012))

  }

  function updateRCA(v) {
    d3.select("#rca-threshold").text(v);
        data.forEach(function(d){
          d.active = d.rca >= v ? 1 : 0
          return d;
        })

    d3.select("#viz").call(chart.highlight(""))
  }

  display_growth = function(arg) {

    // Check if a treemap of map

    // Local variables
    var curr_year = parseInt(viz.year());
    var prev_year = curr_year - arg;
    var curr_year_prods = flat_data.filter(function(d) { return d.year==curr_year; });
    var prev_year_prods = flat_data.filter(function(d) { return d.year==prev_year; });

    curr_year_prods.forEach(function(d) {

      prev_year_prods.forEach(function(e) {

        if(e.id == d.id) {
          d.diff = d.value - e.value;
          return ;
        }

      })

    })

    var min_diff = d3.min(curr_year_prods, function(d) { return d.diff });
    var max_diff = d3.max(curr_year_prods, function(d) { return d.diff });

    var diff_color_scale = d3.scale.linear().domain([min_diff, 0, max_diff]).range(["red", "black", "green"]);

    // Adding new diff attribute for all the years
    flat_data.forEach(function(d) {
      d.diff_color = "#000000";
    })

/*
    curr_year_prods.forEach(function(d) {
      d.diff_color = diff_color_scale(d.diff)
    })
*/
    // Updating the treemap
    d3.select('#viz').call(viz.color_var('diff_color'))

  }

  set_year = function(arg) {

    if((typeof(single_year) != "undefined") && single_year) {

      single_year = false;
      d3.select("#loader").style("display", "block");
      d3.select("#loader").append("text").text("Loading more years...")
      d3.select("#viz").transition().style("opacity", 0)

      // Make the AJAX call to retrieve other years
      d3.json(api_uri + '&amp;data_type=json', function(raw) {
        rawData = raw;
        item_type = raw["item_type"];
        flat_data=raw["data"];
        attr=raw["attr"];
        attr_data = raw["attr_data"];
        app_type= raw["app_type"];
        //prod_class = raw["prod_class"];
        region_attrs = {};

        flat_data = construct_nest(flat_data);

        if(app_name=="tree_map") {

          d3.select("#viz")
             .style('height','520px')
             .datum(flat_data)
             .call(viz);

        } else if(app_name=="product_space") {

          network();

        }

        d3.select("#loader").style("display", "none");
        d3.select("#viz").transition().style("opacity", 1)
        set_year(arg);
      });
      return;
    }

    if(typeof(start_year) == "undefined")
      start_year = viz.year();

    var treemap_title = d3.select('#atlas-search-js').attr("value");
    treemap_title = treemap_title.replace(viz.year(), arg);
    d3.select('#atlas-search-js').attr("value", treemap_title);

    // Update the URL
    update_url('The Atlas', d3.select('#atlas-search-js').text(),  window.location.href.replace(viz.year(), arg));

    // Update the year drowdown
    $("#year1_select > options").attr("selected", false);
    $("#year1_select > [value='"+arg+"']").attr("selected", true);
    $('select').trigger("chosen:updated");

    viz.year(arg);
    d3.select('#viz').call(viz)
    year = viz.year();

  // Set the controls to this year as well
    d3.select("#tool_pane").call(controls.year(arg));
    $(".app_title#icons h2").text(arg)
  }

  set_map_year = function(arg) {

    var map_title = d3.select('#atlas-search-js').text();
    map_title = map_title.replace(app.year(), arg);
    d3.select('#atlas-search-js').text(map_title);

    // TODO: Check if IE compliant
    update_url('The Atlas', d3.select('#atlas-search-js').text(),  window.location.href.replace(app.year(), arg));

    d3.select("#viz").call(app.year(parseInt(arg)));
    // Set the controls to this year as well
    d3.select("#tool_pane").call(controls.year(arg));

    // Update the year drowdown
    $("#year1_select > options").attr("selected", false);
    $("#year1_select > [value='"+arg+"']").attr("selected", true);
    $('select').trigger("chosen:updated");

  }

  construct_nest = function(flat) {

    // Ask for visualizations that need to be sorted by export/import/net values
    if (app_type == "casy" || app_type == "sapy" || app_type == "ccsy") {

      if (app_type == "casy" || app_type=="ccsy") {
        flat = flat.filter(function(d){ return d.community_id != undefined; })
        flat.map(function(d,i){

          if (prod_class == "hs4")
          {
            d.nesting_0 = {"name" :d.community_name, "id":d.community_id};
            d.nesting_1 = {"name":attr[d.code.slice(0, 2)].name,"id":d.code.slice(0, 2)};
          }
          else // sitc4 codes end in 00's
          {
            d.color = attr[d.code.slice(0, 1)+"000"].color
            d.nesting_0 = {"name" :attr[d.code.slice(0, 1)+"000"].name, "id":d.code.slice(0, 1)+"000"};
            // d.nesting_0 = {"name" :d.community_name, "id":d.community_id};
            d.nesting_1 = {"name":attr[d.code.slice(0, 2)+"00"].name,
                           "id":d.code.slice(0, 2)+"00"};
            // d.nesting_1 = {"name":attr[d.code.slice(0, 2)+"00"].name,
                           // "id":d.community_id.toString()+d.code.slice(0, 2)};
          }
          d.nesting_2 = {"name":d.name,"id":d.code};
         })

      } else { // Needs different tailored nesting

        region = rawData["region"];
        continent = rawData["continents"];

        // What to do with countries that do not have regions predefined?
        // Filtering them for now I guess.. "final solution" ???
        flat = flat.filter(function(d){ return d.region_id != undefined; })

        flat.map(function(d,i){

          d.color = region[d.region_id].color;

          plate =  String(continent[d.continent])
          part = String(continent[d.continent]) + String(d.region_id)
          piece = String(continent[d.continent]) + String(d.region_id)+ String(d.id)

          region_attrs[plate] = {"color":d.color,"name":d.continent}
          region_attrs[part] = {"color":d.color,"name":region[d.region_id].name}
          region_attrs[piece] = {"color":d.color,"name":d.name}
          // region_attrs[continent[d.continent]] = {"color":d.color,"name":d.continent}
          // region_attrs[d.region_id] = {"color":d.color,"name":region[d.region_id].name}

          d.nesting_0 = {"name" :d.continent, "id":plate};
          d.nesting_1 = {"name":region[d.region_id].name, "id":part};
          d.nesting_2 = {"name":d.name,"id":piece};

          d.id = piece
        })
      }

    }
    else  // The remaining queries CSAY and CSPY were preprocessed per the query group_by statement
    {

      region = rawData["region"];
      continent = rawData["continents"];

      // What to do with countries that do not have regions predefined?
      // Filtering them for now I guess.. "final solution" ???
      flat = flat.filter(function(d){ return d.region_id != undefined; })

      flat.map(function(d,i){

        d.color = region[d.region_id].color;

        plate =  String(continent[d.continent])
        part = String(continent[d.continent]) + String(d.region_id)
        piece = String(continent[d.continent]) + String(d.region_id)+ String(d.id)

        region_attrs[plate] = {"color":d.color,"name":d.continent}
        region_attrs[part] = {"color":d.color,"name":region[d.region_id].name}
        region_attrs[piece] = {"color":d.color,"name":d.name}
        // region_attrs[continent[d.continent]] = {"color":d.color,"name":d.continent}
        // region_attrs[d.region_id] = {"color":d.color,"name":region[d.region_id].name}

        d.nesting_0 = {"name" :d.continent, "id":plate};
        d.nesting_1 = {"name":region[d.region_id].name, "id":part};
        d.nesting_2 = {"name":d.name,"id":piece};

        d.id = piece
      })
      // region = rawData["region"];
      // continent = rawData["continents"];
      // // What to do with countries that do not have regions predefined?
      // // Filtering them for now
      // flat = flat.filter(function(d){ return d.region_id != undefined; })
      //
      // flat.map(function(d,i)
      //   {
      //     d.color = region[d.region_id].color;
      //     region_attrs[continent[d.continent]] = {"color":d.color,"name":d.continent}
      //     region_attrs[d.region_id*10000] = {"color":d.color,"name":region[d.region_id].name}
      //
      //     region_attrs[d.id] = {"color":d.color,"name":d.name}
      //
      //     d.nesting_0 = {"name" :d.continent, "id":String(continent[d.continent])};
      //     d.nesting_1 = {"name":region[d.region_id].name,"id":String(d.region_id*10000)};
      //     d.nesting_2 = {"name":d.name,"id":String(d.id)};
      //   })
    }
    // rather than saving these changes in the global lets return it
    return flat;

  }

  construct_scatter_nest = function(flat) {

    var flat = flat.filter(function(d){ return d.community_id != undefined; })

    flat.map(function(d){
      d.active = d.rca >=1 ? true : false

      if (prod_class == "hs4")
      {
        d.nesting_0 = {"name" :d.community_name, "id":d.community_id};
        d.nesting_1 = {"name":attr[d.code.slice(0, 2)].name,"id":d.code.slice(0, 2)};
      }
      else // sitc4 codes end in 00's
      {
        d.color = attr[d.code.slice(0, 1)+"000"].color
        d.nesting_0 = {"name" :attr[d.code.slice(0, 1)+"000"].name, "id":d.code.slice(0, 1)+"000"};
        // d.nesting_0 = {"name" :d.community_name, "id":d.community_id};
        d.nesting_1 = {"name":attr[d.code.slice(0, 2)+"00"].name,
                       "id":d.code.slice(0, 2)+"00"};
        // d.nesting_1 = {"name":attr[d.code.slice(0, 2)+"00"].name,
                       // "id":d.community_id.toString()+d.code.slice(0, 2)};
      }
      d.nesting_2 = {"name":d.name,"id":d.code};
      d.complexity =  d.pci
    })
    return flat
  }

  num_format = function(value, name) {

    switch(name) {
      case 'pc_constant':
        return "$"+ d3.round(value)
        break;
      case 'pc_current':
        return "$"+ d3.round(value)
        break;
      case 'Per Capita Constant':
        return "$"+ d3.round(value)
        break;
      case 'Per Capita Current':
        return "$"+d3.round(value)
        break;
      default:
    }
    // console.log(value)
    // DO I NEED THIS ANYMORE!??
    var smalls = ["rca","rca_bra","rca_wld","distance","complexity","RCA","Distance","Complexity"]

    if (smalls.indexOf(name) >= 0) {
      return d3.round(value,2)
    }
    // if the number is larger than 1000
    else if (value.toString().split(".")[0].length > 4) {
      var symbol = d3.formatPrefix(value).symbol
      symbol = symbol.replace("G", "B") // d3 uses G for giga

      // Format number to precision level using proper scale
      value = d3.formatPrefix(value).scale(value)
      value = parseFloat(d3.format(".3g")(value))
      return "$"+value + symbol;
    }
    else if (name=="Year"){
      return value;
    }
    // else if (name="")
    // With no name value, this should only be the share value
    else if (value<1.0)
    {
      if (value<0.1){

        return d3.round(value,4)
      }
      return d3.round(value,2)
    }
    else
    {
      // return d3.round(value,2nd);
      return d3.format("f")(value)
    }

  }

  txt_format = function(words) {

    switch(words) {
     case 'pc_constant':
       return gettext("Per Capita Constant")
       break;
     case 'year':
       return gettext("Year")
       break;
     case 'pc_current':
       return gettext("Per Capita Current")
       break;
     case 'notpc_constant':
       return gettext("Constant")
       break;
     case 'value':
       return gettext("Current")
       break;
     case 'distance':
       return gettext("Distance")
       break;
     case 'share':
       return gettext("Share")
       break;
     case 'complexity':
       return gettext("Complexity")
       break;
     case 'rca':
       return 'RCA'
       break;
     case 'id':
       return "Code"
       break;
     case 'world_trade':
       return gettext("World Trade")
       break;
     case 'active':
       return gettext("Active")
       break;
     case 'opp_gain':
       return gettext("Opportunity Gain")
       break;
     default:
       return words
    }
  }

  // Create tooltip content
  var inner_html = function(obj) {

    var html = "<div class='d3plus_tooltip_title'>Related Visualizations </div><br>";
    html += "<div id='related_links'></div>";

    var name = "", object = null;

    if(viz.depth() == "nesting_2") {

      // Retrieve the name from id
      flat_data.forEach(function(d) {
        if(d.id == obj) {
          name = d.name;
          object = d;
          return;
        }
      })

    } else if(viz.depth() == "nesting_1") {

      // Retrieve the name from id
      flat_data.forEach(function(d) {
        if(d.nesting_1.id == obj) {
          name = d.nesting_1.name;
          object = d;
          return;
        }
      })

    } else if(viz.depth() == "nesting_0") {

      // Retrieve the name from id
      flat_data.forEach(function(d) {
        if(d.nesting_0.id == obj) {
          name = d.nesting_0.name;
          object = d;
          return;
        }
      })

    }

    // Required to make sure the tooltip has been created
    setTimeout(function() {

      //  Sample of API result: /media/js/data/search_sample.json
        d3.json("/api/search/?term="+name, function(error, data) {

          if (error) { // Default data
            return console.warn(error);

          } else {
            json = data;
          }

          related_html = "";

          data[1].forEach(function(d, i) {

            d3.select("#related_links")
              .append("div").style("font-size", "14px").style("margin-top", "6px").html("<a href='"+(data[3][i]+"?"+$.param(queryParameters))+"'>"+d+"</a>");

          })

        })

    }, 100)

    return html;
  }

  tree = function() {

    viz = d3plus.viz();

    viz
      .type("tree_map")
      .height(height)
      .width(width)
      .id_var("id")
      .attrs(attr)
      .text_var("name")
      .value_var("value")
      .tooltip_info({"short": ["value", "year"], "long": ["value", "distance", "rca", "year"]})
      .name_array(["name"])
      .total_bar({"prefix": "", "suffix": " USD"})
      .nesting(["nesting_0","nesting_1","nesting_2"])
      .nesting_aggs({"distance":"mean","complexity":"mean"})
      .font("Helvetica Neue")
      .click_function(inner_html)
      .font_weight("lighter")
      .depth("nesting_"+queryParameters["details_treemap"]) // 2 by default
      .text_format(txt_format)
      .number_format(num_format)
      .font('PT Sans Narrow')
      .year(year)
     // .data_source("Data provided by: ",prod_class)

    if(item_type=="country") {

      viz.depth("nesting_2") // Updated to low level
         .attrs(region_attrs)

    } else {
      // Update Detail level to deepest
      $('#nesting_level').val("nesting_2")
      $('#nesting_level').trigger("liszt:updated");
    }

    // Call Visualization itself
    d3.select("#viz")
           .style('height','520px')
           .datum(flat_data)
           .call(viz);


    // If we embed we do not need key/controls
    if (!embed){

      key = Key()
        .classification(rawData.class)
        .showing(item_type)

      at = d3.values(attr_data)


      d3.select(".key")
        .datum(at)
        .call(key);

      controls = Controls()
        .app_type(app_name)
        .year(year)

      d3.select("#tool_pane")
        .datum(rawData)
        .call(controls);
    }

    d3.select("#loader").style("display", "none");
    if(queryActivated)
      highlight(queryParameters['highlight']);

    //d3.select("#viz").style("height", "0px");
    //d3.select("#viz svg").style("display", "none");
    //d3.select("#loader").style("display", "none");
  }

  stack = function() {

    var years = year.split('.')

    viz = d3plus.viz()
      .type("stacked")
      .height(height)
      .width(748)
      //.value_var("value")
      .sort("color")
      .xaxis_var("year")
      .attrs(attr)
      .tooltip_info({"short": ["value", "distance", "year"], "long": ["value", "distance", "year"]})
      .text_var("name")
      .id_var("id")
      .nesting(["nesting_0","nesting_1","nesting_2"])
      .nesting_aggs({"distance":"mean"})
      .depth("nesting_0")
      .text_format(txt_format)
      .font('PT Sans Narrow')
      .number_format(num_format)
      .stack_type("monotone")
      .click_function(inner_html);

    if(queryActivated && typeof(queryParameters['yaxis']) != "undefined") {

      switch (queryParameters['yaxis']) {
        case "pc_current":
          viz.value_var("pc_current");
          break;
        case "pc_constant":
          viz.value_var("pc_constant");
          break;
        case "notpc_constant":
          viz.value_var("notpc_constant");
          break;
        default:
         viz.value_var("value");
      }
    } else {
      viz.value_var("value");
    }

    d3.select("#loader").style("display", "none");

    //if(queryActivated)
    //  highlight(queryParameters['highlight']);

    flat_data.map(function(d){
      d.id = String(d.id)
    })

    // If not showing countries exporting a product
    if (app_type!="sapy") {

      magic_numbers = rawData["magic_numbers"]
      viz.tooltip_info({"short": ["distance", "year", "pc_current","pc_constant","notpc_constant"]})
      flat_data.map(function(d){

        // Quick fix by rv
        if(magic_numbers[d.year]) {
          d.pc_constant = magic_numbers[d.year]["pc_constant"] * d.value
          d.pc_current = magic_numbers[d.year]["pc_current"] * d.value
          d.notpc_constant = magic_numbers[d.year]["notpc_constant"] * d.value
        }
      })
    }

    //viz.tooltip
    if(item_type=="country") {
      viz
        .depth("nesting_1")
        .sort("color")
        .attrs(region_attrs)
    }

    // Since there is no title bar, we're gona bump the viz down
    d3.select("#viz").style("margin-top","15px")

    // See IAEC-312: thresholding seems to be in place to reduce number of DOM
    // elements to make render quicker. This affects totals in categories in
    // large countries. By tweaking this number, in effect, you're trading off
    // numerical accuracy for render speed, with diminishing returns after a
    // while.
    flat_data = flat_data.filter(function(d){ return d.share > 0.00075})

    // INCASE WE WANT TO COMBINE ALL THE FILTERED ELEMENTS INTO A SINGLE ELEMENT
    // flat_data = flat_data.filter(function(d){return d.value > 85000000})
    // flat_data.forEach(function(d){
    //   if(d.share < 0.00125){
    //     d.color = "lightgray"
    //     d.id = "666666"
    //     d.name = "Other"
    //     d.nesting_0 = {"id":"666666","name":"Other"}
    //     d.nesting_1 = {"id":"666666","name":"Other"}
    //     d.nesting_2 = {"id":"666666","name":"Other"}
    //   }
    // })

    // Call Visualization itself
    d3.select("#viz")
    .style('height','520px')
    .datum(flat_data)
    .call(viz)

    if (!embed){
    key = Key()
      .classification(rawData.class)
      .showing(item_type)

    d3.select(".key")
      .datum(attr_data)
      .call(key);

    controls = Controls()
      .app_type(app_name)
      .year(year)

    d3.select("#tool_pane")
      .datum(rawData)
      .call(controls);

    d3.select("#viz").call(viz.year([year_start,year_end]))

    $("#stacked_labels").buttonset();
    $("#stacked_order").buttonset();
    $("#stacked_layout").buttonset();
    $("#stacked_capita").buttonset();
    $("#stacked_controls input[type='radio']").change(function(e){

      if($(e.target).attr("name") == "labels") {
        ($(e.target).attr("id")=="false") ? d3.select("#viz").call(viz.labels(false)) :
                                            d3.select("#viz").call(viz.labels(true))
      }
      if($(e.target).attr("name") == "layout"){
        //d3.select("#dataviz").call(app.layout($(e.target).attr("id")));
        set_stack_layout($(e.target).attr("id"));
      }
      if($(e.target).attr("name") == "order"){
        ($(e.target).attr("id")=="community") ? d3.select("#viz").call(viz.sort("color")) :
                                                d3.select("#viz").call(viz.sort("total"))
        // d3.select("#viz").call(viz.sort($(e.target).attr("id")))
      }
      if($(e.target).attr("name") == "capita"){
        set_stack_layout($(e.target).attr("id"));
      }
    })
    // Now that we're done loading UI elements show the parent element
    $("#stacked_controls").show();

    d3.select(".axis_title_x").style("font-weight","bold");//.attr("y","40");
    d3.select(".axis_title_y").style("font-weight","bold");//.attr("y","10");

    } else {
      // in this instance we're not getting year start/stop dates from explore view;
      //we need to figure them out from api
      var years = year.split('.')
      year_s = years[0]
      year_e = years[1]
      d3.select("#viz").call(viz.years([years_s,years_e]))

    }

  }

  pie_scatter = function() {

    viz = d3plus.viz()

    viz
      .type("pie_scatter")
      .height(height)
      .width(width)
      .tooltip_info({"short": ["value", "distance", "complexity","rca"], "long": ["value", "distance", "complexity","rca"]})
      .text_var("name")
      .id_var("id")
      .attrs(attr)
      .xaxis_var("distance")
      .value_var("value")
      .total_bar({"prefix": "", "suffix": " USD", "format": ",f"})
      .nesting(["nesting_0","nesting_1","nesting_2"])
      .nesting_aggs({"complexity":"mean","distance":"mean","rca":"mean"})
      .depth("nesting_2")
      .text_format(txt_format)
      .number_format(num_format)
      .spotlight(false)
      .dev(false)
      .font('PT Sans Narrow')
      .click_function(inner_html)
  //    .static_axis(false)
      .year(year)

    if(queryActivated && typeof(queryParameters['yaxis']) != "undefined" && queryParameters['yaxis'] == "opp_gain") {
      viz.yaxis_var("opp_gain")
    } else {
      viz.yaxis_var("complexity")
    }

    d3.select("#loader").style("display", "none");

    flat_data.map(function(d) {
      if(typeof(world_totals[d.year].filter(function(z){ return d.item_id==z.product_id })[0]) != "undefined") {
        d.world_trade = world_totals[d.year].filter(function(z){ return d.item_id==z.product_id })[0]['world_trade']
      }
      d.id = String(d.id)
    })

    d3.select("#viz")
      .style('height','520px')
      .datum(flat_data)
      .call(viz)

    // highlight(queryParameters['highlight']);

    if(!embed){
      key = Key()
        .classification(rawData.class)
        .showing(item_type)

      d3.select(".key")
        .datum(attr_data)
        .call(key);

      controls = Controls()
        .app_type(app_name)
        .year(year)

      d3.select("#tool_pane")
        .datum(rawData)
        .call(controls);

      $("#pie_yvar").buttonset();
      $("#pie_spot").buttonset();
      $("#pie_controls input[type='radio']").change(function(e){
        if($(e.target).attr("name") == "yvar") {

          if($(e.target).attr("id")=="complexity") {
            d3.select("#viz").call(viz.yaxis_var("complexity"))
            queryParameters['yaxis'] = "complexity";
          } else {
            d3.select("#viz").call(viz.yaxis_var("opp_gain"))
            queryParameters['yaxis'] = "opp_gain";
          }

          updateURLQueryParameters();

        }
        if($(e.target).attr("name") == "pie_spot"){
          ($(e.target).attr("id")=="spot_off") ? d3.select("#viz").call(viz.spotlight(false)) :
                                              d3.select("#viz").call(viz.spotlight(true))
        }
      })
    }
  }

  scatterplot = function() {

    flat_data = construct_nest(flat_data);

    viz = d3plus.viz()

    if(item_type=="product") {

      if (prod_class == "sitc4"){
        flat_data = flat_data.filter(function(d){
          return d.distance != 0;
        });
      }
      flat_data = construct_scatter_nest(flat_data);

    viz
      .type("pie_scatter")
      .height(height)
      .width(width)
      .tooltip_info({"short": ["share", "value"], "long": ["share", "value"]})
      .text_var("name")
      .id_var("id")
      .attrs(attr)
      .xaxis_var("distance")
      .yaxis_var("value")
      .value_var("value")
      .total_bar({"prefix": "", "suffix": " USD", "format": ",f"})
      .nesting(["nesting_0","nesting_1","nesting_2"])
      .nesting_aggs({"share":"mean", "value":"mean"})
      .depth("nesting_2")
      .text_format(txt_format)
      .number_format(num_format)
      .spotlight(false)
      .dev(false)
      .font('PT Sans Narrow')
      .click_function(inner_html)
  //    .static_axis(false)
      .year(year)

    d3.select("#loader").style("display", "none");

    flat_data.map(function(d) {
      if(typeof(world_totals[d.year].filter(function(z){ return d.item_id==z.product_id })[0]) != "undefined") {
        d.world_trade = world_totals[d.year].filter(function(z){ return d.item_id==z.product_id })[0]['world_trade']
      }
      d.id = String(d.id)
    })

 } else {

    viz
      .type("pie_scatter")
      .height(height)
      .width(width)
      .tooltip_info({"short": ["value", "share", "rca"], "long": ["value", "share", "rca"]})
      .text_var("name")
      .id_var("id")
      .attrs(region_attrs)
      .xaxis_var("rca")
      .yaxis_var("value")
      .value_var("value")
      .total_bar({"prefix": "", "suffix": " USD", "format": ",f"})
      .nesting(["nesting_0","nesting_1","nesting_2"])
      .nesting_aggs({"value":"sum","share":"mean","rca":"mean"})
      .depth("nesting_2")
      .text_format(txt_format)
      .number_format(num_format)
      .spotlight(false)
      .dev(false)
      .font('PT Sans Narrow')
      .click_function(inner_html)
  //    .static_axis(false)
      .year(year)
 }

    d3.select("#viz")
      .style('height','520px')
      .datum(flat_data)
      .call(viz)

    // highlight(queryParameters['highlight']);

    d3.select("#loader").style("display", "none");

    if(!embed){
      key = Key()
        .classification(rawData.class)
        .showing(item_type)

      d3.select(".key")
        .datum(attr_data)
        .call(key);

      controls = Controls()
        .app_type(app_name)
        .year(year)

      d3.select("#tool_pane")
        .datum(rawData)
        .call(controls);

      $("#pie_yvar").buttonset();
      $("#pie_spot").buttonset();
      $("#pie_controls input[type='radio']").change(function(e){
        if($(e.target).attr("name") == "yvar"){
          ($(e.target).attr("id")=="complexity") ? d3.select("#viz").call(viz.yaxis_var("complexity")) :
                                              d3.select("#viz").call(viz.yaxis_var("opp_gain"))
        }
        if($(e.target).attr("name") == "pie_spot"){
          ($(e.target).attr("id")=="spot_off") ? d3.select("#viz").call(viz.spotlight(false)) :
                                              d3.select("#viz").call(viz.spotlight(true))
        }
      })
    }
  }

  rankings = function() {

    d3.select("#viz").style({"font-size": "14px", "overflow-y": "scroll", "overflow": "-moz-scrollbars-vertical"})

    d3.select("#loader").style("display", "none");

    viz = ranking.viz()
      .container("#viz")
      .id_var("id")
      .height(height)
      .width(width)
      .year(year)
      .data(flat_data)


    if(item_type=="product") {

      viz
        .columns(["id", "year", "name", "opp_gain", "pci", "rca",  "distance", "value"])
        .nesting(["nesting_0","nesting_1","nesting_2"])
        .nesting_aggs({"complexity":"mean","distance":"mean","rca":"mean"})
        .title("Products Ranking")
        .depth("nesting_2");

    } else {

      viz
        .columns(["id", "year", "name", "rca", "value"])
        .nesting(["nesting_0","nesting_1","nesting_2"])
        .nesting_aggs({"value":"mean", "rca":"mean"})
        .title("Countries Ranking")
        .depth("nesting_1");

    }


    d3.select("#viz").call(viz)

    if(!embed) {

      key = Key()
        .classification(rawData.class)
        .showing(item_type)

      d3.select(".key")
        .datum(attr_data)
        .call(key);

    }

  }

  rings = function( req ) {

    (prod_class=="hs4") ? req = "/media/js/data/network_hs.json" :
                          req = "/media/js/data/network_sitc.json";

    d3.json(req, function(hs) {

      viz = d3plus.viz()

      viz_nodes = hs.nodes
      viz_links = hs.edges


      viz_nodes.forEach(function(node){
       if (prod_class=="hs4"){
          node.item_id = attr[node.id.slice(2,6)]['item_id']
          node.id = node.id.slice(2,6);
        }
        else
        {
          node.item_id = node.id
          node.id = node.code
        }
      })
      if (prod_class=="hs4"){
        viz_links.forEach(function(link){
          link.source = viz_nodes[link.source]
          link.target = viz_nodes[link.target]
        })
      }
      else
      {
        viz_links.forEach(function(link){
          link.source =viz_nodes.filter(function(d){ return d.code == link.source })[0]
          link.target =viz_nodes.filter(function(d){ return d.code == link.target })[0]
        })
      }

      flat_data.map(function(d) {
        if(typeof(world_totals[d.year].filter(function(z){ return d.item_id==z.product_id })[0]) != "undefined") {
          d.world_trade = world_totals[d.year].filter(function(z){ return d.item_id==z.product_id })[0]['world_trade']
        }
      })

      data = []
      the_years = d3plus.utils.uniques(flat_data,"year")
      the_years.forEach(function(year){
        var this_year = flat_data.filter(function(p){ return p.year == year})

        viz_nodes.forEach(function(n){
          if (prod_class=="hs4")
          {
            // var d = flat_data.filter(function(p){ return p.year == year && p.code == n.id })[0]
           var d = this_year.filter(function(p){ return p.code == n.id })[0]
           if (typeof d == "undefined")
           {
            var d = {};
            // d.world_trade = world_totals[year].filter(function(z){ return n.item_id==z.product_id })[0]['world_trade']
           }

            d.world_trade = world_totals[year].filter(function(z){ return n.item_id==z.product_id })[0];

            // Added for 2012 data
            if(typeof(d.world_trade) != "undefined")
              d.world_trade = d.world_trade['world_trade'];

            // var obj = vizwhiz.utils.merge(d,attr[n.id])
            // obj.world_trade = d.world_trade
          }
          else
          {
            var d = this_year.filter(function(p){ return p.id == n.code })[0]
            if (typeof d == "undefined")
              {
                var d = {}
              }
            // Double check if this product existed then
            var test = world_totals[year].filter(function(z){ return n.item_id==z.product_id })[0]//['world_trade']
            if (typeof test != "undefined")
              {
                d.world_trade = test['world_trade']
              }
              else // if not then assign value as 0
              {
                d.world_trade = 0
              }

          }

          // obj.year = year;
          d.active = d.rca >=1 ? 1 : 0
          data.push(d)

        })

        this_year = []
      })

      var year_data = flat_data.filter(function(d, i) { if(d.year==parseInt(year)) return d;});
      var max_value = d3.max(year_data, function(d, i) { return d.value})
      var max_id = year_data.filter(function(d, i) { if(d.value==max_value) return d;} )[0].code

      var tooltips = {"": ["id","distance","complexity","year"],"other": ["val_usd","distance"]}

      viz
        .type("rings")
        .height(height)
        .width(width)
        .text_var("name")
        .id_var("id")
        .links(viz_links)
        .nodes(viz_nodes)
        .attrs(attr)
        .name_array(["value"])
        .value_var("world_trade")
        .highlight(max_id+"")
        .tooltip_info(["id","value","complexity","distance","rca","world_trade"])
        .nesting([])
        .total_bar({"prefix": "Export Value: $", "suffix": " USD", "format": ",f"})
        .click_function(inner_html)
        .descs({"id": "This is ID", "val_usd": "This is value USD."})
        .footer("")
        .year(year)
        // .text_format(function(d){return d+"longtext longtext longtext longtext longtext"})
        // .number_format(function(d){return d+"longtext longtext longtext longtext longtext"})

    d3.select("#viz")
      .style('height','520px')
      .datum(data)
      .call(viz);


    d3.select("#loader").style("display", "none");

      d3.selectAll(".node, .d3plus_network_connection").on("mouseup", function() {

        // Update the keys based on product category availability
      })
    })

    // Causes a bug
    //highlight(queryParameters['highlight']);

    if(!embed) {
      key = Key()
        .classification(rawData.class)
        .showing(item_type)

/*
      d3.select(".key")
        .datum(attr_data)
        .call(key);
*/
      controls = Controls()
        .app_type(app_name)
        .year(year)

      d3.select("#tool_pane")
        .datum(rawData)
        .call(controls);
    }

  }

  network = function() {

    // Loading graph nodes positions and links
    if(item_type=="product") {
      (prod_class=="hs4") ? req = "/media/js/data/network_hs.json" :
                            req = "/media/js/data/network_sitc.json";
    } else {
      req = "/media/js/data/network_country.json";
    }

    d3.json(req, function(hs) {

      viz = d3plus.viz();
      viz_nodes = hs.nodes
      viz_links = hs.edges

      // Create node ids
      viz_nodes.forEach(function(node) {

        if(item_type == "product") {

          if (prod_class=="hs4"){
            node.item_id = attr[node.id.slice(2,6)]['item_id']
            node.id = node.id.slice(2,6);
          } else {
            node.item_id = node.id
            node.id = node.code
          }

        } else {
          node.item_id = node.id;
        }

      }) // end of viz_nodes.forEach

    if(item_type == "product") {

      if (prod_class=="hs4") {
        viz_links.forEach(function(link){
          link.source = viz_nodes[link.source]
          link.target = viz_nodes[link.target]
        })
      } else {
        viz_links.forEach(function(link){
          link.source = viz_nodes.filter(function(d){ return d.code == link.source })[0]
          link.target = viz_nodes.filter(function(d){ return d.code == link.target })[0]
        })
      }

      // Making sure no missing world_trade value
      flat_data.map(function(d) {

        if (typeof world_totals[d.year].filter(function(z){ return d.item_id==z.product_id })[0] != "undefined") {
          d.world_trade = world_totals[d.year].filter(function(z){ return d.item_id==z.product_id })[0]['world_trade']
        } else { // if not then assign value as 0
          d.world_trade = 0
        }

      })

      data = [];

      // Create list of unique years
      the_years = d3plus.utils.uniques(flat_data,"year");

      // Fill the data object with data from all the years
      the_years.forEach(function(year) {

        var this_year = flat_data.filter(function(p){ return p.year == year})

        viz_nodes.forEach(function(n) {

          if (prod_class=="hs4") {

           // Required for color by PCI
           //var dd = flat_data.filter(function(p){ return p.year == year && p.code == n.id })[0]
           var d = this_year.filter(function(p){ return p.code == n.id })[0]

           if (typeof d == "undefined") {
            var d = {};
            // d.world_trade = world_totals[year].filter(function(z){ return n.item_id==z.product_id })[0]['world_trade']
           }

            // Required for color by PCI
            // if( (typeof(dd) != "undefined") && (typeof(dd.complexity) != "undefined"))
            //  n.complexity = dd.complexity;
            // else
            //  n.complexity = 0;

            d.world_trade = world_totals[year].filter(function(z){ return n.item_id==z.product_id })[0];

            // Added for 2012 data
            if(typeof(d.world_trade) != "undefined")
              d.world_trade = d.world_trade['world_trade'];

          } else {

            var d = this_year.filter(function(p){ return p.id == n.code })[0]

            if (typeof d == "undefined")
              {
                var d = {}
              }

            // Double check if this product existed then
            var test = world_totals[year].filter(function(z){ return n.item_id==z.product_id })[0]//['world_trade']

            if (typeof test != "undefined") {
              d.world_trade = test['world_trade']
            } else { // if not then assign value as 0
              d.world_trade = 0
            }

          }

          // obj.year = year;
          d.active = d.rca >=1 ? 1 : 0;
          data.push(d)

        })

        this_year = []
      })


    } else { // if item_type == country

      // Conver the links with the right index
      viz_links.forEach(function(link){
        link.source = viz_nodes[viz_nodes.map(function(d) { return d.id; }).indexOf(link.source)]
        link.target = viz_nodes[viz_nodes.map(function(d) { return d.id; }).indexOf(link.target)]
      })

      data = [];

      // Create list of unique years
      the_years = d3plus.utils.uniques(rawData.data, "year");

      // Fill the data object with data from all the years
      the_years.forEach(function(year) {

        var this_year = flat_data.filter(function(p){ return p.year == year})

        viz_nodes.forEach(function(n) {

          var d = {};
          var test = this_year.filter(function(p){ return p.abbrv == n.id })[0]

          if (typeof test != "undefined") {

            d.year = test.year;
            d.rca = test.rca;
            d.name = test.name;
            d.item_id = n.item_id;
            d.region = n.region;
            d.eci = n.eci;
            d.pop = n.pop;
            d.color = test.color;
            d.id = n.id;

          } else {

            // This causes a problem for the missing countries
            d.pop = n.pop;
            d.id = n.id;
            d.name = d.abbrv;
            d.item_id = n.item_id
            d.year = year;
            d.rca = 0;
            d.eci = n.eci;
            d.color = "#fff";
          }

          d.active = d.rca >=1 ? 1 : 0;
          data.push(d);

        });

      });

    }

    viz
      .type("network")
      .width(width)
      .height(height)
      .links(viz_links)
      .nodes(viz_nodes)
      .attrs(attr)
      .value_var("value")
      .name_array(["value"])
      .nesting([])
      .tooltip_info(["id","value","complexity","distance","rca","world_trade"])
      .total_bar({"prefix": "", "suffix": " USD", "format": ",f"})
      .text_format(txt_format)
      .number_format(num_format)
      .font("PT Sans Narrow")
      .year(year)
      .click_function(inner_html)

    if(item_type=="country") {

      viz
        .name_array(["name"])
        .tooltip_info(["pop", "id", "eci"])
        .attrs(attr_data)
        .value_var("rca");
    }


    d3.select("#loader").style("display", "none");

    // If there is no title bar, we're gona bump the viz down
    //  d3.select("#viz").style("margin-top","15px")

    d3.select("#viz")
      .style('height','520px')
      .datum(data)
      .call(viz);

    if(queryActivated)
      highlight(queryParameters['highlight']);

    }) // end of d3.json

    if(!embed) {

      key = Key()
        .classification(rawData.class)
        .showing(item_type)

      d3.select(".key")
        .datum(attr_data)
        .call(key);

      controls = Controls()
        .app_type(app_name)
        .year(year)

      d3.select("#tool_pane")
        .datum(rawData)
        .call(controls);
    }

  }

  map = function() {
    // clean up attribute data
    // initialize the app (build it for the first time)
    app = App()
      .width(width)
      .height(520)
      .year(year)

    d3.select("#loader").style("display", "none");

    // call app function (depending on which is loaded with the page)
    // on the given selection(s)
    d3.select("#viz")
      .style("height", height+"px")
      .datum(rawData)
      .call(app);

    if(!embed){
      /* Not used + adds visual artifacts on static images
      key = Key()
        .classification(rawData.class)
        .showing(item_type)

      // timeline = Timeline()
      //   .app_type(type_of_app)
      //   .year(year)

      controls = Controls()
        .app_type(app_name)
        .year(year)

      d3.select(".key")
        .datum(attr_data)
        .call(key);

      // d3.select("#timeline")
      //   .datum(data.data)
      //   .call(timeline);

      d3.select("#tool_pane")
        .datum(rawData)
        .call(controls);
        */
    }

    d3.select("#mdv").attr("fill", "white");
  }


  function build_viz_app(api_uri,w,h){
    // Are we headless
    var headless_flag = checkParameterExists( "headless" );

    // Only do the below if we are not running headless
    if ( headless_flag == false ) {
        d3.html( api_uri, function(raw)
        {
          // This needs to be global
          rawData = raw;
          height = h;
          width = w;

          // Check if we can get a proper rawData object
          if ( rawData.firstChild != null ) {
              /*// Try replacing the data from g
              if ( typeof rawData.firstChild.childNodes[1] != "undefined" || rawData.firstChild.childNodes[3] != null ) {
                // We have the nodes, so go ahead
                rawData.firstChild.childNodes[1].setAttribute( 'class', 'titles-old' );
              }

              // Check if it the nodes are available first
              if ( typeof rawData.firstChild.childNodes[3] != "undefined" || rawData.firstChild.childNodes[3] != null ) {
                // Check if we have the g.nodes stuff
                jQuery( rawData.firstChild.childNodes[3] ).find( "g" ).each( function(g_index, g_element) {
                    // Update the classes
                jQuery( g_element ).attr( 'class', jQuery( g_element ).attr( 'class' ) + "-old" );
                } );

                // We have the nodes, so go ahead
                rawData.firstChild.childNodes[3].setAttribute( 'class', 'parent-old' );
              }*/

              // Check the raw data
              if ( typeof rawData != "string" ) {
                  // Set the data now to the viz container
                  jQuery( "#loader" ).html( rawData );
              }

              // Do some CSS stuff for the loader container
              d3.select("#loader").style("width", "750px").style("height", "670px").style("margin-top", "-150px").style("text-align", "left");

              // Reset the min-height for now on the #viz node
              d3.select("#viz").style( "min-height", "0px" ).style( "height", "0px" );
          }
        });
    }
  }

  function build_viz_app_original(api_uri, w, h) {

  //d3.json(api_uri,function(raw) {

    (prod_class=="hs4") ? product_file = "media/js/data/sitc4_attr_en.json" :
                          product_file = "media/js/data/hs4_attr_en.json"

    //d3.json(product_file, function(attr_data_file) {

    var single_year_param = "";

    //if(app_type=="casy" && (app_name=="tree_map" || app_name=="product_space" || app_name=="country_space")) {
    //  single_year = true;
    //  single_year_param = "&amp;single_year=true";
    //}

    d3.json(api_uri + '&amp;data_type=json' + single_year_param, function(error, raw) {

      // This needs to be global
      rawData = raw;
      height = h;
      width = w;

      item_type = raw["item_type"];
      flat_data=raw["data"];
      attr=raw["attr"];
      attr_data = raw["attr_data"];
      //app_type= raw["app_type"];
      //prod_class = raw["prod_class"];
      region_attrs = {};

      if(error){
        $("#viz").html("<div id='dataError'><img src='../media/img/all/loadError.png'><h2><b>Data not found</b></h2><ul><li>The data may not exist</li><li>It's values may be too small</li><li>It may not have been reported</li><li><a href='https://github.com/cid-harvard/atlas-data'>View our data</a></li></ul></div>")
          .css("position", "relative")
          .css("top", $("#viz").height()*0.30);
      }

      // Data is found, but it is not usable to generate visualization
      if(rawData.data.length == 0) {  // <<<<<<<<< TODO: What is the threshold for this??

        $("#loader").css("display", "none");
        $("#viz").html("<div id='dataError'><img src='../media/img/all/loadError.png'><h2><b>Data not found</b></h2><ul><li>The data may not exist</li><li>It's values may be too small</li><li>It may not have been reported</li><li><a href='https://github.com/cid-harvard/atlas-data'>View our data</a></li></ul></div>")
          .css("position", "relative")
          .css("top", $("#viz").height()*0.30);

      } else {

/*
         if(rawData.data.filter(function(d) { return d.year == parseInt(year); }).length == 0) {

                $("#loader").css("display", "none");
                $("#viz").html("<div id='dataError'><img src='../media/img/all/loadError.png'><h2><b>Data not found for the year: "+year+"</b></h2><ul><li>The data may not exist</li><li>It's values may be too small</li><li>It may not have been reported</li><li><a href='https://github.com/cid-harvard/atlas-data'>View our data</a></li></ul></div>")
                  .css("position", "relative")
                  .css("top", $("#viz").height()*0.30);
        }
*/
        if(app_type=="casy") {

          // No attr=raw["attr"] for this one, so where to get it?
          // json_response["attr_data"] = Sitc4.objects.get_all(lang) if prod_class == "sitc4" else Hs4.objects.get_all(lang);
          //  attr_data = attr_data_file.attr_data;
          // magic_numbers = rawData["magic_numbers"]
          world_trade = rawData["world_trade"]
          code_look = rawData["code_look"]

          world_totals = {}
          w_years = d3plus.utils.uniques(world_trade,"year")

          w_years.forEach(function(d){
            world_totals[d] = world_trade.filter(function(p){ return p.year == d})
          });
        }


        if (prod_class == "sitc4" && (app_type == "casy" || app_type == "ccsy")){
          attr_data.map(function(g){
            g.sitc1_name = attr[g.code.slice(0, 1)+"000"].name;
            g.sitc1_id = parseInt(g.code.slice(0, 1)+"000");
            g.sitc1_color = attr[g.code.slice(0, 1)+"000"].color
          });
        }

        rawData.attr_data = clean_attr_data(rawData.attr_data)

        if (app_name=="stacked") {

          flat_data = construct_nest(flat_data)
          stack();

          timeline = Slider()
                    .callback('set_stack_year')
                    .initial_value([parseInt(year_start),parseInt(year_end)])
                    .max_width(670)
                    .title("")

          d3.select("#ui_bottom").append("div")
            .attr("class","slider")
            .datum(years_available)
            .call(timeline)

          d3.select('#play_button').style("display","none")
        }

        if (app_name=="tree_map") {
          flat_data = construct_nest(flat_data);

          timeline = Slider()
            .callback('set_year')
            .initial_value(parseInt(year))
            .max_width(670)
            .title("")
          d3.select("#ui_bottom").append("div")
            .attr("class","slider")
            // .style("overflow","auto")
            .datum(years_available)
            .call(timeline)
          d3.select("#ui_bottom").append("br")

          tree();

          if(queryActivated && typeof(queryParameters['cont_id']) != "undefined" && queryParameters['cont_id']!="") {
            var e = document.createEvent('UIEvents');
            e.initUIEvent("click", true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
            d3.select(".cat_"+queryParameters['cont_id']).node().dispatchEvent(e);
          }

          if(queryActivated && typeof(queryParameters['cat_id']) != "undefined" && queryParameters['cat_id']!="") {
            var e = document.createEvent('UIEvents');
            e.initUIEvent("click", true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
            d3.select(".cat_"+queryParameters['cat_id']).node().dispatchEvent(e);
          }

           $("#highlight_select").select2("val", queryParameters['highlight']);
        }

        if (app_name=="pie_scatter") {

          if (prod_class == "sitc4"){
            flat_data = flat_data.filter(function(d){
              return d.distance != 0;
            });
          }

          flat_data = construct_scatter_nest(flat_data);
          pie_scatter();

          timeline = Slider()
                    .callback('set_scatter_year')
                    .initial_value(parseInt(year))
                    .max_width(670)
                    .title("")

          d3.select("#ui_bottom").append("div")
            .attr("class","slider")
            .datum(years_available)
            .call(timeline)

          if(typeof(queryParameters['cat']) != "undefined" && queryParameters['cat']!="" && queryActivated) {
            var e = document.createEvent('UIEvents');
            e.initUIEvent("click", true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
            d3.select(".cat_"+queryParameters['cat']).node().dispatchEvent(e);
          }
        }

        if(app_name == "product_space" || app_name == "country_space") {

          flat_data = construct_nest(rawData.data);
          network();

          timeline = Slider()
            .callback('set_year')
            .initial_value(parseInt(year))
            .max_width(670)
            .title("")

          d3.select("#ui_bottom").append("div")
            .attr("class","slider")
            // .style("overflow","auto")
            .datum(years_available)
            .call(timeline)

          d3.select("#ui_bottom").append("br")
        }

        if(app_name=="rings") {

          flat_data = construct_scatter_nest(flat_data);
          rings(api_uri + '&amp;data_type=json');

          timeline = Slider()
            .callback('set_year')
            .initial_value(parseInt(year))
            .max_width(670)
            .title("")

          d3.select("#ui_bottom").append("div")
            .attr("class","slider")
            // .style("overflow","auto")
            .datum(years_available)
            .call(timeline)

          d3.select("#ui_bottom").append("br")

        }

        if(app_name=="map") {

          map();

          timeline = Slider()
            .callback('set_map_year')
            .initial_value(parseInt(year))
            .max_width(670)
            .title("")
          d3.select("#ui_bottom").append("div")
            .attr("class","slider")
            // .style("overflow","auto")
            .datum(years_available)
            .call(timeline)
          d3.select("#ui_bottom").append("br")

          // Fix wrong shape file with MDV
          d3.select("#MDV").style("display", "none")
        }

        if(app_name=="scatterplot") {

          scatterplot();

          timeline = Slider()
                    .callback('set_scatter_year')
                    .initial_value(parseInt(year))
                    .max_width(670)
                    .title("")

          d3.select("#ui_bottom").append("div")
            .attr("class","slider")
            .datum(years_available)
            .call(timeline)

        }

        if(app_name=="rankings") {

          flat_data = construct_nest(flat_data);

          timeline = Slider()
            .callback('set_year')
            .initial_value(parseInt(year))
            .max_width(670)
            .title("")
          d3.select("#ui_bottom").append("div")
            .attr("class","slider")
            // .style("overflow","auto")
            .datum(years_available)
            .call(timeline)
          d3.select("#ui_bottom").append("br")

          rankings();

        }

      }
    }) // attr
 // }) // api_uri
}
