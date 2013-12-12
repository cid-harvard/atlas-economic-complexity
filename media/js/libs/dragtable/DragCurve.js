/*
    TODO
    -Focus that follows the curve
    -Synch with the table updates
    -Translate the curve to left according to the day
    -Retrieve the colID and team ID with actual values
    -Use the correct cell height
    -Drag top slider at the same time
    -Remove hover on table
    -Transform selected lines as background halo
    -Use correct column
    -Update slider in real time
*/


function DragCurve(params){
    this.snapToTick = params.snapToTick;
    this.parentSVG = params.parentSVG;
    this.margins = params.margins;
    this.width = params.width;
    this.height = params.height;
    this.curve_width = 500;
    this.curve_height = 20*23;
    this.min = params.min;
    this.max = params.max;
    this.x = params.x;
    this.y = params.y;
    this.cell = params.cell;
    this.thumbRadius = params.thumbRadius;
    this.listeners = [];
    this.orientLabels = params.orientLabels;
    this.teamID = params.teamID;
    this.colID = params.colID;

    this.value = params.initValue;
    this.values = params.values;

    this.data = params.data;

    var $this = this;


    this.nbDays = $this.data.length;
    this.nbTeams = $this.data[0].length;
    this.nbCols = $this.data[0][0].length;


    /*
     Initialize the line_data
     */
    $this.line_data = new Array(this.nbCols);
    for(var col=0;col<this.nbCols;col++){
        $this.line_data[col] = new Array(this.nbTeams);
        for(var team=0;team<this.nbTeams;team++){
            $this.line_data[col][team] = new Array(this.nbDays);
            for(var day=0;day<this.nbDays;day++){
                $this.line_data[col][team][day] = {
                    value: $this.data[day][team][col],
                    rank: rankings[day][col].indexOf(team),
                    teamID: team
                };
            }
        }
    }


    this.create();
}

DragCurve.prototype.create = function(){ 
    var $this = this;

    this.axis_scale = d3.scale.ordinal().domain(this.values).rangePoints([0,this.width]);
    this.slider_scale_inverse = d3.scale.linear().domain([0,this.width]).range([this.values[0],this.values[this.values.length-1]]);

    var drag_slider = d3.scale.linear().domain([0, 38]).range([0, $this.width]); 

/*
    // When creating the slider, adjusting according to current time value
    this.sliderGroup = this.parentSVG.append('g')
        .attr('class', 'slider-group')
        .attr('transform', 'translate(' + [this.x - (drag_slider(table.slider.value)), this.y] + ')');

    this.sliderGroup.append("line")
        .attr("class","slider-bar")
        .attr("x2",this.width);

    var sliderAxis = d3.svg.axis()
        .scale(this.axis_scale)
        .orient(this.orientLabels)
        .tickSize(tickHeight,0,tickHeight+this.ticksMargin)
        .tickValues(this.values);

    this.sliderGroup.append("g")
        .attr("class", "slider-axis-thmb")
        .attr("width", this.width)
        .attr("transform","translate("+[0,this.barHeight]+")")
        .append("g")
        .call(sliderAxis);
*/


    this.currentDay =  this.value;

    var CHART_HEIGHT = 20*23;

    this.sliderGroup = this.parentSVG.append('g')
        .attr('class', 'slider-group')
        .attr('transform', 'translate(' + [this.x - (drag_slider(table.slider.value)), 0] + ')');

    //svg.append("rect").attr("width", 200).attr("height", 200).style("fill", "white").style("stroke", "black");

    var data = d3.range(20).map(function(){return Math.random()*10});

    this.curve_scale_x = d3.scale.linear().domain([0, this.values.length]).range([0, this.curve_width]);
    this.curve_scale_y = d3.scale.linear().domain([0, 20]).range([CHART_HEIGHT, 0]);

    var line = d3.svg.line()
      .interpolate(INTERPOLATION)
      .x(function(d,i) { return $this.curve_scale_x(i);})
      .y(function(d) { return $this.curve_scale_y(d);})


//    var g_curves = this.sliderGroup.append("g").attr(".slider-bar");

    // Curve and its halo
    //  var path_halo = this.sliderGroup.append("svg:path").attr("class", "halo").attr("d", line(data))
    path = this.sliderGroup.append("svg:path")
        .attr("d", line($this.line_data[this.colID][this.teamID].map(function(d) { return d.rank })))
        .attr("class", "drag-curve")
        .style("stroke-width", 4)
        .attr("id", "line")

    // Dirty but quick
    // TODO: highlight selected rows
    for(t=0; t<$this.data[0].length; t++) {

      this.sliderGroup.append("svg:path")
        .attr("class", "drag-curve")
        .attr("d", line($this.line_data[this.colID][t].map(function(d) { return t })))
        .style("stroke-width", 2)
        .style("opacity", .4)
        .style("stroke", getTeamColorsFromTeamID(t).primary)
        .transition().duration(500)
        .attr("d", line($this.line_data[this.colID][t].map(function(d) { return d.rank })))


    }

    // TODO: Add bins to the path
    this.sliderGroup.data($this.line_data[this.colID][this.teamID].map(function(d) { return d.rank })).enter().append("circle")          
     // .attr("transform", function(d, i) { console.log(i, d, $this.curve_scale_x(i), $this.curve_scale_y(d)); return "translate(" + $this.curve_scale_x(i) + "," + $this.curve_scale_y(d) + ")"; })
      .attr("x", function(d, i) { return $this.curve_scale_x(i); })
      .attr("y", function(d, i) { return $this.curve_scale_y(d); })
      .attr("dy", ".35em")
      .attr("r", 4)
      .style("fill", function(d) { return "black"; })
      .attr("class", "bins");

    //---------------------------------------------------------------//
    //--------------------------The thumb----------------------------//
    //---------------------------------------------------------------//
    this.thumbGroup = this.sliderGroup.selectAll(".slider-thumb")
        .data([{value: this.value, dx:0}])
        .enter()
        .append("g")
        .attr("class","slider-thumb")
        .attr("transform", function(d){return "translate("+[$this.axis_scale(d.value), 23]+")"})
        .on("mouseover", function(d){
            d3.select(this).style("cursor", "pointer")
        });

    this.thumbGroup.append("circle")
        .attr("r",this.thumbRadius)
        .attr("cx",this.thumbHeight)
     //   .attr("transform", "translate("+[0, $this.find_y_given_x(d3.select("#line"), $this.cell.dx)+23/2]+")")


    function dragSliderStart(d) {
        d.dx = 0;
    }

    function dragSliderMove(d) {
        $this.dragThumb(d3.event);
    }

    function dragSliderEnd(d) {
        d.dx = 0;
        $this.fireEvent("changed");
      //  table.slider.value
    }
};

