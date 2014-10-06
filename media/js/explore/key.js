function Key() {
  var showing = "product",
    classification = "hs4";
    
  function key(selection) {
    selection.each(function(attrs, i) {
      
      // unique list of categories
      cats = pretty_cats(attrs);
      sitcs = pretty_sitcs(attrs);
      
      if (prod_class == "sitc4" && (app_type=="casy"||app_type=="ccsy")) {
        d3.select(this)
          .attr("id", "sitc1")
          .selectAll("a").data(d3.values(sitcs))
          .enter()
            .append("a")
            .call(key_icon)
      }
      else 
      {
      d3.select(this)
        .attr("id", classification)
        .selectAll("a").data(d3.values(cats))
        .enter()
          .append("a")
          .call(key_icon)
      }

    })
  }
  
  ////////////////////////////////////////////
  // PRIVATE functions for this app shhhhh...
  ////////////////////////////////////////////
  
  // Find the unique categories from list of attributes
  function pretty_cats(attrs){
    cats = {}
    d3.values(attrs).forEach(function(d){
      if (d.category_id==undefined){
        return;
      }
      cats[d.category_id] = {}
      d3.keys(d).forEach(function(dd){
        if(dd.indexOf("category") > -1){
          cats[d.category_id][dd.replace("category_", "")] = d[dd]
        }
      })
    })
    return cats
  }
  
  // Find the unique categories from list of attributes
  function pretty_sitcs(attrs){
    sitcs = {}
    d3.values(attrs).forEach(function(d){
      if (d.category_id==undefined){
        return;
      }
      sitcs[d.sitc1_id] = {}
      d3.keys(d).forEach(function(dd){
        
        if(dd.indexOf("sitc1") > -1){
          sitcs[d.sitc1_id][dd.replace("sitc1_", "")] = d[dd]
        }      
      })
    })
    return sitcs
  }
  
  
  // Format the anchor how we want for the given category
  function key_icon(a){
    a.attr("title", function(d){ return d.name; })
    a.attr("data-placement", "bottom")

    // Check if any product in this category
    available_cat = Array();

    flat_data.forEach(function(d) {
      if(item_type=="country") { 
        if(typeof(available_cat[d.continent]) == "undefined") {
          available_cat[d.continent] = true;
        }
      } else {
        if(typeof(available_cat[d.community_id]) == "undefined") {
          available_cat[d.community_id] = true;
        }
      }
    })

    // .attr("class", function(d){ return showing + " cat_"+d.id; })
    // depending on whether we're showing products or countries
    // show icons or just text of that region
    if(showing == "product"){

      a.attr("class", function(d){ return showing + " tooltipbs cat_"+d.id; });

      if(prod_class == "hs4")
        a.style("opacity", function(d){ return typeof(available_cat[d.id]) == "undefined" ? .2 : 1; })
      a.append("img")
        .attr("src", function(d){
          return "/media/img/icons/community_"+d.id+".png"
        })
        
    }
    else {

       a.style("background", function(d){ return d.color; })
        .attr("class", function(d){ return showing + " tooltipbs cat_"+d.id+" "+d.continent; })
        .attr("continent", function(d){ return d.continent; })
        .text(function(d){ return name(d.name);})
        .style("opacity", function(d){ return typeof(available_cat[d.continent]) == "undefined" ? .2 : 1; })
    }
    // mouseover events (extends the specific apps highlight funciton)
    a.on("mouseover", function(d){
       // console.log(d, "keys.js");
        // d3.select("#viz").call(viz.solo([d.name]));
        // d3.select("#viz").call(viz.highlight(d.id));
      })
      .on("mouseout", function(d){
        // d3.select("#viz").call(viz.solo([]));
        // d3.select("#viz").call(viz.highlight(null));
      })


    a.on("click", function(d) {

      if(showing == "product") {

        if(prod_class == "hs4") {
          // Disable categories if not available
          if(typeof(available_cat[d.id]) == "undefined")
              return;
          }
      } else {
        if(typeof(available_cat[d.continent]) == "undefined")
          return;
      }

      // If this node is already selected, return to unsorted
      console.log("click", d3.select(this), d)

      // Make sure no product/country is hihglighted
      reset_highlight()

      if (d3.select(this).attr("active") == "true") {
        d3.select("#viz").call(viz.solo([]));
        d3.select(this).attr("active","false");
        d3.selectAll("."+d.continent).attr("active","false");

        d3.selectAll(".key a").style("pointer-events","auto")  
                              .style("cursor","");

        if(showing == "product") {
          if(prod_class == "hs4")
            d3.selectAll(".key a").style("opacity", function(d){ return typeof(available_cat[d.id]) == "undefined" ? .2 : 1; })
          else
                        d3.selectAll(".key a").style("opacity", function(d){ return 1; })
        } else {
          d3.selectAll(".key a").style("opacity", function(d){ return typeof(available_cat[d.continent]) == "undefined" ? .1 : 1; })          
        }

        sessionStorage.removeItem("productCommunityName");
        sessionStorage.removeItem("productCommunityID"); 

        queryParameters['cat_id'] = "";
        queryParameters['cont_id'] = "";
      }
      // Otherwise, we need to filter just this community
      // by using VizWiz soloing functionality 
      else  {
        // Grey out the other communities
        d3.selectAll(".key a").style("opacity",".3")
                              .style("pointer-events","none")
                              .style("cursor","default");
        
        // Now we'll keep our selection highlighted
        // Check to see app is display country info, in which case
        // we need filter by continent              
        if (d.continent != undefined) {
          // If this is a continent, we want to select all the regions
          d3.selectAll("."+d.continent).style("opacity","1")
                                   .style("pointer-events","auto")  
                                   .style("cursor","")                 
                                   .attr("active","true"); 
          

          //d3.select("#viz").call(viz.solo([d.continent]));
          d3.select("#viz").call(viz.solo(flat_data.filter(function(dd) { 
            if(dd.nesting_0.name == d.continent)// && dd.year==year) 
              return dd;
          }).map(function(ddd) { 
            if(app_name == "product_space" || app_name == "country_space")
              return ddd.abbrv;
            else
              return ddd.id;
          })));

          sessionStorage.setItem("continent",d.continent);
          queryParameters['cont'] = d.id;
          // app_name=="stacked" ? stack_solo_filter(d.continent) : d3.select("#viz").call(viz.solo([d.continent]));
        }
        // or we can simply filter by product community name
        else 
        {
          d3.select(this).style("opacity","1")
                         .style("pointer-events","auto")  
                         .style("cursor","")                 
                         .attr("active","true"); 


          // OLD
          //d3.select("#viz").call(viz.solo([d.name]));           
          d3.select("#viz").call(viz.solo(flat_data.filter(function(dd) { 
            if(dd.nesting_0.name == d.name) // removed  && dd.year==1995
              return dd;
          }).map(function(ddd) { 
            return ddd.id;
          })));

          // app_name=="stacked" ? stack_solo_filter(d.name) : d3.select("#viz").call(viz.solo([d.name]));
	        sessionStorage.setItem("productCommunityName",d.name);
          sessionStorage.setItem("productCommunityID",this.className.replace(" ","."));	
          queryParameters['cat_id'] = d.id;
          //console.log("Filter by", d, flat_data.filter(function(d) { if(d.nesting_0.name == d.name && d.year==year) return d}).map(function(d) { return d.id }));
        }              
                       
      }
      if(queryActivated)
        history.replaceState({}, "Title", window.location.origin+window.location.pathname+"?"+$.param(queryParameters));

        
    }) 
    
    a.style("border",function(d){
      if (d.name == "X"){
        return "1px solid red";
      }
      
    })
    
  }
  
  
  // HELPER FUNCTION to shorten names so they fit on one line
  // totally for aesthetics braaaaaa....
  function name(long_name){
    var short_name = long_name;
    short_name = short_name.replace("South-Eastern", "SE")
    short_name = short_name.replace("Eastern", "E")
    short_name = short_name.replace("Northern", "N")
    short_name = short_name.replace("Southern", "S")
    short_name = short_name.replace("South", "S")
    short_name = short_name.replace("Western", "W")
    short_name = short_name.replace("Central", "C")
    return short_name;
  }
  
  function stack_solo_filter(name){
      var nest_level = ($("#nesting_level").val());
      var use_this
      if (nest_level == "nest0"){
        //if we're display countries sort by 2nd tier 
        (app_type=="csay"||app_type=="cspy"||app_type=="sapy") ? 
        use_this = nest1_value : use_this = nest0_value
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
      console.log("unq", unq)
      d3.select("#viz").call(viz.solo(unq));  
  }
  ////////////////////////////////////////////
  // PUBLIC getter / setter functions
  ////////////////////////////////////////////
  key.showing = function(value) {
    if (!arguments.length) return showing;
    showing = value;
    return key;
  };
  
  key.classification = function(value) {
    if (!arguments.length) return classification;
    classification = value;
    return key;
  };

  key.disable = function(list) {

    // Only works for rings

    // Re-enable all

    for(var p in cats) {
      d3.selectAll(".cat_"+p).style("opacity", "1").style("pointer-events", "auto");
    };

    list.forEach(function(d) {
      d3.selectAll(".cat_"+d).style("opacity", ".05").style("pointer-events", "none"); // "auto"
    });

  }
  
  /////////////////////////////////////////////////////////////////////
  // BE SURE TO ALWAYS RETURN THE APP TO ALLOW FOR METHOD CHAINING
  ///////////////////////////////////////////////////////////////////// 
  return key;
}
