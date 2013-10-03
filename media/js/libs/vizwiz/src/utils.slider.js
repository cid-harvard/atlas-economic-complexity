function Slider() {
  
  var callback,
      handle_value,
      max_width,
      title = ""
      
  function util(selection) {
    
    selection.each(function(data) {
      
      handles = []
      var dragging = false,
          hover = false,
          current_hand = 0,
          // handles = [],
          parent = this,
          tick_size = 4 * d3.max(data,function(d){ return d.toString().length }) + 20, // NEW 4 instead of 3
          width = (tick_size*(data.length)+1),
          height = 23,
          playing = false,
          play_function;

      if (handle_value instanceof Array) var currentWidth = tick_size*2
      else var currentWidth = tick_size
      
      if(width>max_width){
        width = max_width
      }
      // Remove any previous content inside of DIV
      d3.select(this).selectAll('div').remove()
      
      d3.select(this).append("div")
        .attr("class","slider_label")
        .html(title)
      
      var background = d3.select(this).append("div")
        .attr("class","background")
        .style("width",width+"px")
        .style("height",height+"px")
        .style("margin-left","35px")
    
      if (handle_value instanceof Array) {
        var ranger = background.append("div")
          .attr("class","ranger")
          .style("height",height+"px")
      }

      d3.select(this).append("div")
        .attr("class","handle")
        .attr("id","play_button")
        // .style("position","relative")
        .style("width", height+"px")
        // .style("height", height+"px")
        // .style("margin-top","30px")
        // .style("margin-left","223px")
        // .style("margin-right","223px")
        // .text(">")
        .on(vizwhiz.evt.click, function(){
          if (!playing) {
            playing = true;
            d3.select("#play_button i").attr("class","glyphicon glyphicon-pause")
            // d3.select("#play_button").text("||")
            if (handles[0].index == data.length-1) var i = 0;
            else var i = handles[0].index+1;
            set_slider(i);
            i++;
            var play_interval = function() {
              if (i < data.length) {
                set_slider(i);
                i++;
                if (i == data.length) {
                  d3.select("#play_button i").attr("class","glyphicon glyphicon-play")
                  // d3.select("#play_button").text(">")
                  clearInterval(play_function);
                }
              }
            }
            play_function = setInterval(play_interval,2000);
          } else {
            clearInterval(play_function);
            playing = false;
            d3.select("#play_button i").attr("class","glyphicon glyphicon-play");
            // d3.select("#play_button").text(">")
          }
          
        })
        .append("i").attr("class","glyphicon glyphicon-play")
      /////
      // Create the tickmarks for the slider
      ////
      var positions = []

      if (data.length > 20){
        showing = Math.ceil(data.length / 20);
        
        data.forEach(function(value,index){
          switch (showing) {
            case 1: t = (100/(data.length))*(index)
                    break;
            case 2: t = (98/(data.length))*(index)
                    break;
            default: t = (96.5/(data.length))*(index)         
                    break;
          } 
          // console.log(value)  
          if (index%showing==0)
          {
            var tick = background.append("div")
              .attr("class","tick")
              .style("width",tick_size+"px")
              .style("left",t+"%")
              .style("right","0px")
              .text(value)
              .on(vizwhiz.evt.click,function(e){
                set_slider(index);
              })
          
            positions.push(t)  
          }
          else
          {
          var tick = background.append("div")
            .attr("class","tick")
            .style("width",tick_size+"px")
            .style("left",t-1+"%")
            .style("right","0px")
            // .text("·")
            .on(vizwhiz.evt.click,function(e){
              set_slider(index);
            })
            
          {
            switch (showing) {
              case 1: tick.style("left",t+"%")
                          .text("·")
                      break;
              case 2: tick.style("left",t+"%")
                          .text("·")  
                      break;
              default: tick.style("left",t-1+"%")
                       if (index%showing==2 )
                       {
                       tick.text("·");  
                       }
                      break;
            }            }
   
          
          positions.push(t)
          }
         
        })
        
      }
      else
      {
      data.forEach(function(value,index) {
        
        var t = (100/(data.length))*(index)
        
        var tick = background.append("div")
          .attr("class","tick")
          .style("width",tick_size+"px")
          .style("left",t+"%")
          .style("right","0px")
          .text(value)
          .on(vizwhiz.evt.click,function(e){
            set_slider(index);
          })
          
        positions.push(t)
      
      })
     }
    
      var handle = background.append("div")
        .attr("class","handle")
        .style("width",tick_size+"px")
        .style("right","0px")
  
      if (handle_value instanceof Array) {
    
        var handle0 = background.append("div")
          .attr("class","handle")
          .style("width",tick_size+"px")
          .style("right","0px")
    
        handles.push({'index': data.indexOf(handle_value[0]), 'handle': handle0})
        handles.push({'index': data.indexOf(handle_value[1]), 'handle': handle})
        
        handle
          .style("left",positions[handles[1].index]+"%")
          .text(handle_value[1])
        
        handle0
          .style("left",positions[handles[0].index]+"%")
          .text(handle_value[0])
        
        ranger
          .style("left",positions[handles[0].index]+"%")
          .style("width",(positions[handles[1].index]-positions[handles[0].index])+"%")
      } 
      
      else {
        handles.push({'index': data.indexOf(handle_value), 'handle': handle})
        handle
          .style("left",positions[handles[0].index]+"%")
          .text(handle_value)
      }
  
      d3.select(document).on(vizwhiz.evt.up,function(e){
        dragging = false;
      })
  
      background.on(vizwhiz.evt.down,function(e){
        dragging = true;
      })
  
      document.addEventListener(vizwhiz.evt.move,function(e){
        if (dragging) {
          e.preventDefault()
          // CHECK THESE VARIABLES
          var pos = background.node().offsetLeft+parent.offsetLeft,
              top = e.pageX-pos-5,
              bottom = width
              
          // CHECK THESE VARIABLES
          var mouse = (top/bottom)*100
          var index = 0
          while(index < positions.length) {
            if(mouse > positions[index]) {
              if(mouse < positions[index+1]) {
                set_slider(index)
                break
              } else if (!positions[index+1]) {
                set_slider(index)
                break
              }
            } else {
              set_slider(index)
              break
            }
            index++
          }
        }
      })
  
      function set_slider(index) {
        if (handle_value instanceof Array) {
          if (Math.abs(handles[0].index-index) >= Math.abs(handles[1].index-index)) current_hand = 1
          else current_hand = 0
        }
        if (index != handles[current_hand].index) {
          handles[current_hand].index = index
          handles[current_hand].handle.style("left",positions[index]+"%")
          handles[current_hand].handle.html(data[index])
          if (handle_value instanceof Array) {
            var array = [data[handles[0].index],data[handles[1].index]]
            array.sort(function(a,b){return a-b})
            ranger.style("left",positions[data.indexOf(array[0])]+"%")
            ranger.style("width",(positions[data.indexOf(array[1])]-positions[data.indexOf(array[0])])+"%")
            window[callback](array);
          } else {
            window[callback](data[handles[current_hand].index]);
          }
        }
      }
      
    })
  }
  
  util.initial_value = function(value) {
    if (!arguments.length) return handle_value
    handle_value = value
    return util
  }
  
  util.positions = function(value) {
    if (!arguments.length) return handles
    return util
  }
  
  util.title = function(value) {
    if (!arguments.length) return title
    title = value
    return util
  }
  
  util.callback = function(value) {
    if (!arguments.length) return callback
    callback = value
    return util
  }
  
  util.max_width = function(value) {
    if (!arguments.length) return max_width
    max_width = value
    return util
  }
  
  return util
}