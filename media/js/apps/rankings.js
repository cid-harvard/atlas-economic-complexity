ranking = window.ranking || {};

window.ranking = ranking;

ranking.viz = function() {

	// Plenty of default params here
  vars = {
    "container" : "#viz",
    "dev" : true,
    "id" : "id",
    "id_var" : "id",
    "data"  : [],
    "year"  : 1995,
    "columns": ["Rank", "year", "Abbrv", "Country"],
    "title": "Ranking table",
    "solo": [],
    "nesting": null,
    "nesting_aggs": {},
  }

  vars.parent = d3.select(vars.container);

  if (vars.dev) console.log("Init")

	d3.select("#viz").select("table").remove();

	if (!vars.data) vars.data = []

	// Constructor
	chart  = function(selection) {	

    selection.each(function(data_passed) {

      if (vars.dev) console.log("Update", vars.year)

			var level = parseInt(vars.depth[vars.depth.length-1]);

			if(level == 0) {

				console.log("level 0", vars.data)


			  var xaxis_sums = d3.nest()
			    .key(function(d){return d[vars.xaxis_var] })
			    .rollup(function(leaves){
			      return d3.sum(leaves, function(d){return d[vars.yaxis_var];})
			    })
			    .entries(vars.data)


			} else if(level == 1) {

			}

			d3.select("#viz").select("table").remove();

		  vars.table = vars.parent.selectAll("table").data([vars.data.filter(function(d) { 

		  	return d.year == vars.year;
	
		  })]);

		  vars.table_enter = vars.table.enter().append("table")
		    .attr('width', vars.table_width)
		    .attr('height', vars.table_height)
		    .attr("class", "sortable");

		  var caption = vars.table_enter.append("caption")
    										.html(vars.title);

			var drag = d3.behavior.drag()
			    .origin(function(d) { return d; })
			    .on("drag", function() { console.log("start drag"); });

	    // Create
	    var thead = vars.table_enter.append("thead"),
	        tbody = vars.table_enter.append("tbody");

	    thead.append("tr").selectAll("th")
	      .data(function() {
	          return vars.columns;
	      })
	      .enter()
	      .append("th")
	      .attr("class", function(d) {
	        if(d=="Rank")
	          return "sorttable_sorted"
	        else 
	          return "sort"
	      })
	      .text(function(d) { return d; })

	      thead.selectAll("tr > th")

	      .on("click", function(d,i) {

	        var is_sorted = (d3.select(this).attr("id") == "sorted");
	        console.log("click")
	        // toggle sorted state
	        thead.selectAll("th").attr("id", null);
	        if (!is_sorted)
	          d3.select(this).attr("id", "sorted");

	        // TODO: Detect the data type
	        if (i == 0) {
	          tbody.selectAll("tr").sort(function(a, b) {
	            var ascending = d3.ascending(a.value, b.value);
	            console.log(ascending, a[1], a)
	            return is_sorted ? ascending : - ascending;
	          });
	        } else if (i == 2 || i == 3) {
	          tbody.selectAll("tr").sort(function(a, b) {
	            var ascending = d3.ascending(parseFloat(a[2]), parseFloat(b[2])) || d3.ascending(a[1], b[1]);
	            return is_sorted ? ascending : - ascending;
	          });
	        }

	      });

			var rows = tbody.selectAll("tr")
				    .data(function(d) { return d; })
				  .enter().append("tr")
				  	.classed("odd", function(d, i) { return (i % 2) == 0; })
				    .selectAll("td")
				    .data(function(d) {
				    	return vars.columns.map(function(c) { return d[c]})
				    	//return d3.values(d); 
				    })
				  .enter().append("td")
				    .style("border", "1px black solid")
				    .style("padding", "5px")
				    //.on("mouseover", function(){ d3.select(this).style("background-color", "aliceblue")})
				    //.on("mouseout", function(){ d3.select(this).style("background-color", "white")})
				    .text(function(d){ return d; })
				    .style("font-size", "12px")


      });
  }

  // Public Variables
  chart.id = function(x) {
    if (!arguments.length) return vars.id;
    vars.id = x;
    return chart;
  };

  chart.id_var = function(x) {
    if (!arguments.length) return vars.id_var;
    vars.id_var = x;
    return chart;
  };

  chart.year = function(x) {
    if (!arguments.length) return vars.year;
    vars.year = x;
    return chart;
  };

  chart.columns = function(x) {
    if (!arguments.length) return vars.columns;
    vars.columns = x;
    return chart;
  };

	chart.height = function(x) {
	  if (!arguments.length) return vars.table_height;
	  vars.table_height = x;
	  return chart;
	};

  chart.width = function(x) {
    if (!arguments.length) return vars.table_width;
    vars.table_width = x;
    return chart;
  };

  chart.container = function(x) {
    if (!arguments.length) return vars.container;
    vars.container = x;
    return chart;
  };

  chart.title = function(x) {
    if (!arguments.length) return vars.title;
    vars.title = x;
    return chart;
  };

  chart.data = function(x) {
    if (!arguments.length) return vars.data;
    vars.data = x;
    return chart;
  };

chart.solo = function(x) {
  if (!arguments.length) return vars.solo;

  if(x instanceof Array) {
    vars.solo = x;
  } else {
    if(vars.solo.indexOf(x) > -1){
      vars.solo.splice(vars.solo.indexOf(x), 1)
    } else {
      vars.solo.push(x)
    }
  }

  return chart;
};

chart.nesting = function(x) {
  if (!arguments.length) return vars.nesting;
  vars.nesting = x;
  return chart;
};

chart.nesting_aggs = function(x) {
  if (!arguments.length) return vars.nesting_aggs;
  vars.nesting_aggs = x;
  return chart;
};

chart.depth = function(x) {
  if (!arguments.length) return vars.depth;
  vars.depth = x;
  return chart;
};


  console.log("update", chart.year())


  return chart;

	}