DragCurve.prototype.dragThumb = function() {
    var $this = this;
    this.cell.dx += d3.event.dx;

    if($this.cell.dx<=0 || $this.cell.dx>=$this.curve_width)
      return;

    d3.select("body").style("cursor", "none")

    // TODO: test if still within the boundaries

    this.sliderGroup.select(".drag-curve")
        .each(function() {


        function find_y_given_x(x) {

          // Showing focus point as preview of dragging point on the line
          // Code from http://bl.ocks.org/duopixel/3824661
          var pathEl = path.node();
          var pathLength = pathEl.getTotalLength();
          var BBox = pathEl.getBBox();
          var scale = pathLength/BBox.width;
          var offsetLeft = document.getElementById("line").offsetLeft;
          var offsetTop = document.getElementById("line").offsetTop;   

          var beginning = x, end = pathLength, target;

          while (true) {
            target = Math.floor((beginning + end) / 2);
            pos = pathEl.getPointAtLength(target);
            if ((target === end || target === beginning) && pos.x !== x) {
                break;
            }
            if (pos.x > x)      end = target;
            else if (pos.x < x) beginning = target;
            else                break; //position found
          }

          return pos.y;
        }

        var mouseX = d3.mouse(this)[0];

        d3.selectAll(".drag-curve").attr("transform", "translate("+[-$this.cell.dx, 23/2]+")")

        $this.thumbGroup.attr("transform", "translate("+[0, find_y_given_x($this.cell.dx)+23/2]+")")

        $this.setValue(table.slider.value);
        table.changeDay(Math.floor($this.curve_scale_x.invert($this.cell.dx)));


/*

            var newVal = Math.round($this.cell.value+$this.slider_scale_inverse($this.cell.dx));

            console.log($this.cell.value,$this.cell.dx,newVal)
            
            // Set value for the specific cell

            // Retrieve the current time value
            $this.setValue(table.slider.value);
            console.log($this, $this.cell)
            
            d3.selectAll(".slider-axis-thmb").attr("transform", "translate("+[-$this.cell.dx, 0]+")")
      
//            widgets.setValue($this.cell.dx);

            // Translate the slider to have the focus centered


            if(newVal != $this.cell.value && newVal <= $this.max && newVal >= $this.min){
                $this.cell.value = newVal;
                $this.value = $this.cell.value;
                var newPos = $this.axis_scale($this.cell.value);
                $this.cell.dx = mouseX - newPos;
                $this.thumbGroup.attr("transform", "translate("+[newPos, 0]+")");

                $this.fireEvent("dragged");
            }
            */
        });
};





DragCurve.prototype.remove = function(){
    this.sliderGroup.remove();
};

DragCurve.prototype.endDrag = function(callback){
  this.remove();
  d3.select("body").style("cursor", "default")

  console.log("endDrag dragcurve TODO")
  if(callback)callback.call(newVal);
};

DragCurve.prototype.addListener = function(listener){
    if(this.listeners.indexOf(listener) == -1) this.listeners.push(listener);
};

DragCurve.prototype.fireEvent = function(event){
    var $this = this;
    this.listeners.forEach(function(listener){
        listener.sliderChanged(event, $this.value);
    });
};

DragCurve.prototype.setValue = function(value){
    var $this = this;
    if(value != this.value){
        this.sliderGroup.select(".slider-thumb")
            .attr("transform", function(d){
                d.value = $this.value = value;
                return "translate("+[$this.axis_scale(d.value), 0]+")";
            });
    }
};