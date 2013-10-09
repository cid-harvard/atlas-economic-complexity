  var flat_data,
      attr,
      complexity,
      viz,
      timeline,
      rawData,
      where = []
      // year = "{{year}}";
  
  // Some convenience methods baby~~
  Array.prototype.contains = function(obj) {
      var i = this.length;
      while (i--) {
          if (this[i] === obj) {
              return true;
          }
      }
      return false;
  }
  
  Array.prototype.getUnique = function(){
     var u = {}, a = [];
     for(var i = 0, l = this.length; i < l; ++i){
        if(u.hasOwnProperty(this[i])) {
           continue;
        }
        a.push(this[i]);
        u[this[i]] = 1;
     }
     return a;
  }
  // Sort array by year helper
  function compareYears(a, b) 
  {
    return a.year - b.year;
  }
  
  function nest_drop_report(nest_level) 
  {
    // Find Out app_type
    switch (app_name)
    {
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
        set_depth(nest_level)
        break;
    }
    
  }
  
  get_totals = function()
  {
    annual = {}  
    years_available.forEach(function(d){
      data = rawData["data"];
      flat = data.filter(function(g){ return g.year == d; })
      if(app_type=='casy'||app_type=='ccsy'){
        flat = flat.filter(function(z){ return z.community_id != undefined})
      }
      else
      {
        flat = flat.filter(function(z){ return z.region_id != undefined})
      }
      
      sort_flat(flat)
      x = d3.sum(flat, function(t){ return t["value"] })
      annual[d] = x
    })
    // d3.sum(current, function(d){ return d["value"] })
  }     
  
  set_depth = function(arg)
  {
    d3.select('#viz').call(viz.depth(arg))    
  }
  
  check_category_presence = function(arg)
  {
    missing = []
    current = []
    arg.forEach(function(d){
      current.push(d.name)
    })
    
    if (prod_class=="sitc4"){
      $.each(sitcs,function(key,val){
          if(current.contains(val.name)){
            console.log("yes")
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
            console.log("yes")
            return true;
          }
          missing.push(val);
          return false;
        })
    }
    return missing;
  }
  
  set_stack_layout = function(arg)
  {

    if (arg=="share"){
      // set_stack_nesting(nest0_val);
      d3.select("#viz").call(viz.layout("share"));
      // d3.select("#viz").call(viz.value_var("my_share"));
    } 
    else if(arg=="value")
    {
      // Just double check if this app has adjustment values
      d3.select("#viz").call(viz.layout("value"));
        if(app_type=="casy"){
          var adjust = d3.select('input[name=capita]:checked').attr("id")
          switch(adjust)
          {
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
          
        }
        else
        {
          d3.select("#viz").call(viz.value_var("value"));  
        }
    } 
    else if(arg=="current"){
      // d3.select("#viz").call(viz.layout("value"));
      d3.select("#viz").call(viz.value_var("value"));
    }
    else if(arg=="pc_current"){
      // d3.select("#viz").call(viz.layout("value"));
      d3.select("#viz").call(viz.value_var("pc_current"));
    }
    else if(arg=="pc_constant"){
      // d3.select("#viz").call(viz.layout("value"));
      d3.select("#viz").call(viz.value_var("pc_constant"));
    }
    else if(arg=="notpc_constant"){
      // d3.select("#viz").call(viz.layout("value"));
      d3.select("#viz").call(viz.value_var("notpc_constant"));
    }
  }
  // Do I still need this?
  stack_solo_filter = function(name)
  {
      var nest_level = ($("#nesting_level").val());
      var use_this
      if (nest_level == "nest0"){
        //if we're display countries sort by 2nd tier 
        (app_type=="csay"||app_type=="cspy"||app_type=="sapy") ? 
        use_this = nest1_value : use_this = nest0_value;
        console.log(use_this);
      } else if(nest_level == "nest1"){ 
        use_this = nest1_value  
      } else { 
        use_this = nest2_value } 
        
      var solos = []
      use_this.forEach(function(d){
        if (d.nesting_0.name == name){
         solos.push(d.name)
       } 
      });
      unq = solos.getUnique();
      console.log(unq)
      d3.select("#viz").call(viz.solo(unq));  
  }
  // Do I still need this?
  pie_scatter_filter = function(name)
  {
    var nest_level = ($("#nesting_level").val());
    var use_this
    if (nest_level == "nest0"){
      //if we're display countries sort by 2nd tier 
      (app_type=="csay"||app_type=="cspy"||app_type=="sapy") ? 
      use_this = nest1 : use_this = nest0;
      console.log(use_this);
    } else if(nest_level == "nest1"){ 
      use_this = nest1 
    } else { 
      use_this = nest2 } 
      
    var soloing = []
    use_this.forEach(function(d){
      if (d.nesting_0.name == name){
       soloing.push(d)
     } 
    });
    // set_scatter_nesting(everybody)
    set_depth(soloing)
  }
  // Do I still need this?
  pie_scatter_solo = function(name)
  {
      var nest_level = ($("#nesting_level").val());
      var use_this
      if (nest_level == "nest0"){
        //if we're display countries sort by 2nd tier 
        (app_type=="csay"||app_type=="cspy"||app_type=="sapy") ? 
        use_this = nest1 : use_this = nest0;
        console.log(use_this);
      } else if(nest_level == "nest1"){ 
        use_this = nest1 
      } else { 
        use_this = nest2 } 
        
      var solos = []
      use_this.forEach(function(d){
        if (d.nesting_0.name == name){
         solos.push(d.name)
       } 
      });
      unq = solos.getUnique();
      console.log(unq)
      d3.select("#viz").call(viz.solo(unq));  
  }
  // Do I still need this?
  sort_flat = function(arg)
  {
      arg.forEach(function(d){ 
        if (trade_flow=="net_export"){
            val = d.export_value - d.import_value;
            if (val > 0 ){ 
              d.value = d.export_value - d.import_value;
              // where.push(d);
            }
          } else if (trade_flow=="net_import") {
             val = d.import_value - d.export_value;
             if (val > 0 ){ 
               d.value = d.import_value - d.export_value;
               // where.push(d);
              }        
          } else if (trade_flow=="export"){
            if (d.export_value > 0){
              d.value = d.export_value;
              // where.push(d);
            }
          } else {
            if (d.import_value > 0){
              d.value = d.import_value;
              // where.push(d);
            }
          }
        })
  }
  
  set_stack_year = function(arg)
  {   
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
    
    
  }
  
  set_scatter_year = function(arg)
  {
    var nest_level = ($("#nesting_level").val());
    year=arg
    set_depth(nest_level)
    d3.select("#viz").call(viz.year(arg))
  }
  
  set_year = function(arg)
  {

    console.log("dragging slider", "viz_general.js", arg)
    var treemap_title = d3.select('#text_title').text();
    treemap_title = treemap_title.replace(viz.year(), arg);
    d3.select('#text_title').text(treemap_title);
    
    // TODO: Check if IE compliant
    window.history.pushState('The Atlas', d3.select('#text_title').text(),  window.location.href.replace(viz.year(), arg));

  // TODO
  // In which particular case are we?
  // 
   // What does %s %s?" % (countries[0].name, trade_flow.replace("_", " "), year)

    d3.select('#viz').call(viz.year(arg))
    // Set the controls to this year as well
    d3.select("#tool_pane").call(controls.year(arg)); 
    $(".app_title#icons h2").text(arg)
  }
  
  set_map_year = function(arg)
  {
    d3.select("#viz").call(app.year(parseInt(arg)));
    // Set the controls to this year as well
    d3.select("#tool_pane").call(controls.year(arg)); 
  }
  
  construct_nest = function(flat)
  {
    // Ask for visualizations that need to be sorted by export/import/net values
    if (app_type == "casy" || app_type == "sapy" || app_type == "ccsy")
    {
      
      // sort_flat(flat); 
      
      if (app_type == "casy" || app_type=="ccsy")
      {
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
      } 
      else //SAPY query displays country information and needs different tailored nesting
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
  // Do I still need this?
  construct_scatter_nest = function(flat)
  {
    flat = flat.filter(function(d){ return d.community_id != undefined; })
    
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
  
  num_format = function(value,name)
  { 
    switch(name)
    {
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
  
  txt_format = function(words)
  {
    switch(words)
    {
     case 'pc_constant':
       return "Per Capita Constant"
       break;
     case 'year':
       return "Year"
       break;   
     case 'pc_current':
       return "Per Capita Current"
       break;
     case 'notpc_constant':
       return "Constant"    
       break;
     case 'value':
       return "Current"
       break;
     case 'distance':
       return "Distance"
       break;
     case 'share':
       return "Share"
       break;   
     case 'complexity':
       return "Complexity"
       break;
     case 'rca':
       return 'RCA'
       break;
     case 'id':
       return "Code"
       break;
     case 'world_trade':
       return "World Trade"
       break;
     case 'active':
       return "Active"
       break;
     case 'opp_gain':
       return "Opportunity Gain"
       break;                                      
     default: 
       return words     
    }
  }
  
  tree = function()
  {
    viz = vizwhiz.viz()
    viz
      .type("tree_map")
      .height(height)
      .width(width)
      .id_var("id")
      .attrs(attr)
      .text_var("name")
      .value_var("value")
      //.tooltip_info({"short":["value","distance", "complexity","year"]})
      .name_array(["name"])
      .total_bar({"prefix": "", "suffix": " USD"})
      .nesting(["nesting_0","nesting_1","nesting_2"])
      .nesting_aggs({"distance":"mean","complexity":"mean"})
      .depth("nesting_1")
      .text_format(txt_format)
      .number_format(num_format)
      .font('PT Sans Narrow')
      .year(year)
      .data_source("Data provided by: ",prod_class)

    d3.select("#loader").style("display", "none");
    
    if(item_type=="country"){
      
      viz.depth("nesting_2") // Updated to low level
         .attrs(region_attrs)

    }
    else
    {
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
      if(item_type!="country")
      {
        at = at.filter(function(d){return d.ps_size != undefined})
      }
      
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

  }
  
  stack = function()
  {
    var years = year.split('.')  

    viz = vizwhiz.viz()
      .type("stacked")
      .height(height)
      .width(width)
      .value_var("value")
      .sort("color")
      .xaxis_var("year")
      .attrs(attr)
      .tooltip_info({"short": ["value", "distance", "year"]})
      .text_var("name")
      .id_var("id")
      .nesting(["nesting_0","nesting_1","nesting_2"])
      .depth("nesting_0")
      .text_format(txt_format)
      .font('PT Sans Narrow')
      .number_format(num_format)
      .stack_type("monotone")
      // .year([year_start,year_end])
      //.year([years_available[0],years_available.slice(-1)[0]])

    d3.select("#loader").style("display", "none");
  
       flat_data.map(function(d){
         d.id = String(d.id)
       })
       
       if (app_type!="sapy")
       {
         magic_numbers = rawData["magic_numbers"]
         viz.tooltip_info({"short": ["distance", "year", "pc_current","pc_constant","notpc_constant"]})
         flat_data.map(function(d){
           d.pc_constant = magic_numbers[d.year]["pc_constant"] * d.value
           d.pc_current = magic_numbers[d.year]["pc_current"] * d.value
           d.notpc_constant = magic_numbers[d.year]["notpc_constant"] * d.value
         })
       }
       
       if(item_type=="country")
       {
         viz.depth("nesting_1")
         viz.sort("color")
         viz.attrs(region_attrs) // For now this appears to be broken for country/region nesting
       }
       
       // Since there is no title bar, we're gona bump the viz down 
       d3.select("#viz").style("margin-top","15px")
       
       flat_data = flat_data.filter(function(d){ return d.share > 0.0075})

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
            if($(e.target).attr("name") == "labels"){
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
          
        }
        else
        { 
          // in this instance we're not getting year start/stop dates from explore view;
          //we need to figure them out from api
          var years = year.split('.')
          year_s = years[0]  
          year_e = years[1]
          d3.select("#viz").call(viz.years([years_s,years_e]))
        }
  }

  pie_scatter = function()
  {
    // exists = rawData["scatter"]
    // if(exists)
    // {
      viz = vizwhiz.viz()
    
      viz
        .type("pie_scatter")
        .height(height)
        .width(width)
        .tooltip_info({"short": ["value", "distance", "complexity","rca"]})
        .text_var("name")
        .id_var("id")
        .attrs(attr)
        .xaxis_var("distance")
        .yaxis_var("complexity")
        .value_var("world_trade")
        .total_bar({"prefix": "", "suffix": " USD", "format": ",f"})
        .nesting(["nesting_0","nesting_1","nesting_2"])
        .nesting_aggs({"complexity":"mean","distance":"mean","rca":"mean"})
        .depth("nesting_0")
        .text_format(txt_format)
        .number_format(num_format)
        .spotlight(false)
        .dev(false)
        .font('PT Sans Narrow')
        .static_axis(false)
        .year(year)
      
      d3.select("#loader").style("display", "none");
    
      flat_data = flat_data.filter(function(d){ return d.share > 0.00125})
    
      flat_data.map(function(d){
        d.world_trade = world_totals[d.year].filter(function(z){ return d.item_id==z.product_id })[0]['world_trade']
        d.id = String(d.id)
      })
    
    
      d3.select("#viz")
        .style('height','520px')
        .datum(flat_data)
        .call(viz) 

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
      //}
    // else 
 //    {
 //      d3.select("#loader").style("display", "none");
 //      d3.select("#viz")
 //        .style("height","440px")
 //        .append("div").attr("id","missing")
 //      
 //      d3.select("#missing")
 //        .style("padding-top","200px")
 //        .style("padding-left","165px")
 //        .text("Sorry! We do not (yet) support Diversification Options for this country.")  
 //    }
  }
  
  network = function()
  { 
    (prod_class=="hs4") ? req = "/media/js/libs/vizwiz/examples/data/network_hs.json" : 
                          req = "/media/js/libs/vizwiz/examples/data/network_sitc2.json"
    
    d3.json(req, function(hs) {
      viz = vizwhiz.viz()
      
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
      
      flat_data.map(function(d){
        d.world_trade = world_totals[d.year].filter(function(z){ return d.item_id==z.product_id })[0]['world_trade']
      })
      
      data = []
      the_years = vizwhiz.utils.uniques(flat_data,"year")
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
            d.world_trade = world_totals[year].filter(function(z){ return n.item_id==z.product_id })[0]['world_trade']
            
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
              // var obj = {}
              // obj.name = attr[n.code].name
              // obj.id = attr[n.code].code
              // obj.world_trade = d.world_trade
              // d.world_trade = testworld_totals[year].filter(function(z){ return n.id==z.product_id })[0]['world_trade']
            // }
            // else // We still need to assign a world trade value
            // {
            //   // d.world_trade = world_totals[year].filter(function(z){ return n.id==z.product_id })[0]['world_trade']
            // 
            //   test = world_totals[year].filter(function(z){ return n.item_id==z.product_id })[0]//['world_trade']
            //   if(typeof test != "undefined"){
            //     d.world_trade = test['world_trade']
            //   }
            //   else{
            //     d.world_trade = 0
            //   }
            //           
            //   var obj = vizwhiz.utils.merge(d,attr[n.id])
            //   obj.id = attr[n.code].code
            //   obj.world_trade = d.world_trade
            // }
          }
        
          // obj.year = year;
          d.active = d.rca >=1 ? 1 : 0
          data.push(d)
          
        })
        
        this_year = []
      })
      
      
      // data = []
      // the_years = vizwhiz.utils.uniques(flat_data,"year")
      // the_years.forEach(function(year){
      //   viz_nodes.forEach(function(n){
      //     if (prod_class=="hs4")
      //     {
      //       var d = flat_data.filter(function(p){ return p.year == year && p.code == n.id })[0]
      //       var obj = vizwhiz.utils.merge(d,attr[n.id])
      //       if (typeof d == "undefined"){
      //         var d = {}
      //         d.world_trade = world_totals[year].filter(function(z){ return n.item_id==z.product_id })[0]['world_trade']
      //       }
      //       else // We still need to assign a world trade value
      //       {
      //         d.world_trade = world_totals[year].filter(function(z){ return n.item_id==z.product_id })[0]['world_trade']
      //       }
      //       obj.world_trade = d.world_trade
      //     }
      //     else 
      //     {
      //       var d = flat_data.filter(function(p){ return p.year == year && p.id == n.code })[0]
      //       if (typeof d == "undefined")
      //       {
      //         var d = {}
      //         // Double check if this product existed then
      //         test = world_totals[year].filter(function(z){ return n.id==z.product_id })[0]//['world_trade']
      //         if(typeof test != "undefined"){
      //           d.world_trade = test['world_trade']
      //         }
      //         else // if not then assign value as 0
      //         {
      //           d.world_trade = 0
      //         }
      //         var obj = {}
      //         obj.name = attr[n.code].name
      //         obj.id = attr[n.code].code
      //         obj.world_trade = d.world_trade
      //         // d.world_trade = world_totals[year].filter(function(z){ return n.id==z.product_id })[0]['world_trade']
      //       }
      //       else // We still need to assign a world trade value
      //       {
      //         // d.world_trade = world_totals[year].filter(function(z){ return n.id==z.product_id })[0]['world_trade']
      //       
      //         test = world_totals[year].filter(function(z){ return n.item_id==z.product_id })[0]//['world_trade']
      //         if(typeof test != "undefined"){
      //           d.world_trade = test['world_trade']
      //         }
      //         else{
      //           d.world_trade = 0
      //         }
      //     
      //         var obj = vizwhiz.utils.merge(d,attr[n.id])
      //         obj.id = attr[n.code].code
      //         obj.world_trade = d.world_trade
      //       }
      //     }
      //   
      //     // var d = flat_data.filter(function(p){ return p.year == year && p.code == n.id })[0]
      //   
      //     // var obj = vizwhiz.utils.merge(d,attr[n.id])
      //     // d.name = attr[n.id].name
      //     obj.year = year;
      //     obj.x = n.x
      //     obj.y = n.y
      //     // obj = vizwhiz.utils.merge(obj,n)
      //     // obj.active = Math.floor(Math.random()*2);
      //     obj.active = d.rca >=1 ? 1 : 0
      //     // console.log(obj);
      //     data.push(obj)
      //     
      //   })
      // })      

  
    viz
      .type("network")
      .width(width)
      .height(height)
      .links(viz_links)
      .nodes(viz_nodes)
      .attrs(attr)
      .value_var("world_trade")
      .name_array(["value"])
      .nesting(["nesting_0","nesting_1","nesting_2"])
      .tooltip_info(["id","value","complexity","distance","rca","world_trade"])
      // .total_bar({"prefix": "", "suffix": " USD", "format": ",f"})
      .text_format(txt_format)
      .number_format(num_format)
      .font("PT Sans Narrow")
      .year(year)

    d3.select("#loader").style("display", "none");  
    
    // Since there is no title bar, we're gona bump the viz down 
    d3.select("#viz").style("margin-top","15px")
    
    d3.select("#viz")
      .style('height','520px')
      .datum(data)
      .call(viz);  
    
    })
    
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
    }      
  }  
  
  map = function()
  {
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
    }
   
  }
  //
  // the sparkplug that drives my vizwiz engine
  //
  
  function build_viz_app(api_uri,w,h){
    d3.json(api_uri,function(raw)
    {
      // This needs to be global 
      rawData = raw;
      height = h;
      width = w;
      
      item_type = raw["item_type"]
      flat_data=raw["data"]
      attr=raw["attr"]
      attr_data = raw["attr_data"]
      app_type= raw["app_type"]
      prod_class = raw["prod_class"]
      region_attrs = {}

      
      
      if(app_type=="casy"){
        // magic_numbers = rawData["magic_numbers"]
        world_trade = rawData["world_trade"]
        code_look = rawData["code_look"]
        
        world_totals = {}
        w_years = vizwhiz.utils.uniques(world_trade,"year")
        w_years.forEach(function(d){
          world_totals[d] = world_trade.filter(function(p){ return p.year == d}) 
        })
        
      }
      
      if (prod_class == "sitc4" && (app_type == "casy" || app_type == "ccsy"|| app_type=="sapy")){
        attr_data.map(function(g){
          g.sitc1_name = attr[g.code.slice(0, 1)+"000"].name; 
          g.sitc1_id = parseInt(g.code.slice(0, 1)+"000");
          g.sitc1_color = attr[g.code.slice(0, 1)+"000"].color
        })
      }
    
      // attr_data = clean_attr_data(attr_data)
      rawData.attr_data = clean_attr_data(rawData.attr_data)
    
      if (app_name=="stacked")
      {
        flat_data = construct_nest(flat_data)
        stack();
        
        timeline = Slider()
                  .callback('set_stack_year')
                  .initial_value([parseInt(year_start),parseInt(year_end)])
                  //[parseInt(years_available[0]),parseInt(years_available.slice(-1)[0])])
                  .max_width(750)
                  .title("")
                d3.select("#ui_bottom").append("div")
                  .attr("class","slider")
                  .datum(years_available)
                  .call(timeline)
        // get rid of play button -->                  
        d3.select('#play_button').style("display","none") 
      } 
      if (app_name=="tree_map")
      {
        flat_data = construct_nest(flat_data);
        tree();
        
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
      if (app_name=="pie_scatter")
      {
        if (prod_class == "sitc4"){
          flat_data = flat_data.filter(function(d){
            return d.distance != 0;
          })
        }
        flat_data = construct_scatter_nest(flat_data);
        // where = flat_data.filter(function(d){ return d.year == year; })
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
        // get rid of play button -->                  
        // d3.select('#play_button').style("display","none") 
      }
      if(app_name=="product_space")
      {
        flat_data = construct_scatter_nest(flat_data);
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
      if(app_name=="map")
      {
        map()
        
        timeline = Slider()
          .callback('set_map_year')
          .initial_value(parseInt(year))
          .max_width(750)
          .title("")
        d3.select("#ui_bottom").append("div")
          .attr("class","slider")
          // .style("overflow","auto")
          .datum(years_available)
          .call(timeline)
        d3.select("#ui_bottom").append("br")  
        
      }
    
      // // Create Year Toggle
      // if (app_name == "tree_map") {
      //   timeline = Slider()
      //     .callback('set_year')
      //     .initial_value(parseInt(year))
      //     .max_width(540)
      //     .title("")
      //   d3.select("#ui_bottom").append("div")
      //     .attr("class","slider")
      //     // .style("overflow","auto")
      //     .datum(years_available)
      //     .call(timeline)
      //   d3.select("#ui_bottom").append("br")
      // }
      // 
      // if (app_name == "stacked")
      // {
      //   timeline = Slider()
      //             .callback('set_stack_year')
      //             .initial_value([parseInt(year_start),parseInt(year_end)])
      //             .max_width(540)
      //             .title("")
      //           d3.select("#ui_bottom").append("div")
      //             .attr("class","slider")
      //             .datum(years_available)
      //             .call(timeline)
      //   // get rid of play button -->                  
      //   d3.select('#play_button').style("display","none")          
      // }
      // 
      // if (app_name == "pie_scatter")
      // {
      //   timeline = Slider()
      //             .callback('set_scatter_year')
      //             .initial_value(parseInt(year))
      //             .max_width(540)
      //             .title("")
      //           d3.select("#ui_bottom").append("div")
      //             .attr("class","slider")
      //             .datum(years_available)
      //             .call(timeline)
      //   // get rid of play button -->                  
      //   d3.select('#play_button').style("display","none")          
      // }
    
    })
  }  
  // 