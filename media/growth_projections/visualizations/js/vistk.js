(function(){function n(n,a,r){for(var e,s,o,m=-1,u=2*Math.PI/a,b=0,h=[];++m<a;)e=n.m*(m*u-Math.PI)/4,e=Math.pow(Math.abs(Math.pow(Math.abs(Math.cos(e)/n.a),n.n2)+Math.pow(Math.abs(Math.sin(e)/n.b),n.n3)),-1/n.n1),e>b&&(b=e),h.push(e);for(b=r*Math.SQRT1_2/b,m=-1;++m<a;)s=(e=h[m]*b)*Math.cos(m*u),o=e*Math.sin(m*u),h[m]=[Math.abs(s)<1e-6?0:s,Math.abs(o)<1e-6?0:o];return t(h)+"Z"}var a=d3.svg.symbol(),t=d3.svg.line();d3.superformula=function(){function t(a,t){var u,b=r[e.call(this,a,t)];for(u in m)b[u]=m[u].call(this,a,t);return n(b,o.call(this,a,t),Math.sqrt(s.call(this,a,t)))}var e=a.type(),s=a.size(),o=s,m={};return t.type=function(n){return arguments.length?(e=d3.functor(n),t):e},t.param=function(n,a){return arguments.length<2?m[n]:(m[n]=d3.functor(a),t)},t.size=function(n){return arguments.length?(s=d3.functor(n),t):s},t.segments=function(n){return arguments.length?(o=d3.functor(n),t):o},t};var r={asterisk:{m:12,n1:.3,n2:0,n3:10,a:1,b:1},bean:{m:2,n1:1,n2:4,n3:8,a:1,b:1},butterfly:{m:3,n1:1,n2:6,n3:2,a:.6,b:1},circle:{m:4,n1:2,n2:2,n3:2,a:1,b:1},clover:{m:6,n1:.3,n2:0,n3:10,a:1,b:1},cloverFour:{m:8,n1:10,n2:-1,n3:-8,a:1,b:1},cross:{m:8,n1:1.3,n2:.01,n3:8,a:1,b:1},diamond:{m:4,n1:1,n2:1,n3:1,a:1,b:1},drop:{m:1,n1:.5,n2:.5,n3:.5,a:1,b:1},ellipse:{m:4,n1:2,n2:2,n3:2,a:9,b:6},gear:{m:19,n1:100,n2:50,n3:50,a:1,b:1},heart:{m:1,n1:.8,n2:1,n3:-8,a:1,b:.18},heptagon:{m:7,n1:1e3,n2:400,n3:400,a:1,b:1},hexagon:{m:6,n1:1e3,n2:400,n3:400,a:1,b:1},malteseCross:{m:8,n1:.9,n2:.1,n3:100,a:1,b:1},pentagon:{m:5,n1:1e3,n2:600,n3:600,a:1,b:1},rectangle:{m:4,n1:100,n2:100,n3:100,a:2,b:1},roundedStar:{m:5,n1:2,n2:7,n3:7,a:1,b:1},square:{m:4,n1:100,n2:100,n3:100,a:1,b:1},star:{m:5,n1:30,n2:100,n3:100,a:1,b:1},triangle:{m:3,n1:100,n2:200,n3:200,a:1,b:1}};d3.superformulaTypes=d3.keys(r)})();
"use strict";

var w = typeof window === "undefined" ? this : window;

var vistk = w.vistk || {};
w.vistk = vistk;

vistk.version = "{{ VERSION }}";
vistk.utils = {};

vistk.viz = function() {

// Init parameters for the current chart
var vars = {};

// Private functions
var utils ={};

  // LIST OF PRIVATE UTILS FUNCTIONS

  // Create SVG groups for items marks
  utils.items_group = function(d, i) {

    d3.select(this).classed("highlighted", function(d, i) { return d.__highlighted; })
                    .classed("selected", function(d, i) { return d.__selected; })
                    .classed("mark__group", true)
                    .on("mouseover",function(d) {
                      vars.evt.call("highlightOn", d);
                    })
                    .on("mouseleave", function(d) {
                      vars.evt.call("highlightOut", d);
                    })
                    .on("click", function(d) {
                       vars.evt.call("selection", d);
                       d3.event.stopPropagation();
                    });

  }

  // Binds events for items marks
  utils.bind_events = function(d, i) {

    d3.select(this).classed("highlighted", function(d, i) { return d.__highlighted; })
                   .classed("selected", function(d, i) { return d.__selected; })
                   .on("mouseover",function(d) {
                     vars.evt.call("highlightOn", d);
                   })
                   .on("mouseleave", function(d) {
                     vars.evt.call("highlightOut", d);
                   })
                   .on("click", function(d) {
                      vars.evt.call("selection", d);
                      d3.event.stopPropagation();
                   });

  }

  // Create SVG groups for connect marks
  utils.connect_group = function(d, i) {

    d3.select(this).attr("class", "connect__group connect__group_" + d.__index)
                    .classed("highlighted", function(d, i) { return d.__highlighted; })
                    .classed("selected", function(d, i) { return d.__selected; })
                    .on("mouseover",function(d) {
                      if(vars.type !== "productspace") {
                        vars.evt.call("highlightOn", d);
                      }
                    })
                    .on("mouseleave", function(d) {
                      if(vars.type !== "productspace") {
                        vars.evt.call("highlightOut", d);
                      }
                    })
                    .on("click", function(d) {
                      if(vars.type !== "productspace") {
                        vars.evt.call("selection", d);
                      }
                    });

  }

  //  Main function to draw marks
  //  Invoked from a .each() call passing in the current datum d and index i,
  //  with the this context of the current DOM element
  //
  //  params contains the parameters for the current graphical mark to draw
  //  e.g. scales, type of mark, radius, color function, ..
  utils.draw_mark = function(selection, params, vars) {

    if(vars.dev) {
      console.log("[utils.draw_mark]", params.type)
    }

    selection.each(function(d, i) {

      // Skip the drawing if __redraw flag is false
      if(!d.__redraw) {
        return;
      }

      // Default id for marks
      var mark_id = params._mark_id + "_" + i;

      // params_type is the list of marks to be drawn
      // it is either static (string) or can be computer
      // from the params.var_mark
      // in both case it will result int an array of marks

      var var_mark = [];

      // In case a function determines the type of mark to be used
      if(typeof params.var_mark === "object") {

        params.var_mark.forEach(function(var_mark) {

          var params_type = "";

          if(typeof params.type === "function") {
            params_type = params.type(d[var_mark]);
          } else {
            params_type = params.type;
          }

          if(typeof params_type !== "undefined") {
            var_mark = var_mark.concat(params_type)
          }

        })

      } else {

        var params_type = "";

        if(typeof params.type === "function") {
          params_type = params.type(d[params.var_mark]);
        } else {
          params_type = params.type;
        }

        var_mark.push(params_type);

      }

      var params_text = "";

      if(typeof params.text !== "undefined") {
        if(typeof params.text === "function") {
          params_text = params.text(d, i , vars);
        } else if(typeof params.text === "string") {
          params_text = params.text;
        }
      } else if(vars.var_text !== "undefined") {
        params_text = d[vars.var_text];
      }

      var params_source = [0, 0];
      var params_target = [vars.width, vars.height];
      var params_translate = [0, 0];

      if(typeof params.translate !== "undefined" && params.translate !== null) {
        if(typeof params.translate === "function") {
          params_translate = params.translate(d, i, vars);
        } else {
          params_translate = params.translate;
        }
      }
      var params_x = utils.init_params("x", 0, params, d, i, vars);
      var params_y = utils.init_params("y", 0, params, d, i, vars);

      var default_height = params_type === 'div' || params_type === 'divtext' ? "auto": 10;
      var params_height = utils.init_params("height", default_height, params, d, i, vars);

      var params_width = utils.init_params("width", 10, params, d, i, vars);
      var params_rotate = utils.init_params("rotate", 0, params, d, i, vars);
      var params_scale = utils.init_params("scale", 1, params, d, i, vars);
      var params_fill = utils.init_params("fill", null, params, d, i, vars);

      var params_stroke = utils.init_params("stroke", null, params, d, i, vars);
      var params_stroke_width = utils.init_params("stroke_width", null, params, d, i, vars);
      var params_stroke_opacity = utils.init_params("stroke_opacity", null, params, d, i, vars);

      var params_offset_x = utils.init_params("offset_x", 0, params, d, i, vars);
      var params_offset_y = utils.init_params("offset_y", 0, params, d, i, vars);

      // Use the default accessor
      var accessor_data = vars.accessor_data;

      var that = this;

      var_mark.forEach(function(params_type) {

      switch(params_type) {

        case "text":

          if(typeof params.text_anchor === "undefined") {
            params.text_anchor = "start";
          }

          var items_mark_text = d3.select(that).selectAll(".items__mark__text.items_" + mark_id).data([d]);

          items_mark_text.enter().append("text")
              .classed("items__mark__text", true)
              .classed("items_" + mark_id, true)
              .style("text-anchor", params.text_anchor)
              .style("fill", params_fill)
              .attr("x", params_x)
              .attr("y", params_y)
              .attr("dy", ".35em")
              .attr("transform", "translate(" + ([params_translate[0] + params_offset_x, params_translate[1] + params_offset_y]) + ")rotate(" +  params_rotate + ")")
              .on("mouseover",function(d) { // FIX to prevent hovers
                if(typeof vars.evt !== 'undefined' && vars.evt == 'none') {
                  d3.event.stopPropagation();
                }
              })
              .on("mouseleave", function(d) {
                if(typeof vars.evt !== 'undefined' && vars.evt == 'none') {
                  d3.event.stopPropagation();
                }
              })
              .on("click", function(d) {
                if(typeof vars.evt !== 'undefined' && vars.evt == 'none') {
                  d3.event.stopPropagation();
                }
              });

          items_mark_text
              .classed("highlighted", function(d, i) { return d.__highlighted; })
              .classed("selected", function(d, i) { return d.__selected; })
              .transition().duration(vars.duration)
              .style("fill", params_fill)
              .style("stroke", params_stroke)
              .attr("transform", "translate(" + ([params_translate[0] + params_offset_x, params_translate[1] + params_offset_y]) + ")rotate(" +  params_rotate + ")")
              .text(function(d) {

                if(typeof params.text !== "undefined") {
                  return params.text(d);
                } else {
                  return vars.accessor_data(d)[vars.var_text];
                }

              });

        items_mark_text.exit().remove();

        break;

        // Attach a div to the SVG container
        case "div":

          var items_mark_div = d3.select(d3.select(vars.svg.node().parentNode).node().parentNode)
                .selectAll(".items__mark__div.items_" + mark_id).data([d]);

          var items_mark_div_enter = items_mark_div.enter()
               .append("div")
                 .classed("items__mark__div", true)
                 .classed("items_" + mark_id, true)
                 .style("position", "absolute")
                 .style("text-overflow", "ellipsis")
                 .style("overflow", "hidden");

          items_mark_div
                 .style("width", function(d) {
                   if(typeof params_width !== "undefined" && params_width !== 'auto') {
                     return params_width + "px";
                   } else {
                     return "auto";
                   }
                 })
                 .style("height", function(d) {

                   if(typeof params_height !== "undefined" && params_height !== 'auto') {
                     return params_height + "px";
                   } else {
                     return "auto";
                   }
                 })
                 .style("left", function(d) {
                   if(typeof params_x !== "undefined") {
                     return (params_x + params_translate[0]) + "px";
                   } else {
                     return (vars.x_scale[0]["func"](vars.accessor_data(d)[vars.var_x]) + params_translate[0]) + "px";
                   }
                 })
                 .style("top", function(d) {
                   if(typeof params_y !== "undefined") {
                     return (params_y + params_translate[1]) + "px";
                   } else {
                     return (vars.y_scale[0]["func"](vars.accessor_data(d)[vars.var_y]) + params_translate[1]) + "px";
                   }
                 })
                 .html(params_text);

          if(typeof params.class !== "undefined") {
            items_mark_div_enter.classed(params.class(vars.accessor_items(d)), true);
          }

          items_mark_div.exit().remove();

        break;

        case "divtext":

          var items_mark_divtext = d3.select(that).selectAll(".items__mark__divtext").data([d]);

          var items_mark_divtext_enter = items_mark_divtext.enter().insert("foreignObject")
                .style("pointer-events", "none")
                .classed("items__mark__divtext", true)
                .classed("items_" + mark_id, true)
                .attr("width", function(d) {
                   if(typeof d.dx !== "undefined") {
                     return (Math.max(0, d.dx - 2 * vars.padding - params_translate[0])) + "px";
                   } else {
                     return "auto";
                   }
                 })
                .attr("height", function(d) {
                 if(typeof d.dy !== "undefined") {
                    return (Math.max(0, d.dy - 2 * vars.padding - params_translate[1])) + "px";
                  } else {
                    return "auto";
                  }
                })
               .append("xhtml:body")
               .append("div")
               .style("pointer-events", "none")
               .style("width", function(d) {
                 if(typeof d.dx !== "undefined") {
                   return (Math.max(0, d.dx - 2 * vars.padding - params_translate[0])) + "px";
                 } else {
                   return "auto";
                 }
                })
               .style("height", function(d) {
                 if(typeof d.dy !== "undefined") {
                   return (Math.max(0, d.dy - 2 * vars.padding - params_translate[1])) + "px";
                 }
                })
              .style("margin-left", function(d) {
                 return params_translate[0] + 'px';
               })
              .style("margin-top", function(d) {
                 return params_translate[1] + 'px';
               })
               .style({"text-overflow": "ellipsis", "overflow": "hidden"})
               .html(params_text);

          items_mark_divtext.select('div')
              .transition().duration(vars.duration)
              .style({"pointer-events": "none"})
              .style("margin-left", function(d) {
                 return params_translate[0] + 'px';
               })
              .style("margin-top", function(d) {
                 return params_translate[1] + 'px';
               })
              .style("width", function(d) {
                if(typeof d.dx !== "undefined") {
                  return (Math.max(0, d.dx - 2 * vars.padding - params_translate[0])) + "px";
                } else {
                  return "auto";
                }
               })
              .style("height", function(d) {
                if(typeof d.dy !== "undefined") {
                  return (Math.max(0, d.dy - 2 * vars.padding - params_translate[1])) + "px";
                }
               })

          if(typeof params.class !== "undefined") {

            items_mark_divtext_enter.classed(params.class(vars.accessor_items(d)), true);

          }

          items_mark_divtext.exit().remove();

        break;


        case "image":

          var items_mark_image = d3.select(that).selectAll(".items__mark__image").data([d]);

          items_mark_image.enter().append("image")
                 .classed("items__mark__image", true)
                 .classed("items_" + mark_id, true)
                 .attr("xlink:href", params.href)
                 .attr("x", 0)
                 .attr("y", 0)
                 .attr("width", 60)
                 .attr("height", 30);

          items_mark_image.exit().remove();

        break;

      case "rect":

        var items_mark_rect = d3.select(that).selectAll(".items__mark__rect.items_" + mark_id).data([d]);

        items_mark_rect.enter().append("rect")
                  .classed("items__mark__rect", true)
                  .classed("items_" + mark_id, true)
                  .attr("x", params.x || 0)
                  .attr("y", params.y || 0)
                  .attr("height", params_height)
                  .attr("width", params_width)
                  .attr("transform", "rotate(" + params_rotate + ")")
                  .style("stroke", params_stroke);

        items_mark_rect
            .classed("highlighted", function(d, i) { return d.__highlighted; })
            .classed("selected", function(d, i) { return d.__selected; })
            .transition().duration(vars.duration)
            .attr("x", params.x || 0)
            .attr("y", params.y || 0)
            .attr("height", params_height)
            .attr("width", params_width)
            .style("stroke", params_stroke);

          if(typeof params.fill !== "undefined") {

            if(typeof params.fill === "function") {

              items_mark_rect.style("fill", params.fill(d, i, vars));

            } else {

              items_mark_rect.style("fill", function(d) {
                return params.fill(vars.accessor_items(d)[vars.var_color]);
              });

            }

          } else if(vars.var_color !== null) {

            items_mark_rect.style("fill", function(d) {
              return vars.color(vars.accessor_items(d)[vars.var_color]);
            });

            items_mark_rect.style("fill", function(d) {
              return vars.color(vars.accessor_items(d)[vars.var_color]);
            });

          }

        items_mark_rect.exit().remove();

        break;

      case "diamond":

        var items_mark_diamond = d3.select(that).selectAll(".items__mark__diamond.items_" + mark_id).data([d]);

        var items_mark_diamond_enter = items_mark_diamond.enter().append("rect")
            .classed("items__mark__diamond", true)
            .classed("items_" + mark_id, true)
            .attr("height", vars.mark.height)
            .attr("width", vars.mark.width)
            .attr("x", -vars.mark.width/2)
            .attr("y", -vars.mark.height/2)
            .attr("transform", "rotate(" + (params_rotate + 45) + ")")

            if(params_fill !== null) {
              items_mark_diamond_enter.style("fill", params_fill)
            }

           // .style("stroke", params_stroke);

          if(typeof params.class !== "undefined") {
            items_mark_diamond_enter.classed(params.class(vars.accessor_items(d)), true);
          }

        items_mark_diamond
            .classed("highlighted", function(d, i) { return d.__highlighted; })
            .classed("selected", function(d, i) { return d.__selected; })
            .transition().duration(vars.duration)
         //   .style("fill", params_fill)
         //   .style("stroke", params_stroke);

        items_mark_diamond.exit().remove();

        break;

        case "tick":

          var items_mark_tick = d3.select(that).selectAll(".items__mark__tick.items_" + mark_id).data([d]);

          items_mark_tick.enter().append('line')
              .classed('items__mark__tick', true)
              .classed("items_" + mark_id, true)
              .style("stroke", params.stroke(d[vars.var_color]))
              .style("stroke-width", params_stroke_width)
              .style("stroke-opacity", params_stroke_opacity)
              .attr("y2", function(d) { return -20; })
              .attr("transform", "translate(" +  params_translate + ")rotate(" + params_rotate + ")scale(" + params_scale + ")");

          if(typeof params.class !== "undefined") {
            items_mark_tick.classed(params.class(vars.accessor_items(d)), true);
          }

          items_mark_tick
              .classed("highlighted", function(d, i) { return d.__highlighted; })
              .classed("selected", function(d, i) { return d.__selected; })
              .transition().duration(vars.duration)
              .attr("transform", "translate(" +  params_translate + ")rotate(" + params_rotate + ")scale(" + params_scale + ")")  ;

          items_mark_tick.exit().remove();

        break;

        case "shape":

          var items_mark_shape = d3.select(that).selectAll(".items__mark__shape.items_" + mark_id).data([d]);

          items_mark_shape.enter().insert("path")
              .classed('items__mark__shape', true)
              .classed("items_" + mark_id, true)
              .attr("transform", function(d) {
                return "translate("+ -d.x +", "+ -d.y +")";
              })

          items_mark_shape
              .classed("highlighted", function(d, i) { return d.__highlighted; })
              .classed("selected", function(d, i) { return d.__selected; })
              .attr("d", vars.path)
              .style("fill", function(d, i) {
                return params.fill(vars.accessor_data(d)[vars.var_color]);
              })
              .attr("transform", function(d) {
                return "translate("+ -d.x +", "+ -d.y +")";
              })

            items_mark_shape.exit().remove();

          break;

        case "arc":

          var arc = d3.svg.arc().outerRadius(function(d) {

            if(typeof vars.var_r === "undefined") {
              return vars.radius_max*20;
            } else {

              var r_scale = d3.scale.linear()
                .range([vars.radius_min, vars.radius_max*20])
                .domain(d3.extent(vars.new_data, function(d) { return vars.accessor_data(d)[vars.var_r]; }))

              return r_scale(vars.accessor_data(d)[vars.var_r]);
            }

          }).innerRadius(0);

          var mark = d3.select(that).selectAll(".items__mark__arc").data([d]);

          mark.enter().append("path")
              .classed("items_" + mark_id, true)
              .classed("items__mark__arc", true)
              .attr("fill", params_fill)
              //.style("fill-opacity", function(d, i) {
              //  if(d.i == 0)
              //    return .2;
              //  else
              //    return 1;
              //});

          mark
              .classed("highlighted", function(d, i) { return d.__highlighted; })
              .classed("selected", function(d, i) { return d.__selected; })
              .transition().duration(vars.duration)
              .attr("fill", params_fill)
              .attr("d", arc);

        break;

        case "line":

          var mark = d3.select(that).selectAll(".connect__line").data([d]);

          // Make sure we have data for links
          if(typeof d.source == "undefined"  || typeof d.target == "undefined") {
            if(vars.dev) {
              console.log("[draw line] missing source or target")
            }
            return;
          }

          mark.enter().append('line')
              .classed('connect__line', true)
              .classed("items_" + mark_id, true)
              .attr("x1", function(d) { return vars.x_scale[0]["func"](d.source.x); })
              .attr("y1", function(d) { return vars.y_scale[0]["func"](d.source.y); })
              .attr("x2", function(d) { return vars.x_scale[0]["func"](d.target.x); })
              .attr("y2", function(d) { return vars.y_scale[0]["func"](d.target.y); })
              .style("stroke", params_stroke)
              .style("stroke-dasharray", ("3, 3"))
              .on("mouseover",function(d) { // FIX to prevent hovers
                d3.event.stopPropagation();
              })
              .on("mouseleave", function(d) {
                d3.event.stopPropagation();
              })
              .on("click", function(d) {
                 d3.event.stopPropagation();
              });

          mark
              .classed("highlighted", function(d, i) { return d.__highlighted; })
              .classed("highlighted__adjacent", function(d, i) { return d.__highlighted__adjacent; })
              .classed("selected", function(d, i) { return d.__selected; })
              .classed("selected__adjacent", function(d, i) { return d.__selected__adjacent; })

          break;

        case "line_horizontal":

          var mark = d3.select(that).selectAll(".mark__line_horizontal.items_" + mark_id).data([d]);

          var t = d3.transform(d3.select(that).attr("transform")).translate;

          mark.enter().append('line')
              .classed('mark__line_horizontal', true)
              .classed("items_" + mark_id, true)
              .on("mouseover",function(d) { // FIX to prevent hovers
                d3.event.stopPropagation();
              })
              .on("mouseleave", function(d) {
                d3.event.stopPropagation();
              })
              .on("click", function(d) {
                 d3.event.stopPropagation();
              });

          mark
              .classed("highlighted", function(d, i) { return d.__highlighted; })
              .classed("selected", function(d, i) { return d.__selected; })
              .attr("x1", function(d) { return -t[0] + vars.margin.left; })
              .attr("y1", function(d) { return params_offset_y; })
              .attr("x2", function(d) { return vars.x_scale[0]["func"].range()[1] -100; })
              .attr("y2", function(d) { return params_offset_y; });

          break;

        case "line_coord":

          var mark = d3.select(that).selectAll(".mark__line_coord").data([d]);

          var t = d3.transform(d3.select(that).attr("transform")).translate;

          mark.enter().append('line')
              .classed('mark__line_coord', true)
              .classed("items_" + mark_id, true)
              .on("mouseover",function(d) { // FIX to prevent hovers
                d3.event.stopPropagation();
              })
              .on("mouseleave", function(d) {
                d3.event.stopPropagation();
              })
              .on("click", function(d) {
                 d3.event.stopPropagation();
              });

          mark
              .classed("highlighted", function(d, i) { return d.__highlighted; })
              .classed("selected", function(d, i) { return d.__selected; })
              .attr("x1", function(d) { return params_source[0]; })
              .attr("y1", function(d) { return params_target[0]; })
              .attr("x2", function(d) { return params_source[1]; })
              .attr("y2", function(d) { return params_target[1]; });

          break;

        case "path":

          var this_accessor_values = function(d) { return d.values; };

          if(vars.type == "radial") {
            this_accessor_values = function(d) { return d; };
          }

          if(typeof params['func'] == 'undefined') {
              params['func'] = d3.svg.line()
               .interpolate('linear')
               .x(function(d) { return vars.x_scale[0]["func"](d[vars.var_x]); })
               .y(function(d) { return vars.y_scale[0]["func"](d[vars.var_y]); });
          }

          var mark = d3.select(that).selectAll(".connect__path_" + mark_id).data([d]);

          mark.enter().append('path')
              .classed('connect__path', true)
              .classed('connect__path_' + mark_id, true)
              .classed("items_" + mark_id, true)
              .style("fill", params_fill)
              .style("stroke", params_stroke)
              .attr('d', function(e) {
                return params["func"](d3.values(this_accessor_values(e)));
              })
              .attr("transform", function(d) {
                return "translate(" +  params_translate + ")rotate(" +  params_rotate + ")";
              });



          mark
              .classed("highlighted", function(e, j) { return e.__highlighted; })
              .classed("selected", function(e, j) { return e.__selected; })
              .transition().duration(vars.duration)
              .style("stroke", params_stroke)
              .attr('d', function(e) {
                return params["func"](d3.values(this_accessor_values(e)));
              });

        break;

        case "star":

          var star = d3.superformula()
              .type("star")
              .size(10 * 50)
              .segments(360);

          var mark = d3.select(that).selectAll(".items__mark__star").data([d]);

          mark.enter().append('path')
              .classed("items_" + mark_id, true)
              .classed('items__mark__star', true)
              .attr('d', star);

          mark
              .classed("highlighted", function(d, i) { return d.__highlighted; })
              .classed("selected", function(d, i) { return d.__selected; });

          mark.exit().remove();

        break;

        case "polygon":

          var mark = d3.select(that).selectAll('.items__mark__polygon').data([d]);

          mark.enter().append('polygon')
              .classed("items_" + mark_id, true)
              .classed('items__mark__polygon', true)
              .attr('fill', '#ED4036')
              .attr('stroke-width', 0)
              .attr('points','4.569,2.637 0,5.276 -4.569,2.637 -4.569,-2.637 0,-5.276 4.569,-2.637');

          mark
              .classed('highlighted', function(d, i) { return d.__highlighted; })
              .classed('selected', function(d, i) { return d.__selected; });

          mark.exit().remove();

        break;

        case "triangle":

          var mark = d3.select(that).selectAll('.items__mark__triangle').data([d]);

          mark.enter().append('polygon')
              .classed("items_" + mark_id, true)
              .classed('items__mark__triangle', true)
              .attr('fill', params_fill)
              .attr('stroke-width', 0)
              .attr('points','-10,5 0,-15 10,5');

          mark
              .classed('highlighted', function(d, i) { return d.__highlighted; })
              .classed('selected', function(d, i) { return d.__selected; });

          mark.exit().remove();

        break;

        case "marker":

          var mark = d3.select(that).selectAll(".items__mark__marker").data([d]);

          var mark_enter = mark.enter().append('path')
              .classed("items_" + mark_id, true)
              .classed('items__mark__marker', true)
              .attr("fill", "#ED4036")
              .attr("stroke-width", 0)
              .attr('d', "M10,0L0,10l10,25.4L20,10L10,0z M10,14.6c-2.1,0-3.8-1.7-3.8-3.8c0-2.1,1.7-3.8,3.8-3.8 c2.1,0,3.8,1.7,3.8,3.8C13.8,12.9,12.1,14.6,10,14.6z");

          // IN CASE OF CUSTOM ENTER FOR ITEMS
          if(typeof params.enter !== "undefined") {
            mark_enter.call(params.enter, vars);
          }

          mark
              .classed("highlighted", function(d, i) { return d.__highlighted; })
              .classed("selected", function(d, i) { return d.__selected; });

          d3.select(that).selectAll(".items__mark__marker")
                          .transition()
                          .duration(vars.duration)
                          .ease('bounce')
                          .attr("transform", function(d, i) {
                            return "translate(-10, -40)";
                          });

          mark.exit().remove();

        break;

        case "none":

          // To make sure we removed __highlighted and __selected nodes
          d3.select(that).selectAll(".items_" + mark_id).remove();

        break;

        case "circle":
        default:

          var mark = d3.select(that).selectAll(".items__mark__circle.items_" + mark_id).data([d]);

          var mark_enter = mark.enter().append("circle")
              .classed("items_" + mark_id, true)
              .classed("items__mark__circle", true)
              .attr("cx", params_translate[0])
              .attr("cy", params_translate[1])
              .attr("r", function(d) {

                if(typeof vars.var_r === "undefined") {
                  if(typeof params.radius !== "undefined") {
                    return params.radius;
                  } else {
                    return vars.radius;
                  }
                } else {

                  var r_scale = d3.scale.sqrt()
                    .range([vars.radius_min, vars.radius_max])
                    .domain(d3.extent(vars.new_data, function(d) { return d[vars.var_r]; }))

                  return r_scale(d[vars.var_r]);
                }
              })
              .style("stroke", params_stroke)
              .style("stroke-width", params_stroke_width)
              .style("stroke-opacity", params_stroke_opacity);

          if(typeof params.fill !== "undefined") {

            if(typeof params.fill === "function") {

              mark.style("fill", params.fill(d, i, vars));

            } else {

              mark_enter.style("fill", function(d) {
                return params.fill(vars.accessor_items(d)[vars.var_color]);
              });

            }

          } else if(vars.var_color !== null) {

            mark_enter.style("fill", function(d) {
              return vars.color(vars.accessor_items(d)[vars.var_color]);
            });

            mark.style("fill", function(d) {
              return vars.color(vars.accessor_items(d)[vars.var_color]);
            });

          }

          if(typeof params.opacity !== "undefined") {

            if(typeof params.fill === "function") {

              mark_enter.style("opacity", function(d) {
                return params.opacity(vars.accessor_items(d));
              });

            } else {

              mark.style("opacity", params.opacity);

            }

          }

          if(typeof params.title !== "undefined") {
            mark_enter.append("title").text(function(d) {
              return params.title(vars.accessor_items(d));
            });
          }

          if(typeof params.class !== "undefined") {
            mark_enter.classed(params.class(vars.accessor_items(d)), true);
          }

          mark
              .classed("highlighted", function(d, i) { return d.__highlighted; })
              .classed("highlighted__adjacent", function(d, i) { return d.__highlighted__adjacent; })
              .classed("selected", function(d, i) { return d.__selected; })
              .classed("selected__adjacent", function(d, i) { return d.__selected__adjacent; })
              .attr("transform", "translate(" +  params_translate + ")rotate(" +  params_rotate + ")");

          mark.exit().remove();

          break;

        }

      });

    })

  }

  utils.make_zoomable_on_click = function() {

    this.on("click", clicked);

    // http://bl.ocks.org/mbostock/4699541
    function clicked(d) {
      if (active.node() === this) return reset();
      active.classed("active", false);
      active = d3.select(this).classed("active", true);

      // Retrieve parent's node position
      var t = d3.transform(d3.select(this.parentNode).attr("transform")).translate;

      var bounds = d3.select(this).node().getBBox(),
          dx = bounds.width,
          dy = bounds.height,
          x = bounds.x + dx/2 + t[0],
          y = bounds.y + dy/2 + t[1];

          scale = .1 / Math.max(dx / vars.width, dy / vars.height),
          translate = [vars.width / 2 - scale * x, vars.height / 2 - scale * y];

      // Animate the graph
      vars.svg.transition()
          .duration(1750)
          .style("stroke-width", 1.5 / scale + "px")
          .attr("transform", "translate(" + translate + ")scale(" + scale + ")");
    }

    function reset() {
      active.classed("active", false);
      active = d3.select(null);

      vars.svg.transition()
          .duration(750)
          .style("stroke-width", "1.5px")
          .attr("transform", "");
    }

  }

  utils.zoom_to_nodes = function(nodes) {

    if(vars.dev) { console.log("[zooming to nodes]", vars.zoom); }

    if(nodes.length === 0) {
      // Resets scale and viewport to default values

      vars.scale = 1;
      vars.translate = [0, 0];
      vars.translate_x = 0;
      vars.translate_y = 0;

      vars.svg.transition()
              .duration(vars.duration)
              .attr("transform", "translate(" + vars.margin.left + "," + vars.margin.top + ")rotate(" + vars.rotate + ")");
      return;
    }

    var min_x = vars.width;
    var max_x = 0;
    var min_y = vars.height;
    var max_y = 0;

    // Calculate nodes BBOX
    nodes.forEach(function(node_id) {

       var n = vars.svg.selectAll(".items__mark__circle").filter(function(d) {
         return d[vars.var_id] == node_id;
       });

       if(typeof n === "undefined")
        return;

      // Retrieve parent's node position
      var t = d3.transform(d3.select(n.node().parentNode).attr("transform")).translate;

      var bounds = n.node().getBBox();

      min_x = Math.min(min_x, bounds.x + t[0]);
      max_x = Math.max(max_x, bounds.x + t[0]);

      min_y = Math.min(min_y, bounds.y + t[1]);
      max_y = Math.max(max_y, bounds.y + t[1]);

    })

    var width = (max_x - min_x) + 100;
    var height = (max_y - min_y) + 100;

    vars.translate_x = min_x + (max_x - min_x) / 2;
    vars.translate_y = min_y + (max_y - min_y) / 2;

    vars.scale = 1 / Math.max(width / vars.width, height / vars.height);
    vars.translate = [vars.width / 2 - vars.scale * vars.translate_x, vars.height / 2 - vars.scale * vars.translate_y];

    // Animate the graph
    vars.svg.transition()
        .duration(1750)
        .style("stroke-width", 1.5 / vars.scale + "px")
        .attr("transform", "translate(" + vars.translate + ")scale(" + vars.scale + ")");

    // If we want to re-scale the various elements
    // vars.svg.selectAll("circle").style("stroke-width", (1.5 / vars.scale) + "px")

    vars.svg.selectAll("text").style("font-size", (1 / vars.scale) + "rem")

  }

  utils.draw_chart = function(vars_svg, context, params) {

    if(context.dev) {
      console.log("[utils.draw_chart] drawing chart of type", context.type);
    }

    var vars = context;
    vars.new_data = params;

    if(vars.x_invert) {
      vars.x_scale[0]["func"].range([vars.x_scale[0]["func"].range()[1], vars.x_scale[0]["func"].range()[0]]);
    }

    if(vars.y_log) {
      vars.y_scale = [{
        func: d3.scale.log()
                .range([vars.height - vars.margin.top - vars.margin.bottom, vars.margin.top])
                .domain([1, d3.max(vars.new_data, function(d) { return d[vars.var_y]; })]).nice(),
      }];

    }

    if(typeof vars._user_vars.y_invert !== 'undefined' && vars._user_vars.y_invert) {
      vars.y_scale[0]["func"].range([vars.y_scale[0]["func"].range()[1], vars.y_scale[0]["func"].range()[0]]);
    }

    // In case items are programmatically generated
    if(typeof vars.items == "function") {
      vars.items = vars.items(vars);
    }

    if(typeof vars.items !== "undefined" && vars.items[0] !== "undefined" &&  Object.keys(vars.items).length > 0 && vars.type !== "stacked") {

        vars.items.forEach(function(item, index_item) {

            if(!vars.flat_scene) {

              // Use the global accessor, unless specif one has been set
              var accessor_data = vars.accessor_data;

              // In case of custom static accessor
              if(typeof item.accessor_data !== "undefined") {
                accessor_data = item.accessor_data;
              }

              // PRE-UPDATE ITEMS
              // Join is based on the curren_time value
              var gItems = vars_svg.selectAll(".mark__group" +  "_" + index_item)
                              .data(vars.new_data.filter(function(d) {
                                  return typeof accessor_data(d) !== 'undefined' && typeof accessor_data(d)[vars.var_id] !== 'undefined';
                                }), function(d, i) {
                                return accessor_data(d)[vars.var_id] + "_" + index_item + d.depth;
                              });

              // ENTER ITEMS
              var gItems_enter = gItems.enter()
                              .insert("g", ":first-child")
                              .attr('class', function(d) {
                                return "mark__group" +  "_" + index_item;
                              })

              // ITEMS EXIT
              var gItems_exit = gItems.exit();

              // IN CASE OF CUSTOM ENTER FOR ITEMS
              if(typeof item.enter !== "undefined") {
                gItems_enter.call(item.enter, vars);
              } else {
                gItems_enter.attr("transform", function(d, i) {
                  return "translate(" + vars.x_scale[0]["func"](accessor_data(d)[vars.var_x])
                    + ", " + vars.y_scale[0]["func"](accessor_data(d)[vars.var_y]) + ")";
                });
              }

              // IN CASE OF CUSTOM EVENTS FOR ITEMS
              if(vars.init && typeof item.evt !== "undefined") {

                item.evt.forEach(function(e) {
                  vars.evt.register(e.type, e.callback);
                })

              }

            }

           // APPEND AND UPDATE ITEMS MARK
            item.marks.forEach(function(params, index_mark) {

              if(!vars.flat_scene) {

                if(typeof params.filter === "undefined") {
                  params.filter = function() {
                    return true;
                  }
                }

                // Supporting multipe similar elements
                params._mark_id = index_item + "_" + index_mark;

                if(vars.init) {

                  gItems_enter
                      .filter(function(d, i) { return params.filter(d, i, vars); })
                      .filter(utils.filters.redraw_only)
                      .call(utils.draw_mark, params, vars);

                  // Bind events to groups after marks have been created
                  gItems_enter.each(utils.items_group);

                }

                gItems
                    .filter(params.filter)
                    .filter(utils.filters.redraw_only)
                    .call(utils.draw_mark, params, vars);


                // CUSTOM SELECTION EVENT
                if(vars.init && typeof params.evt !== 'undefined') {
                  vars.evt.register("selection", params.evt[0].func)
                }

              } else { // flat scene graph

                var mark_type = params.type;
                var index_mark = index_mark;

                //  Unique ID for the mark
                var mark_id = mark_type + "_" + index_item+ "_" + index_mark;

                // Get the marks params
                var mark_params = vars.default_marks[mark_type](vars);

                var items = vars.svg.selectAll(mark_type + "." + mark_id)
                    .data(vars.new_data, function(d, i) {
                      d.__mark_id = mark_id + '_' + i;
                      return d.__mark_id;
                    });

                // Z-index?
                // .insert("g", ":first-child");
                // Should we re-order the marks to make sure it will appear in right order?
                // Or do it afterwards?

                if(typeof params.filter == "undefined") {
                  params.filter = function() { return true; }
                }

                // Drawing SVG TYPE MARK
                items.enter()
                  .append(mark_type)
                    .filter(params.filter)
                    .filter(utils.filters.redraw_only)
                    .call(mark_params.enter, params, vars, mark_id);

                items
                  .filter(params.filter)
                  .filter(utils.filters.redraw_only)
                  .call(mark_params.update, params, vars, mark_id);

                items.exit()
                  .filter(params.filter)
                  .call(mark_params.exit, params, vars, mark_id);

                if(vars.init) {
                  vars.new_data.forEach(function(d) {
                    if(!d.__selected) { d.__redraw = false; }
                  });
                }


                // TODO: Drawing HTML TYPE MARKS

                // TODO: Drawing CANVAS TYPE MARKS

              }


            });

          if(!vars.flat_scene) {

            // IN CASE OF CUSTOM UPDATE FOR ITEMS
            if(typeof item.update !== "undefined") {
              vars_svg.selectAll(".mark__group" + "_" + index_item).call(item.update, vars)
            } else {
            // POST-UPDATE ITEMS GROUPS
              vars_svg.selectAll(".mark__group" + "_" + index_item)
                            .filter(utils.filters.redraw_only)
                            .transition()
                            .duration(vars.duration)
                            //.ease('none')
                            .attr("transform", function(d, i) {
                              return "translate(" + vars.x_scale[0]["func"](accessor_data(d)[vars.var_x]) + ", " + vars.y_scale[0]["func"](accessor_data(d)[vars.var_y]) + ")";
                            });
            }

            // IN CASE OF CUSTOM EXIT FOR ITEMS
            if(typeof item.exit !== "undefined") {
              gItems_exit.call(item.exit, vars)
            } else {

              gItems_exit.remove();
            }

            // Make sure we won't re-draw all nodes next time
      //      if(vars.type == "productspace" || vars.type == "treemap" || vars.type == "scatterplot" || vars.type == "geomap") {
            if(vars.init && vars.type !== 'linechart' && vars.type !== 'slopegraph' && vars.type !== 'slopegraph_ordinal') {
              vars.new_data.forEach(function(d) {
                if(!d.__selected) { d.__redraw = false; }
              });
            }

          }

        });

    }

    if(typeof vars.connect !== "undefined" && typeof vars.connect[0] !== "undefined" && Object.keys(vars.connect).length > 0) {

      // 1/ Between different items at a given time for one dimension
      // 2/ Between same items at a given time points
      // 2/ Between same items at multiple given times

      // By default, connecting time points
      var connect_data = vars.new_data;

      // Connecting items
      if(vars.type == "productspace" || vars.type == "radial") {

        // Assign a var_id value for each link (for join)
        if(vars.init) {
          vars.links.forEach(function(d, i) {
            d[vars.var_id] = i;
          });
        }

        connect_data = vars.links;

      }

      // APPEND AND UPDATE CONNECT MARK
      vars.connect.forEach(function(connect, index_item) {

        // Use the global accessor, unless specif one has been set
        var accessor_data = vars.accessor_data;

        if(typeof connect.accessor_data !== "undefined") {
          accessor_data = connect.accessor_data;
        }

        // PRE-UPDATE CONNECT
        // TOOD: find a common join to al types of connections

        var gConnect = vars_svg.selectAll(".connect__group")
                        .data(connect_data, function(d, i) {
                          return d[vars.var_id] + "_" + d.__index;
                        });

        // ENTER CONNECT
        var gConnect_enter = gConnect.enter()
                        .insert("g", ":first-child")
                        .attr("class", "connect__group");

        connect.marks.forEach(function(params, index_mark) {

          if(typeof params.filter === "undefined") {
            params.filter = function() { return true; };
          }

          // Supporting multipe similar elements
          params._mark_id = index_item + "_" + index_mark;

          // Only create connections when char inits
          if(vars.init) {

            gConnect_enter
              .filter(params.filter)
              .filter(utils.filters.redraw_only)
              .call(utils.draw_mark, params, vars)

          }

          gConnect
            .filter(params.filter)
            .filter(utils.filters.redraw_only)
            .call(utils.draw_mark, params, vars);

        });

        if(vars.init) {
          // Bind events to groups after marks have been created
          gConnect.each(utils.connect_group);
        }

        // EXIT
        var gConnect_exit = gConnect.exit().remove();

        // Specific to the product space as the structure does not change
        if(vars.init && vars.type === "productspace") {
          connect_data.forEach(function(d) { d.__redraw = false; });
        }


      });

    } else {

      // Remove connect mark if not in config file anymore
      vars_svg.selectAll(".connect__group").remove();

    }

    if(typeof vars._user_vars.x_tickValues !== 'undefined') {
      vars.x_tickValues = vars._user_vars.x_tickValues;
    }

    // CREATE / UPDATE / REMOVE AXIS
    if(vars.x_axis_show) {
      context.svg.call(utils.x_axis);
    } else {
      context.svg.selectAll(".x.axis").remove();
    }

    if(vars.y_axis_show) {
      vars_svg.call(utils.y_axis);
    } else {
      vars_svg.selectAll(".y.axis").remove();
    }

    if(vars.x_grid_show) {

      vars_svg.selectAll(".x.grid").data([vars.new_data])
        .enter()
          .insert("g", ":first-child")
          .attr("class", "x grid")
          .style("display", function() {
            return vars.x_grid_show ? "block": "none";
          })
          .attr("transform", function() {
            if(vars.x_axis_orient == "top") {
              return "translate(0," + (vars.height - vars.margin.top - vars.margin.bottom) + ")";
            } else {
              return "translate(0," + (vars.margin.top) + ")";
            }
          });

      vars_svg.selectAll(".x.grid").transition()
          .duration(vars.duration)
          .call(utils.make_x_axis()
          .tickSize(vars.height - vars.margin.top - vars.margin.bottom, 0, 0)
          .tickFormat(""));

    }

    if(vars.y_grid_show) {

      vars_svg.selectAll(".y.grid").data([vars.new_data])
        .enter()
          .insert("g", ":first-child")
          .attr("class", "y grid")
          .style("display", function() { return vars.y_axis_show ? "block": "none"; })
          .attr("transform", "translate(" + vars.margin.left + ", 0)");

      vars_svg.selectAll(".y.grid").transition()
          .duration(vars.duration)
          .call(utils.make_y_axis()
          .tickSize(-vars.x_scale[0]["func"].range()[1] + vars.margin.right + vars.y_tickSize, 0, 0)
          .tickFormat(""));

    }

    if(typeof vars._user_vars.y_grid_show !== 'undefined' && !vars._user_vars.y_grid_show) {
      vars_svg.selectAll(".y.grid").remove();
    }

    if(vars.refresh) {
      utils.zoom_to_nodes(vars.zoom);
    }

    utils.background_label(vars.title);

    // Flag that prevent to re-wrangle data by default
    vars.refresh = false;
    vars.init = false;

  }

  utils.x_axis = function(d, i) {

    vars.x_axis = utils.make_x_axis();

    vars.svg.selectAll(".x.axis").data([vars.new_data])
      .enter()
        .insert("g", ":first-child")
        .attr("class", "x axis")
        .attr("transform", "translate(" + vars.x_axis_translate + ")")
      .append("text")
        .attr("class", "axis__label x__axis__label")
        .attr("x", vars.width-vars.margin.left-vars.margin.right)
        .attr("y", -6)
        .style({
          "text-anchor": "end",
          "display": function(d) {
            if(vars.x_text) {
              return "block";
            } else {
              return "none";
            }
          }
        })
        .text(function() {
          if(vars.x_text_custom !== "") {
            return vars.x_text_custom;
          } else {
            return vars.var_x;
          }
        });

    vars.svg.selectAll(".x.axis").transition()
        .duration(vars.duration)
        .style("display", function() { return vars.x_axis_show ? "block": "none"; })
        .call(vars.x_axis)
        .selectAll(".tick text")
        .style("text-anchor", function(d, i) {
          if(vars.x_ticks === 2) {
            if(i === 0) {
              return "start";
            } else {
              return "end";
            }
          } else {
            return "middle";
          }
        })

  }

  utils.y_axis = function(d, i) {

    vars.y_axis = utils.make_y_axis();

    vars.svg.selectAll(".y.axis").data([vars.new_data])
      .enter()
        .insert("g", ":first-child")
        .attr("class", "y axis")
        .attr("transform", "translate(" + vars.y_axis_translate + ")")
      .append("text")
        .attr("class", "axis__label x__axis__label")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style({
          "text-anchor": "end",
          "display": function(d) {
            return typeof vars.y_text !== "undefined" && vars.y_text !== null;
          }
        })
        .text(function() {
          if(vars.y_text_custom !== "") {
            return vars.y_text_custom;
          } else {
            return vars.var_y;
          }
        });

    vars.svg.selectAll(".y.axis").transition()
        .duration(vars.duration)
        .style("display", function() { return vars.y_axis_show ? "block": "none"; })
        .call(vars.y_axis);

  }

  utils.make_x_axis = function() {
    return d3.svg.axis()
        .scale(vars.x_scale[0]["func"])
        .ticks(vars.x_ticks)
        // Quick fix to get max value
        .tickValues(vars.x_tickValues)
        .tickFormat(vars.x_format)
        .tickSize(vars.x_tickSize)
        .tickPadding(vars.x_tickPadding)
        .orient(vars.x_axis_orient);
  }

  utils.make_y_axis = function() {
    return d3.svg.axis()
        .scale(vars.y_scale[0]["func"])
        .ticks(vars.y_ticks)
        // Quick fix to get max value
        .tickValues(vars.y_tickValues)
        .tickFormat(vars.y_format)
        .tickSize(vars.y_tickSize)
        .tickPadding(vars.y_tickPadding)
        .orient(vars.y_axis_orient);
  }

  // Title
  utils.background_label = function() {

    vars.svg.selectAll(".background_label")
        .data([vars.new_data])
      .enter()
        .insert("text")
        .attr("class", "background_label")
        .attr("text-anchor", "middle")
        .attr("y", 0)
        .attr("x", vars.width/2);

    vars.svg.selectAll(".background_label")
        .text(vars.title);

  }

  // One way to wrap text but creates too many elements
  // Alternative is to use the divtext graphical mark which wraps and ellipsis
  // http://bl.ocks.org/mbostock/7555321
  utils.wrap = function(node) {

    node.each(function() {

      if(typeof d3.select(this).data()[0].name == "undefined")
        return;

      var width = d3.select(this).data()[0].dx;

      var text = d3.select(this),
          words = d3.select(this).data()[0].name.split(/\s+/).reverse(),
          word,
          line = [],
          lineNumber = 0,
          lineHeight = 1.1, // ems
          y = text.attr("y"),
          dy = 0, //parseFloat(text.attr("dy")),
          tspan = text.text(null).append("tspan").attr("x", 0).attr("y", y).attr("dy", dy + "em");

      while (word = words.pop()) {
        line.push(word);
        tspan.text(line.join(" "));
        if (tspan.node().getComputedTextLength() > width) {
          line.pop();
          tspan.text(line.join(" "));
          line = [word];
          tspan = text.append("tspan").attr("x", 0).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
        }
      }
    });
  }

  utils.update_filters = function(value, add) {

    if(vars.dev) {
      console.log("[update_filters]", value);
    }

    // If we add a new value to filter
    if(add) {
      if(vars.filter.indexOf(value) < 0) {
        vars.filter.push(value)
      }
    } else {
      var index = vars.filter.indexOf(value)
      if(index > -1) {
        vars.filter.splice(index, 1);
      }
    }
  }

  // Moves a graphical mark along a SVG path
  utils.animate_trajectory = function(path, start_time, duration) {

    var totalLength = path.node().getTotalLength();

    path.attr("stroke-width", "5")
        .attr("stroke-dasharray", totalLength + " " + totalLength)
        .attr("stroke-dashoffset", totalLength)
      .transition()
        .duration(vars.duration)
        .ease("linear")
        .attr("stroke-dashoffset", 0);

  }

  utils.filters = {};

  utils.init_item = function(d) {
    d.__aggregated = false;
    d.__selected = false;
    d.__selected__adjacent = false;
    d.__highlighted = false;
    d.__highlighted__adjacent = false;
    d.__missing = false;
    d.__redraw = false;
  }

  utils.init_params = function(v, default_value, params, d, i, vars) {

    var result = default_value;

    if(typeof params[v] !== "undefined") {
      if(typeof params[v] === "function") {
        result = params[v](d, i, vars);
      } else if(typeof params[v] === "string") {
        result = params[v];
      } else if(typeof params[v] === "number") {
        result = params[v];
      } else {
        result = params[v];
      }
    }

    return result;

  }

  utils.filters.redraw_only = function(d) { return d.__redraw; }

  utils.find_adjacent_links = function(d, links) {

      return vars.links.filter(function(e) {
        if(typeof e.source !== 'undefined' && typeof e.target !== 'undefined') {
          return e.source[vars.var_id] === d[vars.var_id] || e.target[vars.var_id] === d[vars.var_id];
        } else {
          return false;
        }
      })
  }

  utils.find_adjacent_nodes = function(d, links) {

      return vars.links.filter(function(e) {
        if(typeof e.source !== 'undefined' && typeof e.target !== 'undefined') {
          return e.source[vars.var_id] === d[vars.var_id] || e.target[vars.var_id] === d[vars.var_id];
        } else {
          return false;
        }
      })
  }

  utils.create_hierarchy = function(vars) {

   // Create the root node
    vars.root = {};
    vars.root[vars.var_text]= "root";
    vars.root.depth = 0;

    vars.root[vars.var_size] = vars.new_data.map(function(d) {
      return d[vars.var_size];
    }).reduce(function(p, c) {
      return p + c;
    }, 0);

    vars.groups = [];

    vars.unique_groups = [];

    // Creates the groups here
    vars.new_data.map(function(d, i) {

      // If group doesn't exist, we create it
      if(vars.unique_groups.indexOf(d[vars.var_group]) < 0) {
        vars.unique_groups.push(d[vars.var_group]);
        vars.groups[vars.unique_groups.indexOf(d[vars.var_group])] = [];
      }

      var n = {year: d[vars.var_time], id: i};

      n[vars.var_size] = d[vars.var_size];
      n[vars.var_group] = d[vars.var_group];
      n[vars.var_id] = d[vars.var_id];
      n[vars.var_text] = d[vars.var_text];
      n[vars.var_color] = d[vars.var_color];
      n[vars.var_text_item] = d[vars.var_text_item];

      vars.groups[vars.unique_groups.indexOf(d[vars.var_group])].push(n);

    });

    // Make sure there is no empty elements
    vars.groups = vars.groups.filter(function(n) { return n !== "undefined"; });

    // Add group elements are root children
    vars.root.children = vars.groups.map(function(d, i) {

      node = {};

      if(typeof vars.var_text_parent !== 'undefined') {
        node[vars.var_text] = d[0][vars.var_text_parent];
      } else {
        node[vars.var_text] = d[0][vars.var_text];
      }

      node[vars.var_group] = d[0][vars.var_group];
      node[vars.var_id] = d[0][vars.var_group];
      node[vars.var_color] = d[0][vars.var_color];

      node[vars.var_sort] = 0;
      node[vars.var_size] = 0;

      // Create the children nodes var
      node.children = d.map(function(e, j) {

        var n = e;

        // For parent element
        node[vars.var_sort] += e[vars.var_sort];
        node[vars.var_size] += e[vars.var_size];

        return n;
      });

      return node;

    });

    if(typeof vars.var_sort_asc !== "undefined" && !vars.var_sort_asc) {
      vars.root.children = vars.root.children.sort(function(a, b) {
        return d3.ascending(a[vars.var_sort], b[vars.var_sort]);
      });
    } else {
      vars.root.children = vars.root.children.sort(function(a, b) {
        return d3.descending(a[vars.var_sort], b[vars.var_sort]);
      });
    }

  }

  utils.check_data_display = function() {
    if(vars.type === 'treemap') {
      return nb_values = vars.new_data.filter(function(d) {
        return d[vars.var_size] > 0;
      }).length > 0;
    } else {
      return vars.new_data.length > 0;
    }
  }

  // http://stackoverflow.com/questions/17500312/is-there-some-way-i-can-join-the-contents-of-two-javascript-arrays-much-like-i/17500836#17500836
  utils.join = function(lookupTable, mainTable, lookupKey, mainKey, select) {
      var l = lookupTable.length,
          m = mainTable.length,
          lookupIndex = [],
          output = [];
      for (var i = 0; i < l; i++) { // loop through l items
          var row = lookupTable[i];
          lookupIndex[row[lookupKey]] = row; // create an index for lookup table
      }
      for (var j = 0; j < m; j++) { // loop through m items
          var y = mainTable[j];
          var x = lookupIndex[y[mainKey]]; // get corresponding row from lookupTable
          var s = select(y, x);
          if(typeof s !== 'undefined')
            output.push(s); // select only the columns you need
      }
      return output;
  };

utils.init_params_values = function(var_v, default_value, params, d, i, vars) {

    var result = default_value;

    if(typeof params[var_v] !== "undefined") {
      if(typeof params[var_v] === "function") {
        result = params[var_v](d, i, vars);
      } else if(typeof params[var_v] === "string") {
        result = params[var_v];
      } else if(typeof params[var_v] === "number") {
        result = params[var_v];
      } else {
        result = params[var_v];
      }
    }

    return result;

  }

  // Turns parameters into actual values
  utils.mark_params = function(params, vars, d, i) {

    var mark_params = {};

    mark_params.text = "";

    if(typeof params.text !== "undefined") {
      if(typeof params.text === "function") {
        mark_params.text = params.text(d, i , vars);
      } else if(typeof params.text === "string") {
        mark_params.text = params.text;
      }
    } else if(vars.var_text !== "undefined") {
      mark_params.text = vars.accessor_data(d)[vars.var_text];
    }

    mark_params.source = [0, 0];
    mark_params.target = [vars.width, vars.height];
    mark_params.translate = [0, 0];

    if(typeof params.translate !== "undefined" && params.translate !== null) {
      if(typeof params.translate === "function") {
        mark_params.translate = params.translate(d, i, vars);
      } else {
        mark_params.translate = params.translate;
      }
    }

    // Available to all marks
    mark_params.x = utils.init_params("x", 0, params, d, i, vars);
    mark_params.y = utils.init_params("y", 0, params, d, i, vars);
    mark_params.height = utils.init_params("height", 10, params, d, i, vars);
    mark_params.width = utils.init_params("width", 10, params, d, i, vars);
    mark_params.translate[0] += vars.x_scale[0]["func"](vars.accessor_data(d)[vars.var_x]);
    mark_params.translate[1] += vars.y_scale[0]["func"](vars.accessor_data(d)[vars.var_y]);

    // Specific to marks / charts
    mark_params.rotate = utils.init_params("rotate", 0, params, d, i, vars);
    mark_params.fill = utils.init_params("fill", vars.color(vars.accessor_data(d)[vars.var_color]), params, d, i, vars);
    mark_params.stroke = utils.init_params("stroke", 0, params, d, i, vars);
    mark_params.text_anchor = utils.init_params("text_anchor", "end", params, d, i, vars);

    return mark_params;
  }


  utils.mark_params_values = function(params, vars, d, i) {

    var params_values = {};

    params_values.text = utils.init_params_values(vars.var_text, "default", params, d, i, vars);

    // Available to all marks
    params_values.x = utils.init_params_values(vars.var_x, 0, params, d, i, vars);
    params_values.y = utils.init_params_values(vars.var_y, 0, params, d, i, vars);
    params_values.height = utils.init_params_values(vars.var_height, 10, params, d, i, vars);
    params_values.width = utils.init_params_values(vars.var_width, 10, params, d, i, vars);

    params_values.translate = [0, 0];

    params_values.translate[0] += vars.x_scale[0]["func"](vars.accessor_data(d)[vars.var_x]);
    params_values.translate[1] += vars.y_scale[0]["func"](vars.accessor_data(d)[vars.var_y]);

    params_values.rotate = utils.init_params_values(vars.var_rotate, 0, params, d, i, vars);

/*
    // Specific to marks / charts
    mark_params.fill = utils.init_params("fill", vars.color(vars.accessor_items(d)[vars.var_color]), params, d, i, vars);
    mark_params.stroke = utils.init_params("stroke", 0, params, d, i, vars);
    mark_params.text_anchor = utils.init_params("text_anchor", "end", params, d, i, vars);
*/
    return params_values;
  }

  utils.push_array = function(arr, data) {
    var index = -1;
    vars[arr].forEach(function(d, i) {
      if(d === data[vars.var_id]) {
        index = i;
      }
    });

    if(index < 0) {
      vars[arr].push(data[vars.var_id])
    }
  }

  // Find index and removes it
  utils.pop_array = function(arr, data) {
    var index = -1;
    vars[arr].forEach(function(d, i) {
      if(d === data[vars.var_id]) {
        index = i;
      }
    });

    if(index > -1) {
      vars[arr].splice(index, 1);
    }
  }


  // Default parameters for all charts
  var default_vars = {
    // PUBLIC (set by the user)
    container : "",
    this_chart: null,

    new_data: null,
    time_data: null,

    dev : false,
    id : "id",
    id_var : "id",
    var_group: null,
    data: [],
    links: [],
    var_node_id: 'id', // ID to join the nodes/link data

    title: "",

    // Default dimensions
    margin: {top: 0, right: 0, bottom: 0, left: 0},
    rotate: 0,

    // Default Variables mapping
    var_color: null,
    var_sort_asc: false,

    // Interaction
    highlight: [],
    selection: [],
    filter: [],
    zoom: [],

    time: {
      var_time: null,
      current_time: null,
      parse: function(d) { return d; }
    },

    // TABLE
    columns: [],
    sort_by: {'column': 'name', 'asc': true},

    // DOTPLOT
    x_type: "linear",
    x_scale: [],
    x_ticks: 5,
    x_axis: null,
    x_format: function(d) { return d; },
    x_tickSize: 10,
    x_tickPadding: 0,
    x_tickValues: null,
    x_axis_show: false,
    x_axis_orient: "bottom",
    x_grid_show: false,
    x_text: true,
    x_text_custom: "",
    x_axis_translate: [0, 0],
    x_invert: false,
    x_domain: null,
    x_range: null,

    // SCATTERPLOT (INCLUDES DOTPLOT)
    y_type: "linear",
    y_scale: [],
    y_ticks: 5,
    y_axis: null,
    y_format: function(d) { return d; },
    y_tickSize: 10,
    y_tickPadding: 0,
    y_tickValues: null,
    y_axis_show: false,
    y_axis_orient: "left",
    y_grid_show: false,
    y_text: true,
    y_text_custom: "",
    y_axis_translate: [0, 0],
    y_invert: false,
    y_domain: null,
    y_range: null,

    r_scale: null,
    r_cutoff: function(d) { return d > 30; },

    // Automatically generate UI elements
    ui: true,

    lang: 'en_US', // 'es_ES, fr_FR', ..
    locales: {}, // Translations for various lang

    // Graphical properties for graphical marks
    color: d3.scale.category20c(),
    size: d3.scale.linear(),

    dispatch: [],
    evt: {register: function() {}, call: function() {} },

    // SVG Container
    svg: null,      // Contains the svg element
    root_svg: null, // Contains the group children to the svg element
    ratio: 0.5, // Visualization aspect ratio

    duration: 1000,
    interpolate: "monotone",

    layout: {},

    padding: 1,
    treemap_mode: 'squarify',

    treemap: {
      padding: 1,
      d_x: 30,
      d_y: 30,
      depth_text: 1,
      depth_rect: 2
    },

    radius: 5,

    radius_min: 2,
    radius_max: 10,

    mark: {
      height: 10,
      width: 10,
      rotate: 0,
      radius: 5,
      fill: function(d) { return vars.color(vars.accessor_values(d)[vars.var_color]); }
    },

    accessor_values: function(d) { return d; },
    accessor_items: function(d) { return d; },

    accessor_static: function(d) { return d; },
    accessor_data: function(d) {
      return d.values[vars.time.current_time];
    },

    container: "#viz",

    refresh: true,
    init: true,
    redraw_all: false,

    _user_vars: {},

    list: {type: ["sparkline", "dotplot", "barchart", "linechart", "scatterplot", "grid",
                  "stacked", "piechart", "slopegraph", "slopegraph_ordinal", "productspace", "treemap", "geomap",
                  "stackedbar", "ordinal_vertical", "ordinal_horizontal", "matrix", "radial",
                  "rectmap", "caterplot", "tickplot", "barchart_vertical"],
      mark: ['rect', 'circle', 'star', 'shape']
    },

    default_params: {},
    default_marks: {},

    z_index: [
 //     {selector: '.mark__group', attribute: '__aggregated', type: 'productspace', weight: 1},
      {selector: '.connect__group', type: 'productspace', weight: 1, event: 'highlightOut'},
      {selector: '.mark__group', type: 'productspace', weight: 1, event: 'highlightOut'},
      {selector: '.connect__group', attribute: '__highlighted', type: 'productspace', weight: 1, event: 'highlightOn'},
      {selector: '.mark__group', attribute: '__highlighted', type: 'productspace', weight: 1, event: 'highlightOn'},
      {selector: '.mark__group', attribute: '__highlighted__adjacent', type: 'productspace', weight: 1, event: 'highlightOn'},
    ],

    set: [],

    scale: 1,
    translate_x: 0,
    translate_y: 0,
    translate: [0, 0],

    flat_scene: false

  };

  vars = vistk.utils.merge(vars, default_vars);


  vars.evt.register = function(evt, f) {

    if(vars.dev) { console.log("[vars.evt.register]", evt); }

    if(typeof evt === "string") {
      evt = [evt];
    }

    evt.forEach(function(e) {

      if(typeof vars.evt[e] === "undefined") {
        vars.evt[e] = [];
      }

      vars.evt[e].push([f]);

    });

  };

  vars.evt.call = function(evt, a) {

    if(vars.dev) { console.log("[vars.evt.call]", evt, a); }

    if(typeof vars.evt[evt] === "undefined") {
      if(vars.dev) { console.warn("No callback for event", evt, a); }
      return;
    }

    vars.evt[evt].forEach(function(e, i) {
      if(vars.dev) { console.log("[calling evt]", e); }
      if(typeof(e[0]) !== "undefined") {
        e[0](a, 0, vars);
      }
    });
  };

  if (!vars.data) { vars.data = []; }

  vars.width = parseInt(d3.select("body").style('width').substring(0, d3.select("body").style('width').length-2));
  vars.width = vars.width - vars.margin.left - vars.margin.right;
  vars.height = vars.width * vars.ratio;

  // List of events
  vars.dispatch = d3.dispatch('init', 'start', 'finish', 'end', 'highlightOn', 'highlightOut', 'selection', 'resize', 'clearAnimations', 'timeUpdate');

  vars.evt.register('start', function(d) {
    if(vars.dev) { console.log("[vars.evt.call] start rendering"); }
    d3.select(vars.container).selectAll(".message").style('display', 'block').text('Loading...');
  });

  vars.evt.register('finish', function(d) {
    if(vars.dev) { console.log("[vars.evt.call] end rendering"); }
    if(utils.check_data_display()) {
      d3.select(vars.container).selectAll(".message").style('display', 'none');
    }
  });

  // Default events
  d3.select(window).on('resize', function(d) {
    vars.evt.call("resize", d);
  });

  vars.evt.register("highlightOn", function(d) {
    utils.push_array('highlight', d);
    d.__highlighted = true;
    d.__redraw = true;
  });

  vars.evt.register("highlightOn", function(d) {
    if(vars.dev) { console.log("[vars.evt.call] highlightOn"); }
  });

  vars.evt.register("highlightOut", function(d) {
    utils.pop_array('highlight', d);
    d.__highlighted = false;
    d.__redraw = true;

    // Temporary settings to prevent chart redraw tooltips .tooltip
    d3.select(vars.container).selectAll(".items__mark__text.tooltip").remove();
    d3.select(vars.container).selectAll(".items__mark__div.tooltip").remove();

  });

  vars.evt.register("highlightOut", function(d) {
    if(vars.dev) { console.log("[vars.evt.call] highlightOut"); }
  });

  vars.evt.register("timeUpdate", function(new_time) {
    if(vars.dev) { console.log("[vars.evt.call] timeUpdate"); }

    vars.time.current_time = new_time;
    d3.select(vars.container).call(vars.this_chart);

  });

  vars.evt.register("selection", function(d) {
    if(d.__selected) {
      utils.pop_array('highlight', d);
    } else {
      utils.pop_array('highlight', d);
    }
    d.__selected = !d.__selected;
    d.__redraw = true;
  });


  function chart(selection) {

    // Merging the various user params
    vars.user_vars = vistk.utils.merge(vars.user_vars, vars._user_vars);

    // Merging with current charts parameters set by the user in the HTML file
    vars = vistk.utils.merge(vars, vars.user_vars);

    // Create the top level element conaining the visualization
    if(!vars.svg && vars.init && vars.refresh) {
       if(vars.type !== "table") {

        vars.root_svg = d3.select(vars.container).append("svg")
          .attr("width", vars.width)
          .attr("height", vars.height)
          .style('overflow', 'hidden')
          .style('z-index', 0)
          .on("click", function(d) {

            if(vars.type === "productspace") {

              vars.links.forEach(function(e) {
                e.__selected = false;
                e.__selected__adjacent = false;
                e.__highlighted = false;
                e.__highlighted__adjacent = false;
                e.__redraw = true;
              });

              vars.new_data.forEach(function(f, k) {
                f.__selected = false;
                f.__selected__adjacent = false;
                f.__highlighted = false;
                f.__highlighted__adjacent = false;
                f.__redraw = true;
              });

              vars.zoom = [];
              vars.selection = [];
              vars.highlight = [];

            //  vars.init = true;
            //  vars.refresh = true;

              d3.select(vars.container).selectAll(".connect__line")
                .classed("highlighted", function(d, i) { return false; })
                .classed("highlighted__adjacent", function(d, i) { return false; })
                .classed("selected", function(d, i) { return false; })
                .classed("selected__adjacent", function(d, i) { return false; });

              d3.select(vars.container).selectAll("circle")
                .classed("highlighted", function(d, i) { return false; })
                .classed("highlighted__adjacent", function(d, i) { return false; })
                .classed("selected", function(d, i) { return false; })
                .classed("selected__adjacent", function(d, i) { return false; });

                utils.zoom_to_nodes(vars.zoom);
            // d3.select(vars.container).call(vars.this_chart);

            }

          })

        vars.svg = vars.root_svg.append("g")
          .attr("transform", "translate(" + vars.margin.left + "," + vars.margin.top + ")rotate(" + vars.rotate + ")");

        vars.message_svg = vars.root_svg.append("g").insert("text", ":first-child")
          .attr("transform", "translate(" + vars.margin.left + "," + vars.margin.top + ")rotate(" + vars.rotate + ")")
          .attr("class", "message")
          .attr("y", 80)
          .attr("x", 10)
          .attr("text-anchor", "start")
          .style("font-size", 40)
        //  .text("Loading..");


      } else {

        // HTML Container for table
        vars.svg = d3.select(vars.container).append("div")
            .style({height: vars.height+"px", width: vars.width+"px", overflow: "scroll"});

      }
   }


    // 1 - Init and define default values [INIT]
    // 2 - Duplicates the dataset [INIT]
    // 3 - Mutate all_data with static metadata [INIT]
    // Filter by time values
    // Filter by attribute/ Selection
    // Find unique values from dataset
    // Remove missing data
    // Aggregates the data [REFRESH]
    // Sorts the data

    // 1 - Init and define default parameters
    vars.items_data = [];

    // Each item needs coordinates
    // 1/ In case we use functions for X/Y variables
    // 2/ Adds default attributes __var_x and __var_y if no coordinate exist

    // Duplicate the dataset to prevent mutation
    if(vars.init) {

      // Get a copy of the whole dataset
      vars.all_data = JSON.parse(JSON.stringify(vars.data));

    }

    if(typeof vars.var_x !== "string" && typeof vars.var_x === "function") {
      vars.all_data.forEach(function(d, i) {
        d.__var_x = vars.var_x(d, i, vars);
      });
      vars.var_x = "__var_x";
    }

    if(typeof vars.var_x === "undefined") {
      // vars.data.forEach(function(d, i) {
      //   d.__var_x = vars.var_x(d, i, vars);
      // });
      vars.var_x = "__var_x";
    }

    if(typeof vars.var_y !== "string" && typeof vars.var_y === "function") {
      vars.all_data.forEach(function(d, i) {
        d.__var_y = vars.var_y(d, i, vars);
      });
      vars.var_y = "__var_y";
    }

    // In case the chart type is a function
    if(typeof vars.type !== "string" && typeof vars.type === "function") {
      vars.type = vars.type(vars);
    }

    if(typeof vars.type === 'undefined') {
      vars.type = 'none';
    };

    // In case the current_time is set dynamically
    if(typeof vars.time.current_time === "function") {
      vars.time.current_time = vars.time.current_time(vars.data);
    }

    // Calculate vars.new_data which should contain two things
    // 1/ The list of all items (e.g. countries, products)
    // 2/ The metadata for each items
    if(vars.init || vars.refresh) {

      // Creates default ids `__id` and `__value` for dataset without any id
      if(typeof vars.var_id === 'undefined') {

        if(vars.new_data === null) {
          vars.new_data = vars.all_data;
        }

        vars.new_data = vars.new_data.map(function(d, i) {

          if(typeof d !== 'object') {
            var e = {}
            e.__id = i;
            e.__value = d;
            d = e;
          }

          d.__id = i;
          return d;

        });

        vars.var_id = '__id';

        if(typeof vars.var_text === 'undefined') {
          vars.var_text = '__id';
        }

      } else {

        // Duplicate data to prevent mutation
        vars.new_data = JSON.parse(JSON.stringify(vars.all_data));

      }

      // If time filter parameter is set, then keep values for this time
      if(typeof vars.time.filter !== "undefined" && vars.time.filter.length > 0) {

        if(vars.dev) {
          console.log("[vars.time.filter]", vars.time.filter);
        }

        vars.new_data = vars.new_data.filter(function(d, i) {
          return vars.time.filter.indexOf(d[vars.time.var_time]) > -1;
        });

      }

      // If time filter interval is set, then keep values from this interval
      if(typeof vars.time.filter_interval != "undefined" && vars.time.filter_interval.length == 2) {

        if(vars.dev) {
          console.log("[vars.time.interval]", vars.time.filter_interval);
        }

        vars.new_data = vars.new_data.filter(function(d, i) {
          return (d[vars.time.var_time] >= vars.time.filter_interval[0]) && (d[vars.time.var_time] <= vars.time.filter_interval[1]);
        });

      }

      // Find unique values for various parameters
      vars.time.interval = d3.extent(vars.new_data, function(d) { return d[vars.time.var_time]; });
      vars.time.points = vistk.utils.find_unique_values(vars.new_data, vars.time.var_time);

      // In case no temporal values, change the accessor
      if(vars.time.var_time === null || vars.type === 'treemap') {
        vars.accessor_data = function(d) { return d; }
      }

      var unique_data = [];

      var lookup_index = [];
      var lookup_size = 0;

      vars.lookup_index_time = [];
      var lookup_time_size = 0;

      vars.new_data.forEach(function(d, i) {

        var index = -1;

        if(typeof lookup_index[d[vars.var_id]] === 'undefined') {

          index = lookup_size;
          lookup_size++;

          lookup_index[d[vars.var_id]] = index;

          utils.init_item(d);

          if(vars.filter.indexOf(d[vars.var_group]) > -1) {
            d.__filtered = true;
          }
          if(vars.highlight.indexOf(d[vars.var_id]) > -1) {
            d.__highlighted = true;
          }
          if(vars.selection.indexOf(d[vars.var_id]) > -1) {
            d.__selected = true;
          }

          d.__redraw = true;

          d.__index = index;

          // Dup for metadata
          var dup = JSON.parse(JSON.stringify(d));
          dup.values = [];

          unique_data.push(dup);

        } else {

          index = lookup_index[d[vars.var_id]];

        }

        var v = {};
        v[vars.var_id] = d[vars.var_id];
        v[vars.time.var_time] = d[vars.time.var_time];
        v[vars.var_y] = d[vars.var_y];
        v[vars.var_x] = d[vars.var_x];
        v[vars.var_color] = d[vars.var_color];
        v[vars.var_size] = d[vars.var_size];
        v[vars.var_text] = d[vars.var_text];
        v[vars.var_r] = d[vars.var_r];

        // TODO: make sure there is no existing value for this time
        unique_data[index].values[d[vars.time.var_time]] = v;

      });

      vars.new_data = unique_data;

    }

    // Filter data by attribute
    // TODO: not sure we should remove data, but add an attribute instead would better
    if(vars.filter.length > 0) {

      if(vars.dev) {
        console.log("[vars.filter]", vars.filter);
      }

      vars.new_data = vars.new_data.filter(function(d) {
        // We don't keep values that are not in the vars.filter array
        return vars.filter.indexOf(d[vars.var_group]+"") > -1;
      });

    }

    // Aggregate data
    if(typeof vars.set['__aggregated'] !== 'undefined' && vars.refresh) {

      if(vars.dev) {
        console.log("[vars.aggregate]", vars.aggregate);
      }

      // Do the nesting
      // Should make sure it works for a generc dataset
      // Also for time or none-time attributes
      nested_data = d3.nest()
        .key(function(d) {
          return d[vars.var_group];
        })
        .rollup(function(leaves) {

          // Generates a new dataset with aggregated data
          var aggregation = {};

          aggregation[vars.var_id] = leaves[0][vars.var_group];

          aggregation[vars.var_text] = leaves[0][vars.var_group];

          aggregation[vars.var_group] = leaves[0][vars.var_group];

          // Quick fix in case var_x is an ordinal scale
          if(vars.var_x !== vars.var_id && vars.var_x !== vars.time.var_time && vars.var_x !== vars.var_group) {
            aggregation[vars.var_x] = d3.mean(leaves, function(d) {
              return d[vars.var_x];
            });
          } else {
            aggregation[vars.var_x] = leaves[0][vars.var_x];
          }

          if(vars.var_y !== vars.var_id && vars.var_y !== vars.time.var_time) {
            aggregation[vars.var_y] = d3.mean(leaves, function(d) {
              return d[vars.var_y];
            });
          } else {
            aggregation[vars.var_y] = leaves[0][vars.var_y];
          }

          aggregation[vars.var_r] = d3.sum(leaves, function(d) {
            return d[vars.var_r];
          });

          aggregation.piescatter = [];
          aggregation.piescatter[0] = {};
          aggregation.piescatter[1] = {};

          aggregation.values = [];

          // Assuming all the time values are present in all items
          vars.time.points.forEach(function(time, i) {

            var d = {};

           // if(vars.var_x === vars.time.var_time) {
           //   d[vars.var_x] = leaves[0].values[i][vars.var_x];
           // } else {
           //   d[vars.var_x] = 0;
           // }

            // Init values
            d[vars.var_x] = leaves[0].values[time][vars.var_x];
            d[vars.var_y] = leaves[0].values[time][vars.var_y];
            d[vars.var_r] = leaves[0].values[time][vars.var_r];
            d[vars.var_id] = leaves[0].values[time][vars.var_id];

            // Time var
            d[vars.time.var_time] = leaves[0].values[time][vars.time.var_time];

            aggregation.values[time] = d;

            //return d;
          });

          // Assuming we only aggregate var_x, var_y, var_r
          leaves.forEach(function(d, i) {

            vars.time.points.forEach(function(time, i) {

              if(vars.var_x !== vars.time.var_time) {
                aggregation.values[time][vars.var_x] += d.values[time][vars.var_x];
              }

              aggregation.values[time][vars.var_y] += d.values[time][vars.var_y];
              aggregation.values[time][vars.var_r] += d.values[time][vars.var_r];

            });
          });

          utils.init_item(aggregation);
          aggregation.__aggregated = true;
          aggregation.__redraw = true;

          if(typeof vars.share_cutoff != "undefined") {

            aggregation.piescatter[0][vars.var_share] = d3.sum(leaves, function(d) {

              if(vars.share_cutoff(d)) {
                return 1;
              } else {
                return 0;
              }
            });

            aggregation.piescatter[1][vars.var_share] = d3.sum(leaves, function(d) {

              if(!vars.share_cutoff(d)) {
                return 1;
              } else {
                return 0;
              }
            });

          }

          vars.columns.forEach(function(c) {

            if(c === vars.var_text || c === vars.var_group) {
              return;
            }

            aggregation[c] = d3.mean(leaves, function(d) {
              return d[c];
            });
          });

          return aggregation;
        })
        .entries(vars.new_data);

      // Transform key/value into values tab only
      if(typeof vars.set['__aggregated'] !== 'undefined' && vars.set['__aggregated']) {
        vars.new_data = vars.new_data.concat(nested_data.map(function(d) { return d.values; }));
      } else {
        vars.new_data = nested_data.map(function(d) { return d.values; });
      }

    }

    if(vars.init || vars.refresh) {

      // Links between items
      // Used for product space
      if(vars.links !== null && vars.type === 'productspace') {

        vars.links.forEach(function(d, i) {

          if(typeof d.source === "string") {
            d.source = vistk.utils.find_node_by_id(vars.nodes, d.source);
          }

          if(typeof d.target === "string") {
            d.target = vistk.utils.find_node_by_id(vars.nodes, d.target);
          }

          d.__redraw = true;

        });

      }

      // Flagging missing nodes with __missing true attribute
      if(typeof vars.nodes !== "undefined" && vars.type === 'productspace') {

        vars.new_data = utils.join(vars.nodes, vars.new_data, vars.var_node_id, vars.var_id, function(new_data, node) {
            var r = new_data;
            if(typeof node === 'undefined') {
              return;
            }

            // Update all time points
            vars.time.points.forEach(function(time) {

              if(typeof(r.values[time]) === 'undefined') {
                r.values[time] = {};
                r.values[time][vars.var_id] = vars.var_id;
              }

              r.values[time].x = node.x;
              r.values[time].y = node.y;
            });

            // Keep the metadata
            r.x = node.x;
            r.y = node.y;

            r.__redraw = true;
            return r;
        });

        // Remove missing nodes
        // vars.new_data = vars.new_data.filter(function(d) {
        //  return !d.__missing;
        // });

        // Go through again the list of nodes
        // to make sure we display all the nodes
        vars.nodes.forEach(function(d, i) {

          var node = vistk.utils.find_node_coordinates_by_id(vars.new_data, vars.var_id, d[vars.var_node_id]);

          if(typeof node === "undefined") {

            d.values = [];
            d[vars.var_r] = 0;
            d[vars.var_id] = d.id;

            utils.init_item(d);
            d.__redraw = true;

            vars.new_data.push(d);

          }

        });

      }

    }

    // Sorting the dataset
    if(typeof vars.var_sort !== "undefined" && vars.refresh) {

      if(vars.dev) {
         console.log("[updating sort]", vars.var_sort, vars.var_sort_asc, vars.user_vars)
      }

      if(typeof vars.var_sort_asc !== "undefined" && !vars.var_sort_asc) {
        vars.new_data = vars.new_data.sort(function(a, b) {
          if(typeof vars.accessor_data(a) !== 'undefined' && typeof vars.accessor_data(b) !== 'undefined')
            return d3.ascending(vars.accessor_data(a)[vars.var_sort], vars.accessor_data(b)[vars.var_sort]);
        });
      } else {
        vars.new_data = vars.new_data.sort(function(a, b) {
          if(typeof vars.accessor_data(a) !== 'undefined' && typeof vars.accessor_data(b) !== 'undefined')
            return d3.descending(vars.accessor_data(a)[vars.var_sort], vars.accessor_data(b)[vars.var_sort]);
        });
      }
    }

    vars.new_data = vars.new_data.filter(function(d) {

      // Making sure we re-draw highlighted items
      if(vars.highlight.indexOf(d[vars.var_id]) > -1) {
        d.__highlighted = true;
        d.__redraw = true;
      } else if(d.__highlighted) {
        d.__highlighted = false;
        d.__redraw = true;
      }

      return typeof vars.accessor_data(d) !== 'undefined' && typeof vars.accessor_data(d)[vars.var_id] !== 'undefined';
    });

    if(vars.redraw_all) {
      vars.new_data.forEach(function(d) { d.__redraw = true; });
    }

    vars.redraw_all = false;

vars.locales = {
  'en_US': {
    'complexity': 'Complexity',
    'low': 'Low',
    'high': 'High',
    'export': 'Export',
    'non-export': 'Non-Export',
    'similarity_link': 'Similarity Link',
    'loading': 'Loading...',
    'no-data': 'No data is available'
  },
  'en_EN': {
    'complexity': 'Complexity',
    'low': 'Low',
    'high': 'High',
    'export': 'Export',
    'non-export': 'Non-Export',
    'similarity_link': 'Similarity Link',
    'loading': 'Loading...',
    'no-data': 'No data is available'
  },
  'es_ES': {
    'complexity': 'Complejidad',
    'low': 'Bajo',
    'high': 'Alto',
    'export': 'Exportación',
    'non-export': 'No-Exportación',
    'similarity_link': 'Enlar de similitud',
    'loading': 'Cargando...',
    'no-data': 'Sin datos disponibles'
  },
  'fr_FR': {
    'complexity': 'Complexité',
    'low': 'Basse',
    'high': 'Haute',
    'export': 'Export',
    'non-export': 'Non-Export',
    'similarity_link': 'Lien de similarité',
    'loading': 'Chargement...',
    'no-data': 'Aucune donnée disponible'
  }
},

vars.default_marks['rect'] = function(scope) {

  var this_params = {};

  this_params.type = 'rect';
  this_params.rendering = 'svg';
  this_params.radius = 5;

  this_params.enter = function(selection, params, vars, mark_id) {

    selection.each(function(d, i) {

      var mark_params = utils.mark_params(params, vars, d, i);

      d3.select(this)
        .attr('id', d.__mark_id)
        .classed("items__mark__rect", true)
        .attr("x", mark_params.x)
        .attr("y", mark_params.y)
        .attr("height", mark_params.height)
        .attr("width", mark_params.height)
        .style("stroke", mark_params.stroke)
        .style("fill", mark_params.fill)
        .attr("transform", "translate(" +  mark_params.translate + ")rotate(" +  mark_params.rotate + ")")
        .each(utils.bind_events);

    });

  };

  this_params.update = function(selection, params, vars, mark_id) {

    selection.each(function(d, i) {

    var mark_params = utils.mark_params(params, vars, d, i);

      d3.select(this)
        .classed("highlighted", function(d, i) { return d.__highlighted; })
        .classed("highlighted__adjacent", function(d, i) { return d.__highlighted__adjacent; })
        .classed("selected", function(d, i) { return d.__selected; })
        .classed("selected__adjacent", function(d, i) { return d.__selected__adjacent; })
        .attr("x", mark_params.x)
        .attr("y", mark_params.y)
        .attr("height", mark_params.height)
        .attr("width", mark_params.height)
        .style("stroke", mark_params.stroke)
        .style("fill", mark_params.fill)
        .attr("transform", "translate(" +  mark_params.translate + ")rotate(" +  mark_params.rotate + ")");

      });
  };

  this_params.exit = function(selection) {
    selection.remove();
  };

  return this_params;

}

vars.default_marks["circle"] = function(scope) {

  var this_params = {};

  this_params.type = 'circle';
  this_params.rendering = 'svg';
  this_params.radius = 5;

  this_params.enter = function(selection, params, vars, mark_id) {

    selection.each(function(d, i) {

      var mark_params = utils.mark_params(params, vars, d, i);

      d3.select(this)
        .attr('id', mark_id)
        .classed(mark_id, true)
        .classed("items__mark__circle", true)
        .attr("r", this_params.radius)
        .attr("transform", "translate(" +  mark_params.translate + ")rotate(" +  mark_params.rotate + ")")
        .each(utils.bind_events);

    });

  };

  this_params.update = function(selection, params, vars, mark_id) {

    selection.each(function(d, i) {

    var mark_params = utils.mark_params(params, vars, d, i);

      d3.select(this)
        .classed("highlighted", function(d, i) { return d.__highlighted; })
        .classed("highlighted__adjacent", function(d, i) { return d.__highlighted__adjacent; })
        .classed("selected", function(d, i) { return d.__selected; })
        .classed("selected__adjacent", function(d, i) { return d.__selected__adjacent; })
        .transition().duration(vars.duration)
        .attr("transform", "translate(" +  mark_params.translate + ")rotate(" +  mark_params.rotate + ")")


    })

  };

  this_params.exit = function(selection) {
	  selection.remove();
  };

  return this_params;

}

vars.default_params["sparkline"] = function(scope) {

  var params = {};

  params.x_scale = [{
    func: d3.scale.linear()
            .range([scope.margin.left, scope.width - scope.margin.left - scope.margin.right])
            .domain(scope.time.interval)
  }];

  params.y_scale = [{
    func: d3.scale.linear()
            .range([scope.margin.top, scope.height - scope.margin.top - scope.margin.bottom])
            .domain(d3.extent(Array.prototype.concat.apply([], vars.new_data.map(function(d) {
              return d3.values(d.values);
            })), function(d) {
              return d[vars.var_y];
            }))
  }];

  params.items = [{
    marks: [{
      type: "circle",
      rotate: "0",
    }, {
      type: "text",
      rotate: "0",
      translate: [-20, 0],
      text_anchor: "end"
    }]
  }];

  params.connect = [{
    attr: scope.time.var_time,
    marks: [{
      type: "path",
      rotate: "0",
      stroke: function(d) { return "black"; },
      func: d3.svg.line()
           .interpolate(scope.interpolate)
           .x(function(d) { return params.x_scale[0]["func"](d[scope.var_x]); })
           .y(function(d) { return params.y_scale[0]["func"](d[scope.var_y]); }),
      fill: 'none'
    }]
  }];

  params.x_axis_show = false;
  params.x_grid_show = false;

  params.y_axis_show = false;
  params.y_grid_show = false;
  params.y_invert = true;

  return params;

};

vars.default_params["dotplot"] = function(scope) {

  var params = {};

  params.x_scale = [{
    name: "linear",
    func: d3.scale.linear()
            .range([scope.margin.left, scope.width-scope.margin.left-scope.margin.right])
            .domain(d3.extent(vars.new_data, function(d) {
              return scope.accessor_data(d)[vars.var_x];
            }))
            .nice()
  }];

  // Custom domain for X-scale
  if(scope.x_domain !== null && scope.x_domain.length === 2) {
    params.x_scale[0]['func'].domain(scope.x_domain);
  }

  params.y_scale = [{
    name: "linear",
    func: d3.scale.linear()
            .range([scope.height/2, scope.height/2])
            .domain(d3.extent(vars.new_data, function(d) {
              return scope.accessor_data(d)[vars.var_y];
            }))
            .nice()
  }];

  params.items = [{
    attr: "name",
    marks: [{
      type: "circle",
    },{
      type: "text",
      rotate: "-90"
    }]
  }];

  params.x_axis_show = true;
  params.x_tickValues = [params.x_scale[0]["func"].domain()[0], params.x_scale[0]["func"].domain()[1]];
  params.x_axis_translate = [0, scope.height/2];

  params.y_axis_show = false;

  return params;

};

vars.default_params["barchart"] = function(scope) {

  var params = {};

  params.x_scale = [{
    func: d3.scale.ordinal()
            .rangeRoundBands([scope.margin.left, scope.width - scope.margin.left - scope.margin.right], .1)
            .domain(vars.new_data.map(function(d) {
              return scope.accessor_data(d)[vars.var_x];
            }))
  }];

  params.y_scale = [{
    func: d3.scale.linear()
            .range([scope.height - scope.margin.top - scope.margin.bottom, scope.margin.top])
            .domain(d3.extent(vars.new_data, function(d) {
              return scope.accessor_data(d)[vars.var_y];
            }))
            .nice()
  }];

  params.items = [{
    attr: "bar",
    marks: [{
      type: "rect",
      x: function() { return -scope.mark.width/2; },
      y: function(d) { return -scope.margin.top; },
      height: function(d) {
        return scope.height - scope.margin.bottom - scope.margin.top - params.y_scale[0]["func"](scope.accessor_data(d)[scope.var_y]);
      },
      width: function(d) {
        return params.x_scale[0]["func"].rangeBand();
      },
      fill: function(d) {
        return scope.color(scope.accessor_items(d)[scope.var_color]);
      }
    }, {
      type: 'text',
      text: function(d) {
        return scope.accessor_data(d)[vars.var_y];
      },
      translate: [params.x_scale[0]["func"].rangeBand() / 4, -20],
      text_anchor: 'middle'
    }]
  }];

  params.x_axis_show = true;
  params.x_axis_translate = [0, scope.height - scope.margin.bottom - scope.margin.top];
  params.x_grid_show = false;

  //params.y_axis_show = true;
  params.y_axis_translate = [scope.margin.left, -10];
  //params.y_grid_show = true;

  return params;

};

vars.default_params["linechart"] = function(scope) {

  var params = {};

  params.accessor_values = function(d) { return d.values; };
  params.accessor_items = function(d) { return d; };

  params.x_scale = [{
    func: d3.scale.linear()
            .range([scope.margin.left, scope.width - scope.margin.left - scope.margin.right])
            .domain(vars.time.interval)
  }];

  params.y_scale = [{
    func: d3.scale.linear()
            .range([scope.height - scope.margin.top - scope.margin.bottom, scope.margin.top])
            .domain(d3.extent(Array.prototype.concat.apply([], vars.new_data.map(function(d) {
              return d3.values(d.values);
            })), function(d) {
              return d[vars.var_y];
            }))
  }];

  params.items = [{
    marks: [{
      type: "circle",
     // fill: function(d) { return vars.color(params.accessor_items(d)[vars.var_color]); }
    }, {
      var_mark: '__highlighted',
      type: d3.scale.ordinal().domain([true, false]).range(['text', 'none']),
      translate: [10, 0],
      text: function(d) {
        return scope.accessor_data(d)[vars.var_y] + ' ' + d[vars.var_text];
      }
    }, {
      var_mark: '__selected',
      type: d3.scale.ordinal().domain([true, false]).range(['text', 'none']),
      translate: [10, 0],
      text: function(d) {
        return scope.accessor_data(d)[vars.var_y] + ' ' + d[vars.var_text];
      }
    }],
    accessor_data: function(d) {
      return d.values.filter(function(e) {
        return e[vars.time.var_time] == vars.time.current_time;
      })[0];
    }
  }];


  params.connect = [{
    marks: [{
      type: "path",
      stroke: function(d) {
        return vars.color(params.accessor_items(d)[vars.var_color]);
      },
      func: d3.svg.line()
           .interpolate(vars.interpolate)
           .x(function(d) { return params.x_scale[0]["func"](d[vars.var_x]); })
           .y(function(d) { return params.y_scale[0]["func"](d[vars.var_y]); }),
      fill: "none"
    }]
  }];

  params.x_ticks = vars.time.points.length;
  params.x_tickValues = null;
  params.x_axis_orient = "top";
  params.x_axis_show = true;
  params.x_grid_show = true;
  params.x_text = false;

  params.y_axis_show = false
  params.y_grid_show = false;
  params.y_invert = false;

  return params;

};

vars.default_params["scatterplot"] = function(scope) {

  var params = {};

  params.x_scale = [{
    func: d3.scale.linear()
            .range([scope.margin.left, scope.width - scope.margin.left - scope.margin.right])
            .domain(d3.extent(vars.new_data, function(d) {
              return scope.accessor_data(d)[vars.var_x];
            })).nice()
  }];

  params.y_scale = [{
    func: d3.scale.linear()
            .range([scope.height - scope.margin.top - scope.margin.bottom, scope.margin.top])
            .domain(d3.extent(vars.new_data, function(d) {
              return scope.accessor_data(d)[vars.var_y];
            })).nice()
  }];

  params.r_scale = d3.scale.linear()
              .range([vars.radius_min, vars.radius_max])
              .domain(d3.extent(vars.new_data, function(d) {
                return scope.accessor_data(d)[vars.var_r];
              }));

  params.items = [{
    marks: [{
        type: "circle",
        r_scale: d3.scale.linear()
                    .range([vars.radius_min, vars.radius_max])
                    .domain(d3.extent(vars.new_data, function(d) {
                      return scope.accessor_data(d)[vars.var_r];
                    })),
        fill: function(d) { return vars.color(vars.accessor_items(d)[vars.var_color]); }
      }, {
      var_mark: '__highlighted',
      type: d3.scale.ordinal().domain([true, false]).range(["text", "none"])
    }]
  }];

  params.x_axis_show = true;
  params.x_axis_translate = [0, scope.height - scope.margin.bottom - scope.margin.top];
  params.x_grid_show = true;
  params.x_ticks = 10;

  params.y_axis_show = true;
  params.y_axis_translate = [scope.margin.left, 0];
  params.y_grid_show = true;

  return params;

};

 vars.default_params["geomap"] = function(scope) {

  var params = {};

  params.var_x = 'x';
  params.var_y = 'y';

  params.accessor_data = function(d) { return d; };
  params.accessor_values = function(d) { return d.data.values; };

  if(vars.init || vars.refresh) {

    // countries contains bot the data and coordinates for shapes drawing
    vars.countries = topojson.object(vars.topology, vars.topology.objects.countries).geometries;
    vars.neighbors = topojson.neighbors(vars.topology, vars.countries);

    vars.countries.forEach(function(d) {

      // Retrieve the country name based on its id
      d[vars.var_id] = vars.names.filter(function(n) {
        return d.id == n.id;
      })[0][vars.var_id];

      // TODO: should merge on a more reliable join (e.g. 2-char)
      d.data = vars.new_data.filter(function(n) {
        return d[vars.var_id] === n[vars.var_id];
      })[0];

      // Two reasons why it is not defined
      // 1/ No data
      // 2/ Current country
      if(typeof d.data == "undefined") {

        var data = {}
        data[vars.var_id] = d[vars.var_id];
        d.data = data;
        d.data.__no_data = true;
      } else {
        d.data.__no_data = false;
      }

      d.__redraw = true;

    });


    vars.new_data = vars.countries.map(function(d) {

      d[vars.var_color] = d.data[vars.var_color];
      d[vars.var_group] = d.data[vars.var_group];
      if(typeof d.x === 'undefined') { d.x = 0; }
      if(typeof d.y === 'undefined') { d.y = 0; }
      return d;
    });

    vars.projection = d3.geo.equirectangular()
                    .scale(100);

    // This is the main function that draws the shapes later on
    vars.path = d3.geo.path()
        .projection(vars.projection);

    // Pr-process the shapes and calculate their BBox here and assign to x

    vars.new_data.forEach(function(d) {
      var a = vars.svg.append("path").attr("id", "geomap__pre-render").attr("d", vars.path(d))
      d.x = 200;// a.node().getBBox().x;
      d.y = 50; //a.node().getBBox().y;
      a.remove();
    })

  }

  params.x_scale = [{
    func: d3.scale.linear()
            .domain(d3.extent(vars.new_data, function(d) { return d[params.var_x]; }))
            .range([scope.margin.left, scope.width - scope.margin.left - scope.margin.right])
  }];

  params.y_scale = [{
    func: d3.scale.linear()
            .domain(d3.extent(vars.new_data, function(d) { return d[params.var_y]; }))
            .range([scope.margin.top, scope.height - scope.margin.top - scope.margin.bottom])
  }];

  params.items = [{
    marks: [{
      type: "shape",
      fill: d3.scale.linear()
              .domain([
                d3.min(vars.new_data, function(d) { return d[scope.var_color]; }),
                d3.max(vars.new_data, function(d) { return d[scope.var_color]; })
              ])
              .range(["red", "green"])
    }]
  }];

  return params;

};

vars.default_params["grid"] = function(scope) {

  var params = {};

  params.accessor_data = function(d) { return d; };

  // Chart specific metadata: grid
  // Generates x and y attributes to display items as a 2D grid
  if(vars.refresh) {

    var nb_dimension =  Math.ceil(Math.sqrt(vars.new_data.length));

    if(typeof scope.width_grid === 'undefined') {
      scope.width_grid = nb_dimension;
    }

    if(typeof scope.height_grid === 'undefined') {
      scope.height_grid = nb_dimension;
    }

    // Create foci for each dimension
    // TOFIX: should update children, not necessary replace
    d3.range(scope.width_grid).map(function(d, i) {

       d3.range(scope.height_grid).map(function(e, j) {

        var index = i * scope.height_grid + j;

        // To make sure we don't update more points than necessary
        if(index < vars.new_data.length) {

          vars.new_data[index].grid_x = i;
          vars.new_data[index].grid_y = j;
          vars.new_data[index].grid_index = index;

        }
      });

    });

  }

  params.x_scale = [{
    func: d3.scale.linear()
          .domain([0, scope.width_grid])
          .range([scope.margin.left, scope.width - scope.margin.left - scope.margin.right])
  }];

  params.y_scale = [{
    func: d3.scale.linear()
          .domain([0, scope.height_grid])
          .range([scope.height - scope.margin.top - scope.margin.bottom, scope.margin.top])
  }];

  params.items = [{
    marks: [{
      type: "rect",
    }, {
      type: "text",
      rotate: "-30"
    }]
  }];

  params.var_x = "grid_x";
  params.var_y = "grid_y";

  params.x_axis_show = false;
  params.y_axis_show = false;

  return params;

};

vars.default_params["stacked"] = function(scope) {

  var params = {};

  params.accessor_values = function(d) { return d.values; };
  params.accessor_items = function(d) { return d; };


  // Chart specific metadata: stacked
  if(vars.refresh) {

    // Make sure all items and all ranks are there
    vars.new_data.forEach(function(c) {

      vars.time.points.forEach(function(y) {
        var is_year = false;

        c.values.forEach(function(v) {

          if(v[vars.time.var_time] == y) {
            is_year = true;
          }
        });

        if(!is_year) {

          // Set missing values to null
          var v = {date: y, year: y};

          v[vars.time.var_time] = y;
          v[vars.var_y] = 0;
          c.values.push(v);

        }

      });

    });

    vars.stack = d3.layout.stack()
        .values(function(d) { return d3.values(d.values); })
        .x(function(d) { return d[vars.time.var_time]; })
        .y(function(d) { return d[vars.var_y]; });

     vars.new_data = vars.stack(vars.new_data);
  }

  params.x_scale = [{
    func: d3.time.scale()
            .range([scope.margin.left, scope.width - scope.margin.left - scope.margin.right])
            .domain(vars.time.interval)
  }];

  params.y_scale = [{
    func: d3.scale.linear()
            .range([scope.height - scope.margin.top - scope.margin.bottom, scope.margin.top])
            .domain(d3.extent(Array.prototype.concat.apply([], vars.new_data.map(function(d) {
              return d3.values(d.values);
            })), function(d) {
              return d.y + d.y0;
            }))
  }];

  params.connect = [{
    attr: vars.time.var_time,
    marks: [{
      type: "path",
      fill: function(d) { return vars.color(params.accessor_items(d)[vars.var_color]); },
      stroke: function(d) {
        return "black";
      },
      func: d3.svg.area()
              .interpolate('cardinal')
              .x(function(d) { return params.x_scale[0]["func"](d[vars.time.var_time]); })
              .y0(function(d) { return params.y_scale[0]["func"](d.y0); })
              .y1(function(d) { return params.y_scale[0]["func"](d.y0 + d.y); })
    }]
  }];

  params.x_axis_show = true;
  params.x_axis_translate = [0, scope.height - scope.margin.bottom - scope.margin.top];
  params.x_grid_show = true;
  params.x_ticks = vars.time.points.length;
  params.x_format = d3.time.format("%Y");
  params.x_text = false;

  params.y_axis_show = true;
  params.y_axis_translate = [scope.margin.left, 0];
  params.y_grid_show = true;

  return params;

};

vars.default_params["piechart"] = function(scope) {

  var params = {};

  if(vars.refresh) {

    scope.pie = d3.layout.pie().value(function(d) { return d[scope.var_share]; });
    scope.new_data = scope.pie(scope.new_data);

    scope.new_data.forEach(function(d) {
      d.values = d.data.values;
    });

    scope.new_data.forEach(function(d) { d.__redraw = true; });

  }

  params.x_scale = [{
    func: d3.scale.linear()
            .range([scope.width/2, scope.width/2])
  }];

  params.y_scale = [{
    func: d3.scale.linear()
            .range([scope.height/2, scope.height/2])
  }];

  params.r_scale = d3.scale.linear()
              .range([0, scope.width/6])
              .domain([0, d3.max(scope.new_data, function(d) {
                return scope.accessor_data(d)[scope.var_share];
              })]);

  params.items = [{
    marks: [{
      type: "arc",
      fill: function(d) { return scope.color(scope.accessor_items(d)[scope.var_color]); }
    }]
  }];

  params.x_axis_show = false;
  params.x_grid_show = false;

  params.y_axis_show = false;
  params.y_grid_show = false;

  params.postprocessing = function() {

  }

  return params;

};

vars.default_params["slopegraph"] = function(scope) {

  var params = {};

  params.accessor_values = function(d) { return d.values; };
  params.accessor_items = function(d) { return d.values; };

  params.x_scale = [{
    func: d3.scale.linear()
            .range([scope.margin.left, scope.width - scope.margin.left - scope.margin.right])
            .domain(scope.time.interval)
  }];

  params.y_scale = [{
    func: d3.scale.linear()
            .range([scope.height - scope.margin.top - scope.margin.bottom, scope.margin.top])
            .domain(d3.extent(vars.new_data, function(d) {
              return scope.accessor_data(d)[vars.var_y];
            }))
  }];

  params.items = [{
    attr: "right_label",
    marks: [{
      type: "text",
      text_anchor: "start"
    }]
  }, {
    attr: "left_label",
    accessor_data: function(d) {
      return d.values.filter(function(e) {
        return e.year == "2003";
      })[0];
    },
    marks: [{
      type: "text",
      text_anchor: "end",
      translate: [- 20, 0]
      // translate: [-(scope.width-scope.margin.left-scope.margin.right-scope.margin.left+20), 0]
    }]
  }];

  params.connect = [{
    attr: vars.time.var_time,
    marks: [{
      type: "path",
      rotate: "0",
      fill: 'red',
      stroke: function(d) { return "black"; },
      func: d3.svg.line()
           .interpolate(vars.interpolate)
           .x(function(d) { return vars.x_scale[0]["func"](d[vars.var_x]); })
           .y(function(d) { return vars.y_scale[0]["func"](d[vars.var_y]); }),
    }]
  }];

  params.x_ticks = vars.time.points.length;
  params.x_tickValues = vars.time.interval;
  params.x_axis_orient = "top";
  params.x_axis_show = true;
  params.x_grid_show = false;
  params.x_text = false;

  params.y_axis_show = false;
  params.y_grid_show = false;

  return params;

};

vars.default_params["slopegraph_ordinal"] = function(scope) {

  var params = {};

  params.accessor_values = function(d) { return d.values; };
  params.accessor_items = function(d) { return d.values; };

  params.x_scale = [{
    func: d3.scale.linear()
            .range([scope.margin.left, scope.width - scope.margin.left - scope.margin.right])
            .domain(scope.time.interval)
  }];

  params.y_scale = [{
    func: d3.scale.ordinal()
            .domain(d3.set(vars.new_data.map(function(d) { return d[vars.var_y]; })).values())
            .rangeBands([scope.margin.left, scope.width - scope.margin.left - scope.margin.right])
  }];

  params.items = [{
    attr: "right_label",
    marks: [{
      type: "text",
      text_anchor: "start"
    }]
  }, {
    attr: "left_label",
    accessor_data: function(d) {
      return d.values.filter(function(e) {
        return e.year == "2003";
      })[0];
    },
    marks: [{
      type: "text",
      text_anchor: "end",
      translate: [- 20, 0]
      // translate: [-(scope.width-scope.margin.left-scope.margin.right-scope.margin.left+20), 0]
    }]
  }];

  params.connect = [{
    attr: vars.time.var_time,
    marks: [{
      type: "path",
      rotate: "0",
      stroke: function(d) { return "black"; },
      func: d3.svg.line()
           .interpolate(vars.interpolate)
           .x(function(d) { return vars.x_scale[0]["func"](d[vars.var_x]); })
           .y(function(d) { return vars.y_scale[0]["func"](d[vars.var_y]); }),
    }]
  }];

  params.x_ticks = vars.time.points.length;
  params.x_tickValues = vars.time.interval;
  params.x_axis_orient = "top";
  params.x_axis_show = true;
  params.x_grid_show = false;
  params.x_text = false;

  params.y_axis_show = false;
  params.y_grid_show = false;

  return params;

};

vars.default_params["treemap"] = function(scope) {

  var params = {};

  if(vars.init) {

    // If no group is set, then each item is its own group
    if(typeof vars.var_group === "undefined" || vars.var_group === null) {
      vars.var_group = vars.var_id;
    }

    if(vars.var_group === vars.var_id) {
      vars.var_group = "_index_item";
    }

  }

  if(vars.refresh) {

    utils.create_hierarchy(scope);

    vars.layout.treemap = d3.layout.treemap()
        .padding(scope.treemap.padding)
        .sticky(true)
        .sort(function(a,b) { return a[scope.var_sort] - b[scope.var_sort]; })
        .size([scope.width - scope.margin.left - scope.margin.right, scope.height - scope.margin.top - scope.margin.bottom])
        .mode(scope.treemap_mode)
        .value(function(d) {
          if(typeof scope.accessor_data(d)[vars.var_size] === "function") {
            return scope.accessor_data(d)[vars.var_size](d);
          } else {
            return scope.accessor_data(d)[vars.var_size];
          }
        });

    vars.new_data = vars.layout.treemap.nodes(vars.root);

    // Since we generated new data, need to redraw
    vars.new_data.forEach(function(d) {
      d.__redraw = true;
    });

  }

  // Identity scale
  params.x_scale = vistk.utils.scale.linear(scope);

  params.y_scale = [{
    func: d3.scale.linear()
            .range([scope.margin.top, scope.height - scope.margin.top - scope.margin.bottom])
            .domain([scope.margin.top, scope.height - scope.margin.top - scope.margin.bottom]),
  }];

  params.items = [{
    marks: [{
      type: "divtext",
      filter: function(d, i) { return d.depth == vars.treemap.depth_text && d.dx > vars.treemap.dx && d.d_y >  vars.treemap.d_y; }
    }, {
      type: "rect",
      filter: function(d, i) { return d.depth == vars.treemap.depth_rect; },
      x: 0,
      y: 0,
      width: function(d) { return d.dx; },
      height: function(d) { return d.dy; }
    }]
  }];

  params.var_x = 'x';
  params.var_y = 'y';

  return params;

};

vars.default_params["radial"] = function(scope) {

  var params = {};

  params.var_x = 'x';
  params.var_y = 'y';

  if(vars.refresh) {

    utils.create_hierarchy(scope);

    var tree = d3.layout.tree()
        .size([360, scope.width / 3 - 120])
        .separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });

    var diagonal = d3.svg.diagonal.radial()
        .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });

    vars.nodes = tree.nodes(vars.root);
    vars.links = tree.links(vars.nodes);

    vars.new_data = vars.nodes;

    vars.new_data.forEach(function(d) {

      d.values = [];
      d.values[vars.time.current_time] = {};
      d.values[vars.time.current_time][vars.var_id] = d[vars.var_id];
      d.values[vars.time.current_time][vars.var_x] = d[vars.var_x];
      d.values[vars.time.current_time][vars.var_y] = d[vars.var_y];
      d.values[vars.time.current_time][vars.var_text] = d[vars.var_text];

      d.__redraw = true;
    });

    vars.links.forEach(function(d) { d.__redraw = true; });

  }

  params.x_scale = [{
    func: d3.scale.linear()
            .range([0, scope.width-scope.margin.left-scope.margin.right])
            .domain(d3.extent(vars.new_data, function(d) { return d.x; })).nice()
  }];

  params.y_scale = [{
    func: d3.scale.linear()
            .range([scope.height-scope.margin.top-scope.margin.bottom, scope.margin.top])
            .domain(d3.extent(vars.new_data, function(d) { return d.y; })).nice(),
  }];

  params.r_scale = d3.scale.linear()
              .range([10, 30])
              .domain(d3.extent(vars.new_data, function(d) { return d[vars.var_r]; }));

/*
  params.connect = [{
    attr: "links",
    type: "items",
    marks: [{
      type: "line",
      rotate: "0",
      func: null,
    }]
  }];
  */

  params.connect = [{
    attr: vars.time.var_time,
    marks: [{
      type: "path",
     // fill: function(d) { return vars.color(params.accessor_items(d)[vars.var_color]); },
      stroke: function(d) {
        return "black";
      },
      func: diagonal,
      translate: [scope.width / 2, scope.height / 2]
    }]
  }];

  params.items = [{
    marks: [{
      type: "text",
  //    rotate: function(d) { return d.x - 90; },
  //      translate: function(d) { return [d.y, 0]; }
  //    filter: function(d, i) { return d.depth == 1 && d.dx > 30 && d.dy > 30; }
    }, {
      type: "circle",
 //     filter: function(d, i) { return d.depth == 2; },
      r: 10,
      x: 0,
      y: 0,
      rotate: function(d) { return d.x - 90; },
      translate: function(d) { return [d.y, 0]; }
    }]
  }];


  return params;

};

vars.default_params["stackedbar"] = function(scope) {

  var params = {};

  if(vars.refresh) {

    var y0 = 0;

    vars.new_data.forEach(function(d) {

      d["y0"] = y0;
      y0 += d[vars.var_y];
     // d[vars.var_y] = y0;

    });

    vars.var_y = "y0";

  }

  params.x_scale = [{
    func: d3.scale.linear()
            .range([scope.height/2, scope.height/2])
            .domain([0, d3.max(vars.new_data, function(d) { return d[scope.var_x]; })])
            .nice()
  }];

  params.y_scale = [{
    func: d3.scale.linear()
            .range([scope.height - scope.margin.top - scope.margin.bottom, scope.margin.top])
            .domain([d3.max(vars.new_data, function(d) { return d[vars.var_height] + d['y0']; }), 0])
  }];

  params.items = [{
    attr: "bar",
    marks: [{
      type: "rect",
      x: function() { return -vars.mark.width/2; },
      y: 0,
      height: function(d) { return params.y_scale[0]["func"](d[vars.var_height]) -10; },
      width: function(d) { return vars.mark.width*10; },
      fill: function(d) { return scope.color(scope.accessor_items(d)[scope.var_color]); }
    }]
  }];

  params.x_axis_show = true;
  params.x_axis_translate = [0, scope.height - scope.margin.bottom - scope.margin.top];
  params.x_grid_show = false;

  params.y_axis_show = true;
  params.y_axis_translate = [scope.margin.left, 0];
  params.y_grid_show = true;

  return params;

};

vars.default_params["rectmap"] = function(scope) {

  var params = {};


  params.x_scale = [{
    func: d3.scale.linear()
            .range([scope.margin.left, scope.margin.left])
            .domain([0, d3.max(vars.new_data, function(d) {
              return scope.accessor_data(d)[vars.var_width];
            })])
  }];

  params.y_scale = [{
    func: d3.scale.linear()
            .range([scope.margin.top, scope.height - scope.margin.top - scope.margin.bottom])
            .domain([0, d3.max(vars.new_data, function(d) {
              return scope.accessor_data(d)[vars.var_height];
            })])
  }];

  params.width_scale = [{
    func: d3.scale.linear()
            .range([scope.margin.left, scope.width - scope.margin.left - scope.margin.right])
            .domain([0, d3.max(vars.new_data, function(d) {
              return scope.accessor_data(d)[vars.var_width];
            })])
  }];

  params.height_scale = [{
    func: d3.scale.linear()
            .range([scope.margin.top, scope.height - scope.margin.top - scope.margin.bottom])
            .domain([0, d3.max(vars.new_data, function(d) {
              return scope.accessor_data(d)[vars.var_height];
            })])
  }];


  if(vars.init) {

    vars.new_data.forEach(function(d) {
      d.x = 0;
      d.y = 0;
      d.dx = params.width_scale[0]["func"](d[vars.var_width]);
      d.dy = params.width_scale[0]["func"](d[vars.var_height]);
    });

  }

  params.items = [{
    marks: [{
     type: "text",
     x: function(d) { return params.width_scale[0]["func"](d[vars.var_width]); },
     y: function(d) { return params.height_scale[0]["func"](d[vars.var_height]) - 10; },
     text_anchor: "end"
   //  filter: function(d, i) { return d.depth == vars.treemap.depth_text && d.dx > vars.treemap.dx && d.d_y >  vars.treemap.d_y; }
   }, {
      type: "rect",
   //   filter: function(d, i) { return d.depth == vars.treemap.depth_rect; },
      x: 0,
      y: 0,
      width: function(d) { return params.width_scale[0]["func"](d[vars.var_width]); },
      height: function(d) { return params.height_scale[0]["func"](d[vars.var_height]); }
    }]
  }];

  params.var_x = 'x';
  params.var_y = 'y';

  return params;

};

vars.default_params["caterplot"] = function(scope) {

  var params = {};

  params.accessor_values = function(d) { return d.values; };
  params.accessor_items = function(d) { return d; };

  params.x_scale = [{
    func: d3.scale.ordinal()
            .rangeBands([scope.margin.left, scope.width - scope.margin.left - scope.margin.right])
            .domain(d3.set(vars.new_data.map(function(d) { return d[vars.var_x]; })).values())
  }];

  params.y_scale = [{
    func: d3.scale.linear()
            .range([scope.height - scope.margin.top - scope.margin.bottom, scope.margin.top])
            .domain(d3.extent(vars.new_data, function(d) { return d[vars.var_y]; })).nice()
  }];

  params.r_scale = d3.scale.linear()
              .range([vars.radius_min, vars.radius_max])
              .domain(d3.extent(vars.new_data, function(d) { return d[vars.var_r]; }));

  params.items = [{
    marks: [{
    type: 'circle',
    r_scale: d3.scale.linear()
                .range([vars.radius_min, vars.radius_max])
                .domain(d3.extent(vars.new_data, function(d) { return d[vars.var_r]; })),
    fill: function(d) { return vars.color(vars.accessor_items(d)[vars.var_color]); },
   // translate: function() {
   //   return [vars.x_scale[0]['func'].rangeBand() / 4, 0]
   // },
     }, {
      var_mark: '__highlighted',
      type: d3.scale.ordinal().domain([true, false]).range(['text', 'none'])
    }, {
      var_mark: '__selected',
      type: d3.scale.ordinal().domain([true, false]).range(['text', 'none']),
      translate: function(d) {
        return [10, -20];
      }
    }]
  }];

  params.connect = [];

  params.x_axis_show = true;
  params.x_axis_translate = [0, scope.height - scope.margin.bottom - scope.margin.top];
  params.x_grid_show = true;
  params.x_ticks = 10;

  params.y_axis_show = true;
  params.y_axis_translate = [scope.margin.left, 0];
  params.y_grid_show = true;
  params.y_invert = false;

  return params;

};

vars.default_params["tickplot"] = function(scope) {

  var params = {};

  params.items = [];

  params.x_scale = [{
    func: d3.scale.linear()
            .range([scope.margin.left, scope.width - scope.margin.left - scope.margin.right])
            .domain(d3.extent(vars.new_data, function(d) {
              return scope.accessor_data(d)[vars.var_x];
            })).nice()
  }];

  params.y_scale = [{
    func: d3.scale.linear()
            .range([scope.height - scope.margin.top - scope.margin.bottom, scope.margin.top])
            .domain(d3.extent(vars.new_data, function(d) {
              return scope.accessor_data(d)[vars.var_y];
            })).nice()
  }];

  scope.time.points.forEach(function(time) {

    var item = {};
    item.marks = [];
    // Draw items with a specific filter
    var mark = [{
        type: "rect",
        rotate: 90
      }];

    item.marks[0] = mark;

    item.accessor_data = function(d) {
      return d.values.filter(function(e) {
        return e.year == time;
      })[0];
    };

    params.items = params.items.concat(item);

  });

  params.x_ticks = vars.time.points.length;
  params.x_tickValues = null;
  params.x_axis_orient = "top";
  params.x_axis_show = true;
  params.x_grid_show = true;
  params.x_text = false;

  params.y_axis_show = false
  params.y_grid_show = false;
  params.y_invert = true;

  return params;

};

vars.default_params['barchart_vertical'] = function(scope) {

  var params = {};

  // params.x_scale = vistk.utils.scale.linear(scope);

  params.x_scale = [{
    func: d3.scale.linear()
            .range([scope.width - scope.margin.left - scope.margin.right, scope.margin.left])
            .domain([d3.max(vars.new_data, function(d) {
              return scope.accessor_data(d)[vars.var_x];
            }), d3.min(vars.new_data, function(d) {
              return scope.accessor_data(d)[vars.var_x];
            })])
            .nice()
  }];

  params.y_scale = [{
    func: d3.scale.ordinal()
            .rangeRoundBands([scope.height - scope.margin.top - scope.margin.bottom, scope.margin.top], .1)
            .domain(vars.new_data.map(function(d) {
              return scope.accessor_data(d)[vars.var_y];
            }))
  }];

  params.items = [{
    marks: [{
      type: "rect",
      x: function(d) {
         return -params.x_scale[0]["func"](scope.accessor_data(d)[scope.var_x]) + scope.margin.left;
      },
      y: function(d) {
        return 0;
//        return -scope.margin.top + scope.mark.width;
      },
      height: function(d) {
        return scope.mark.width;
      },
      width: function(d) {
        return params.x_scale[0]["func"](scope.accessor_data(d)[scope.var_x]) - scope.margin.left;
      },
      fill: function(d) {
        return scope.color(scope.accessor_data(d)[scope.var_color]);
      }
    }, {
      type: 'text',
      text: function(d) {
        return scope.accessor_data(d)[vars.var_x];
      },
      translate: [2, 5],
      text_anchor: 'start'
    }]
  }];

  params.x_axis_show = false;
  params.x_axis_translate = [0, scope.height - scope.margin.bottom - scope.margin.top];
  params.x_grid_show = false;

  params.y_axis_show = true;
  params.y_axis_translate = [scope.margin.left, 0];
  params.y_grid_show = true;

  return params;

};

vars.default_params["productspace"] = function(scope) {

  var params = {};

  var accessor_values = function(d) {
    return d.values.filter(function(v) {
      if(v[vars.time.var_time] === vars.time.current_time) {
        return v;
      }
    })[0];
  }

  params.x_scale = [{
    func: d3.scale.linear()
            .range([0, vars.width-vars.margin.left-vars.margin.right])
            .domain(d3.extent(vars.new_data, function(d) { return d[vars.var_x]; })).nice()
  }];

  params.y_scale = [{
    func: d3.scale.linear()
            .range([vars.height-vars.margin.top-vars.margin.bottom, vars.margin.top])
            .domain(d3.extent(vars.new_data, function(d) { return d[vars.var_y]; })).nice(),
  }];

  //params.r_scale = d3.scale.linear()
  //            .range([10, 30])
  //            .domain(d3.extent(vars.new_data, function(d) { return accessor_values(d)[vars.var_r]; }));

  params.items = [{
    marks: [{
      type: "circle",
     // r_scale: d3.scale.linear()
     //             .range([10, 30])
     //             .domain(d3.extent(vars.new_data, function(d) { return accessor_values(d)[vars.var_r]; })),
      fill: function(d) { return vars.color(vars.accessor_items(accessor_values(d))[vars.var_color]); }
    }, {
      type: "text",
      rotate: "30",
      translate: null
    }]
  }];

  params.connect = [{
    attr: "links",
    type: "items",
    marks: [{
      type: "line",
      func: null,
    }]
  }];

  params.x_axis_show = false;
  params.x_grid_show = false;

  params.y_axis_show = false;
  params.y_grid_show = false;


  if(vars.init) {
    vars.evt.register("highlightOn", function(d) {

      // Make sure the highlighted node is above other nodes
      vars.svg.selectAll('.mark__group').sort(function(a, b) { return a.__highlighted ;})

      var adjacent_links = utils.find_adjacent_links(d, vars.links);

      adjacent_links.forEach(function(e) {

          // Redraw adjacent links
          e.__highlighted__adjacent = true;
          e.__redraw = true;

         vars.new_data.forEach(function(f, k) {

           if(f[vars.var_id] === e.target[vars.var_id] || f[vars.var_id] === e.source[vars.var_id]) {
            // Redraw adjacent nodes
             f.__highlighted__adjacent = true;
             f.__redraw = true;
           }

         });

      });

    });

    vars.evt.register("highlightOut", function(d) {

      vars.new_data.forEach(function(f, k) {
        if(f.__highlighted__adjacent) {
          f.__highlighted__adjacent = false;
          f.__redraw = true;
        }
      });

      vars.links.forEach(function(f, k) {
        if(f.__highlighted__adjacent) {
          f.__highlighted__adjacent = false;
          f.__redraw = true;
        }
      });

      d3.select(vars.container).selectAll(".connect__line")
        .classed("highlighted", function(d, i) { return false; })
        .classed("highlighted__adjacent", function(d, i) { return false; })

      d3.select(vars.container).selectAll("circle")
        .classed("highlighted", function(d, i) { return false; })
        .classed("highlighted__adjacent", function(d, i) { return false; })

    });

    vars.evt.register("selection", function(d) {

      // Make sure the highlighted node is above other nodes
      // vars.svg.selectAll('.mark__group').sort(function(a, b) { return a.__highlighted ;})

      vars.new_data.forEach(function(f, k) {
        if(f.__selected) {
          f.__selected = false;
          f.__redraw = true;
        }

        if(f.__selected__adjacent) {
          f.__selected__adjacent = false;
          f.__redraw = true;
        }

      });

      vars.links.forEach(function(f, k) {
        if(f.__selected) {
          f.__selected = false;
          f.__redraw = true;
        }

        if(f.__selected__adjacent) {
          f.__selected__adjacent = false;
          f.__redraw = true;
        }

      });

      d.__selected = true;
      d.__redraw = true;

      var adjacent_links = utils.find_adjacent_links(d, vars.links);

      adjacent_links.forEach(function(e) {

        // Update links
        e.__selected = true;
        e.__selected__adjacent = true;
        e.__redraw = true;

        vars.new_data.forEach(function(f, k) {

          if(f[vars.var_id] === e.target[vars.var_id] || f[vars.var_id] === e.source[vars.var_id]) {

            // Update nodes
            f.__selected = true;
            f.__selected__adjacent = true;
            f.__redraw = true;
          }

        });

      });

      d3.select(vars.container).selectAll(".connect__line")
        .classed("selected", function(d, i) { return d.__selected; })
        .classed("selected__adjacent", function(d, i) { return d.__selected__adjacent; })

      d3.select(vars.container).selectAll("circle")
        .classed("selected", function(d, i) { return d.__selected; })
        .classed("selected__adjacent", function(d, i) { return d.__selected__adjacent; })

    });
  }

  return params;

};

vars.default_params["ordinal_vertical"] = function(scope) {

  var params = {};

  params.x_scale = [{
    func: d3.scale.linear()
            .range([scope.width/2, scope.width/2])
            .nice()
  }];

  params.y_scale = [{
    func: d3.scale.ordinal()
            .domain(d3.set(vars.new_data.map(function(d) { return d[vars.var_y]; })).values())
            .rangeBands([scope.margin.left, scope.width - scope.margin.left - scope.margin.right])
  }];

  params.items = [{
    marks: [{
      type: "circle"
    },{
      type: "text"
    }]
  }];

  params.connect = [];

  params.x_axis_show = false;

  params.y_axis_show = false;

  return params;

}

vars.default_params["ordinal_horizontal"] = function(scope) {

  var params = {};

  params.x_scale = [{
    func: d3.scale.ordinal()
            .domain(d3.set(vars.new_data.map(function(d) {
              return d.values[vars.time.current_time][vars.var_x];
            })).values())
            .rangeBands([scope.margin.left, scope.width - scope.margin.left - scope.margin.right]),
  }];

  params.y_scale = [{
    name: "linear",
    func: d3.scale.linear()
            .range([scope.height/2, scope.height/2])
            .domain([0, d3.max(vars.new_data, function(d) {
              return d[scope.var_y];
            })])
            .nice()
  }];

  params.items = [{
    marks: [{
      type: "circle"
    },{
      type: "text"
    }]
  }];

  params.connect = [];

  params.x_axis_show = false;

  params.y_axis_show = false;

  return params;

}

vars.default_params["matrix"] = function(scope) {

  var params = {};

  // vars.new_data = miserabels

  // A matrix is a permutation of two ordinal scales
  // Each cell is a graphical mark


  if(vars.refresh) {

    // Prepare data

    // Duplicate and create


  }



  params.connect = [{
    marks: [{
      type: "rect"
    }]
  }];

// Horizontal ordinal scale
// var x = d3.scale.ordinal().rangeBands([0, vars.width]),
var z = d3.scale.linear().domain([0, 4]).clamp(true),
    c = d3.scale.category10().domain(d3.range(10));

  // TODO: Re-use previous scales
  // vars.default_params["ordinal_vertical"]
  // vars.default_params["ordinal_horizontal"]
  params.x_scale = [{
    func: d3.scale.ordinal()
            .domain(d3.set(vars.new_data.map(function(d) { return d[vars.var_x]; })).values())
            .rangeBands([scope.margin.left, scope.width - scope.margin.left - scope.margin.right]),
  }];

  /* Prototyping ideal configuration
  params.items = [{
    marks: [{
      type: 'text'
    }],
    marks: [{
      type: 'text'
    }]
   }];
  */

  var matrix = [],
      nodes = vars.nodes,
      n = vars.nodes.length;

  // Compute index per node.
  nodes.forEach(function(node, i) {
    node.index = i;
    node.count = 0;
    matrix[i] = d3.range(n).map(function(j) { return {x: j, y: i, z: 0}; });
  });

  // Convert links to matrix; count character occurrences.
  vars.links.forEach(function(link) {
    matrix[link.source][link.target].z += link.value;
    matrix[link.target][link.source].z += link.value;
    matrix[link.source][link.source].z += link.value;
    matrix[link.target][link.target].z += link.value;
    nodes[link.source].count += link.value;
    nodes[link.target].count += link.value;
  });

  // Precompute the orders.
  var orders = {
    name: d3.range(n).sort(function(a, b) { return d3.ascending(nodes[a].name, nodes[b].name); }),
    count: d3.range(n).sort(function(a, b) { return nodes[b].count - nodes[a].count; }),
    group: d3.range(n).sort(function(a, b) { return nodes[b].group - nodes[a].group; })
  };

  // The default sort order.
  params.x_scale[0]['func'].domain(orders.name);

  vars.svg.append("rect")
      .attr("class", "background")
      .attr("width", vars.width)
      .attr("height", vars.height);

  var row = vars.svg.selectAll(".row")
      .data(matrix)
    .enter().append("g")
      .attr("class", "row")
      .attr("transform", function(d, i) { return "translate(0," + params.x_scale[0]['func'](i) + ")"; })
      .each(row);

  row.append("line")
      .attr("x2", vars.width);

  row.append("text")
      .attr("x", -6)
      .attr("y", params.x_scale[0]['func'].rangeBand() / 2)
      .attr("dy", ".32em")
      .attr("text-anchor", "end")
      .text(function(d, i) { return nodes[i].name; });

  var column = vars.svg.selectAll(".column")
      .data(matrix)
    .enter().append("g")
      .attr("class", "column")
      .attr("transform", function(d, i) { return "translate(" + params.x_scale[0]['func'](i) + ")rotate(-90)"; });

  column.append("line")
      .attr("x1", -vars.width);

  column.append("text")
      .attr("x", 6)
      .attr("y", params.x_scale[0]['func'].rangeBand() / 2)
      .attr("dy", ".32em")
      .attr("text-anchor", "start")
      .text(function(d, i) { return nodes[i].name; });

  function row(row) {
    var cell = d3.select(this).selectAll(".cell")
        .data(row.filter(function(d) { return d.z; }))
      .enter().append("rect")
        .attr("class", "cell")
        .attr("x", function(d) { return params.x_scale[0]['func'](d.x); })
        .attr("width", params.x_scale[0]['func'].rangeBand())
        .attr("height", params.x_scale[0]['func'].rangeBand())
        .style("fill-opacity", function(d) { return z(d.z); })
        .style("fill", function(d) { return nodes[d.x].group == nodes[d.y].group ? c(nodes[d.x].group) : null; })

  }

  return params;

};


    selection.each(function(d) {

      // Trigger the previous visualization updates (e.g. to clear animations)
      if(vars.init || vars.refresh) {
        vars.evt.call("clearAnimations", null);
        vars.evt.call('start', null);
      }

      // If no data, display a user friendly message telling
      if(!utils.check_data_display() && vars.init) {

        d3.select(vars.container).selectAll(".message")
          .style('display', 'block')
          .text(vars.locales[vars.lang]['no-data']);

        vars.svg.style('visibility', 'hidden');

      } else {

        // There is no data to display so we show a message
        vars.svg.style('visibility', 'visible');
      }

      switch(vars.type) {

        case 'raw':

        // Display the current dataset
         vars.svg.append("span")
             .html(JSON.stringify(vars.new_data));

        break;

      case 'table':

       vars.svg.select("table").remove();

       function row_data(row, i) {

        // Creates an array first of the size of the desired rows
        // Then fills the array with the appropriate data
        // Applies some formatting depending on the index of the column
        return vars.columns.map(function(column, i) {
          
          // console.log( vars.accessor_year(row)[vars.columns[i]], i, vars.columns, row["group"], row[vars.columns[i]])

           return row[column];      
/*
          if(i==0 || i==1) {

            return row[column];      

           } else if(i == 4) {

            var million_scale = 1;
            var population = vars.accessor_year(row)[vars.columns[i]];

            return d3.format(",")(population);//+d3.formatPrefix(million_scale).symbol;
          
           } else if(i == 3) {

            return parseFloat(vars.accessor_year(row)[vars.columns[i]]).toFixed(1);

          } else if(i == 2) {

            var gdp = vars.accessor_year(row)[vars.columns[i]];
            var million_scale = 1000000000;
            return d3.round(d3.formatPrefix(million_scale, 1).scale(gdp), 1)+d3.formatPrefix(million_scale).symbol;
          
          // Extra attribute that we manually added
          } else {

            return vars.var_year;

          }
          */
        });
      }

      vars.evt.register("highlightOn", function(d) {
        vars.svg.selectAll("tr")
                .filter(function(e, j) { return e === d; })
                .style("background-color", "#F3ED86");
      });

      vars.evt.register("highlightOut", function(d) {
        tbody.selectAll("tr")
          .style("background-color", null);
      });

      function create_table(data) {

        if(vars.debug) { console.log("[create_table]"); }

        var table = vars.svg.append("table").style("overflow-y", "scroll"),
          thead = table.append("thead").attr("class", "thead");
        tbody = table.append("tbody");

        if(vars.title != null) {

          var title = vars.title;

          if(typeof vars.current_time !== "undefined") {
            title += " (" + vars.time.current_time + ")";
          }

          table.append("caption")
            .html(title);
        }

        thead.append("tr").selectAll("th")
          .data(vars.columns)
        .enter()
          .append("th")
          .text(function(d) { return d; })
          .on("click", function(header, i) {

            click_header(header);
            paint_zebra_rows(tbody.selectAll("tr.row"));

          });

        var rows = tbody.selectAll("tr.row")
          .data(data)
        .enter()
          .append("tr")
          .attr("class", "row");

        var cells = rows.selectAll("td")
          .data(row_data)
        .enter()
          .append("td")
          .text(function(d) { return d; })
          .on("mouseover", function(d, i) {
            vars.evt.call("highlightOn", d3.select(this.parentNode).data()[0]);
          })
          .on("mouseout", function(d) {
            vars.evt.call("highlightOut", d3.select(this.parentNode).data()[0]);
          })
          .on("click", function(d) {

            var data = d3.select(this.parentNode).data()[0];
            var index = vars.selection.indexOf(data);

            if(index <0) {
              vars.selection.push(data);
            } else {
              vars.selection.splice(index, 1);
            }

          });

        }

       // Function that orders the rows of the table
        function sort_by(header) {

          if(vars.debug) { console.log("[sort_by]", header); }

          vars.sort_by.column = header;
          vars.sort_by.is_sorted = !vars.sort_by.is_sorted;
/*
          if(vars.aggregate == 'continent') {
            vars.accessor_year = accessor_year_agg;
          } else {
            vars.accessor_year = accessor_year;
          }
  */
          d3.select(".thead").selectAll("th").attr("id", null);

          // For those specific columns, we are sorting strings
          if (header === "continent" || header === "name") {

            tbody.selectAll("tr").sort(function(a, b) {
              var ascending = d3.ascending(a[header], b[header]);
              return vars.sort_by.is_sorted ? ascending : - ascending;
            });

          // For the others, we sort numerical values
          } else {

            tbody.selectAll("tr").sort(function(a, b) {

              a = vars.accessor_year(a)[header];
              b = vars.accessor_year(b)[header];
              var ascending =  a > b ? 1 : a === b ? 0 : -1;

              return vars.sort_by.is_sorted ? ascending : - ascending;
            });

          }
        }


        function click_header(header) {

          var this_node = d3.selectAll("th").filter(function(d) {
              return d === header;
            });

          var is_sorted = (this_node.attr("class") === "sorted");

          d3.selectAll("th").text(function(d) {
            return d.replace("▴", "");
          });

          d3.selectAll("th").text(function(d) {
            return d.replace("▾", "");
          });

          if(!is_sorted) {
            this_node.classed("sorted", true)
                      .text(this_node.text()+"▾");
          }
          else {
            this_node.classed("sorted", false)
                     .text(this_node.text()+"▴");
          }

          if(vars.dev) { console.log("[click_header]", is_sorted); }

         // vars.sort_by.is_sorted = !vars.sort_by.is_sorted;
          sort_by(header);

        }

        function paint_zebra_rows(rows) {
          rows.filter(function() {
            return d3.select(this).style("display") !== "none";
          })
            .classed("odd", function(d, i) { return (i % 2) === 0; });
        }

        // If no column have been specified, take all columns
        // vars.columns = d3.keys(vars.data[0])

        // Basic dump of the data we have
        create_table(vars.new_data);

        paint_zebra_rows(tbody.selectAll("tr.row"));
        // Now update the table

        break;
        
      case "boxplot":

        var margin = {top: 10, right: 50, bottom: 20, left: 50},
            width = 120 - margin.left - margin.right,
            height = 500 - margin.top - margin.bottom;

        var min = Infinity,
            max = -Infinity;

        var chart = d3.box()
            .whiskers(iqr(1.5))
            .width(width)
            .height(height);

          data = [];

          vars.new_data.forEach(function(x) {
            var e = Math.floor(x.Expt - 1),
                r = Math.floor(x.Run - 1),
                s = Math.floor(x.Speed),
                d = data[e];
            if (!d) d = data[e] = [s];
            else d.push(s);
            if (s > max) max = s;
            if (s < min) min = s;
          });

          chart.domain([min, max]);

          d3.select(vars.container).selectAll(".box").data(data)
            .enter().append("svg")
              .attr("class", "box")
              .attr("width", width + margin.left + margin.right)
              .attr("height", height + margin.bottom + margin.top)
            .append("g")
              .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
              .call(chart);

        // Returns a function to compute the interquartile range.
        function iqr(k) {
          return function(d, i) {
            var q1 = d.quartiles[0],
                q3 = d.quartiles[2],
                iqr = (q3 - q1) * k,
                i = -1,
                j = d.length;
            while (d[++i] < q1 - iqr);
            while (d[--j] > q3 + iqr);
            return [i, j];
          };
        }

        break;

      case "none":

        var none_params = function(scope) {

          var params = {};
          params.accessor_data = function(d) { return d; };

          params.x_scale = [{
            func: d3.scale.identity()
          }];

          params.y_scale = [{
            func: d3.scale.identity(),
          }];

          params.items = [{
            marks: [{
                type: "circle",
                radius: 5
              }, {
                type: "text",
                rotate: "30",
                translate: null
              }]
          }];

          return params;

        };

        vars = vistk.utils.merge(vars, none_params(vars));

        // LOAD USER PARAMS
        vars.items = vistk.utils.merge(vars.items, vars.user_vars.items);

        // In case we don't have (x, y) coordinates for nodes'
        vars.force = d3.layout.force()
            .size([vars.width, vars.height])
            .charge(-50)
            .linkDistance(10)
            .on("tick", tick)
            .on("start", function(d) {
              // TODO: register the clearAnimation here
            })
            .on("end", function(d) {
              // TODO: un-register the clearAnimation here
            })

        vars.var_x = 'x';
        vars.var_y = 'y';

        vars.force.nodes(vars.new_data).start();

        // In case we change visualization before the nodes are settled
        vars.evt.register("clearAnimations", function(d) {
          vars.force.nodes(vars.new_data).stop();
        });

        var index_item = 0;
        var accessor_data = function(d) { return d; };

        // PRE-UPDATE
        var gItems = vars.svg.selectAll(".mark__group")
                        .data(vars.new_data, function(d, i) {
                          d._index_item = index_item;
                          return accessor_data(d)[vars.var_id] + "_" + index_item;
                        });

        // ENTER
        var gItems_enter = gItems.enter()
                        .append("g")
                        .each(utils.items_group)
                        .attr("transform", function(d, i) {
                          return "translate(" + vars.margin.left + ", " + vars.height/2 + ")";
                        });

       // APPEND AND UPDATE ITEMS MARK
        vars.items[0].marks.forEach(function(params) {
          gItems_enter.call(utils.draw_mark, params);
          gItems.call(utils.draw_mark, params);
        });

        // EXIT
        var gItems_exit = gItems.exit().remove()  ;

        // POST-UPDATE

        function tick(duration) {

          vars.svg.selectAll(".mark__group")
                          .attr("transform", function(d, i) {
                            return "translate(" + d.x + ", " + d.y + ")";
                          });

        }

      break;

      default:

        if(typeof vars.default_params[vars.type] === "undefined") {
           console.log("No params for chart " + vars.type);
        }

        if(vars.dev) { console.log("[init.vars.default]", vars); }

        // If there is an existing configuration
        if(vars.list.type.indexOf(vars.type) >= 0) {

          var scope = {};

          scope = vars.default_params[vars.type](vars);

          vars = vistk.utils.merge(vars, scope);

          // Disabled since merging is more complex than that
          //if(vars.type !== "stacked")
          //  vars.items = vistk.utils.merge(vars.items, vars.user_vars.items);

          // Enabling a more simple option
          if(typeof vars.user_vars.items !== "undefined") {
            vars.items = vars.user_vars.items;
          }

        } else {

          // LOAD CHART PARAMS
          vars = vistk.utils.merge(vars, vars.default_params[vars.type]);

          // LOAD USER PARAMS
          vars.items = vistk.utils.merge(vars.items, vars.user_vars.items);

        }

        vars.svg.call(utils.draw_chart, vars, vars.new_data);

      break;

    }


      // FUNCTIONS TO CREATE UI ELEMENTS
      // Those functions are companion to the charts, not required

      if(vars.ui.default) {

        // BUILDING THE UI elements
        d3.select(vars.container).selectAll(".break").data([vars.var_id])
          .enter()
            .append("p")
            .attr("class", "break");

        if(vars.var_group) {

          unique_categories = d3.set(vars.new_data
            .filter(function(d) {
              return typeof vars.accessor_data(d) !== 'undefined';
            })
            .map(function(d) { return vars.accessor_data(d)[vars.var_group]; })).values();

          label_checkboxes = d3.select(vars.container).selectAll(".checkboxes").data(unique_categories)
            .enter()
              .append("label")
              .attr("class", "checkboxes");

          label_checkboxes.append("input")
              .attr("type", "checkbox")
              .attr("value", function(d) { return d; })
              .property("checked", function(d) {
                  return vars.filter.indexOf(d) > -1;
               })
              .on("change", function(d) {

                utils.update_filters(this.value, this.checked);
                vars.refresh = true;
                d3.select(vars.container).call(vars.this_chart);

              });

          label_checkboxes.append("span")
              .html(function(d) {
                var count = vars.new_data
                .filter(function(d) {
                  return typeof vars.accessor_data(d) !== 'undefined';
                })
                .filter(function(e, j) { return vars.accessor_data(e)[vars.var_group] == d; }).length;
                return d + " (" + count + ")";
              });

        }

        if(typeof vars.var_id == "object") {

          var label_radios = d3.select(vars.container).selectAll(".aggregations").data(vars.var_id)
            .enter()
              .append("label")
              .attr("class", "aggregations");

          // TODO: find levels of aggregation
          label_radios.append("input")
                     .attr("type", "radio")
                     .attr("id", "id")
                     .attr("value", function(d) { return d; })
                     .attr("name", "radio-nest")
                     .property("checked", true)
                     .on("change", function(d) {

                       vars.aggregate = d;
                       vars.refresh = true;
                       d3.select(vars.container).call(vars.this_chart);

                     });

          label_radios.append("span")
              .html(function(d) {
  //              var count = vars.data.filter(function(e, j) { return e[vars.var_group] == d; }).length;
                // TODO
                var count = "";
                return d + " (" + count + ")";
              });

        }

      if(vars.time.var_time !== null) {

        var label_slider = d3.select(vars.container)
          .selectAll(".slider")
          .data([vars.var_id])
        .enter()
          .append("label")
          .attr("class", "slider");

        // Assuming we have continuous years
        // unique_years = d3.set(vars.data.map(function(d) { return d[vars.time.var_time];})).values();

        all_values = vars.data.map(function(d) { return d[vars.time.var_time];});

         var u = {};
        unique_years = [];
         for(var i = 0, l = all_values.length; i < l; ++i){
            if(u.hasOwnProperty(all_values[i])) {
               continue;
            }
            unique_years.push(all_values[i]);
            u[all_values[i]] = 1;
         }

        // TODO: find time range
        label_slider.append("input")
                      .attr("type", "range")
                      .attr("class", "slider-random")
                      .property("min", d3.min(unique_years))
                      .property("max", d3.max(unique_years))
                      .property("value", vars.time.current_time)
                      .attr("step", 1)
                      .on("input", function() {
                        vars.redraw_all = true;
                        vars.evt.call("timeUpdate", +this.value);
                      })
                      .style("width", "100px");

      }

     if(vars.x_scale.length > 0) {

        // Additional options below
        d3.select(vars.container).selectAll("#select_var_x").data([vars.var_id])
          .enter()
            .append("select")
            .attr("id", "select_var_x")
            .on("change", function(d) {

              vars.this_chart.params({
                var_x: this.value
              })
              d3.select(vars.container).call(vars.this_chart)

            })
            .selectAll("option")
            .data(d3.keys(vars.data[0]))
          .enter()
            .append("option")
            .attr("value", function(d) { return d; })
            .html(function(d) { return d; })

            var label_radios = d3.select(vars.container).selectAll(".aggregations").data(["index", "linear"])
              .enter()
                .append("label")
                .attr("class", "aggregations");

            // TODO: find levels of aggregation
            label_radios.append("input")
                       .attr("type", "radio")
                       .attr("id", "id")
                       .attr("value", function(d) { return d; })
                       .attr("name", "radio-nest")
                       .property("checked", true)
                       .on("change", function(d) {

                          visualization.params({
                            x_type: d
                          })
                          d3.select(vars.container).call(vars.this_chart)
                       });

            label_radios.append("span")
                .html(function(d) {
                  return d ;
                });

     }

     if(vars.ui.options) {

        var label_radios = d3.select(vars.container).selectAll(".aggregations_radio").data([vars.time.var_time, vars.var_group, vars.var_id])
          .enter()
            .append("label")
            .attr("class", "aggregations_radio")

        // TODO: find levels of aggregation
        label_radios.append("input")
                   .attr("type", "radio")
                   .attr("id", "id")
                   .attr("value", function(d) { return d; })
                   .attr("name", "radio-nest")
                   .property("checked", function(d) { return vars.aggregate === d; })
                   .on("change", function(d) {

                    if(d === vars.var_id) {

                      delete vars.set['__aggregated'];
                      vars.refresh = true;
                      d3.select(vars.container).call(vars.this_chart)

                    } else if(d === vars.var_group) {

                      vars.set['__aggregated'] = false;
                      vars.refresh = true;
                      d3.select(vars.container).call(vars.this_chart)

                    }

                   });

        label_radios.append("span")
            .html(function(d) {
              return d ;
            });

     }

      // Sorting option
      if(vars.ui.sort) {

        d3.select(vars.container).selectAll(".label_sort").data([vars.ui.sort])
          .enter()
            .append("span")
            .classed("label_sort", true)
            .html("<br>Sort by")

        var label_radios = d3.select(vars.container).selectAll(".sort_radio").data(vars.ui.sort)
          .enter()
            .append("label")
            .attr("class", "sort_radio")

        // TODO: find levels of aggregation
        label_radios.append("input")
                   .attr("type", "radio")
                   .attr("id", "id")
                   .attr("value", function(d) { return d; })
                   .attr("name", "radio-nest")
                   .property("checked", function(d) {
                      return d == vars.var_sort;
                   })
                   .on("click", function(d) {

                     if(vars.var_sort == d)
                       vars._user_vars.var_sort_asc = !vars._user_vars.var_sort_asc;

                      vars._user_vars.var_sort = d;

                      vars.refresh = true;

                      d3.select(vars.container).call(vars.this_chart);
                   });

        label_radios.append("span")
            .html(function(d) {
              return d ;
            });
      }

        d3.select(vars.container).selectAll(".label_highlight").data([vars.var_id])
          .enter()
            .append("span")
            .classed("label_highlight", true)
            .html("<br>Select/highlight");

      // Highlight
      var label_litems = d3.select(vars.container).selectAll(".items").data([vars.var_id])
        .enter()
          .append("label")
          .attr("class", "items");

      label_litems.append("select")
        .attr("id", "select_items")
        .style("width", vars.width/2)
        .on("change", function(d, i) {

          // Focus on a sepecifc item
          var id_focus = vars.new_data.map(function(d) {return d[vars.var_text]; }).indexOf(this.value);
          vars.this_chart.focus(1);

          d3.select(vars.container).call(vars.this_chart);

        })
        .selectAll("option")
        .data(vars.new_data)
      .enter()
        .append("option")
        .attr("value", function(d) { return d[vars.var_text]; })
        .html(function(d) { return d[vars.var_text]; });

      d3.select(vars.container).selectAll(".clearSelection").data([vars.var_id]).enter().append("button")
             .attr("type", "button")
             .attr("class", "clearSelection")
             .on("click", function() {

                vars.svg.selectAll(".selected").classed("selected", false);
                vars.selection = [];
                d3.select(vars.container).call(vars.this_chart);

              })
             .html("Clear selection");

      d3.select(vars.container).selectAll(".clearHighlight").data([vars.var_id]).enter().append("button")
             .attr("type", "button")
             .attr("class", "clearHighlight")
             .on("click", function() {

                vars.svg.selectAll(".highlighted").classed("highlighted", false);
                vars.highlight = [];
                d3.select(vars.container).call(vars.this_chart);

              })
             .html("Clear highlight");



      d3.select(vars.container).selectAll(".toggleLanguage").data(["toggleLanguage"]).enter().append("button")
               .attr("type", "button")
               .attr("class", "toggleLanguage")
               .on("click", function() {

                  // Then move groups to their grid position
                  // visualization.param("refresh", true);

                  var new_lang = vars.var_text == "name_en" ? "name_es" : "name_en";

                  var new_lang_param = vars.var_text == "name_en" ? "en_US" : "es_ES";

                  vars.this_chart.params({
                    var_text: new_lang,
                    lang: new_lang_param
                  });

                  // visualization.params().refresh = true;
                  // visualization.params().init = true;

                  d3.select(vars.container.call(vars.this_chart));

                  d3.select(this).html(function() {
                    return "Current language: " + vars.lang;
                  })

                })
               .html("Current language: " + vars.lang);

    }

    // Legend for product space
    if(vars.ui.legend) {

      var width = vars.width;
      var legend_offset = vars.width / 4;

      var nb_color = 3; // visualization.params().color.domain().length

      var items_mark_color = [vars.locales[vars.lang]['low'], "", vars.locales[vars.lang]['high']];
      var x_offset = legend_offset / nb_color;

      var legend =  d3.select(vars.container).selectAll(".svg_legend").data(["legend"]);

      legend.enter()
        .append("svg")
        .attr("class", "svg_legend")
        .attr("width", vars.width)
        .attr("height", 100)
        .append("g")
        .attr("transform", "translate(20, 0)")
        .attr("class", "legend_group")

      var legend_items_mark_text = legend.selectAll(".legend_items_mark_text")
          .data([vars.locales[vars.lang]['complexity']]);

      legend_items_mark_text.enter().append("g")
          .attr("class", "legend_items_mark_text")
          .attr("transform", function(d, i) { return "translate(" + (legend_offset / 2) + ", 12)"; })
          .append('text')
          .style("text-anchor", 'end')
          .attr("transform", "translate(-10, 0)");

      legend_items_mark_text.select('text').text(function(d) { return d; });

      var legend_items_mark_color = legend.selectAll(".legend_items_mark_color")
          .data(items_mark_color);

      var legend_items_mark_color_enter = legend_items_mark_color.enter().append("g")
          .attr("class", "legend_items_mark_color")
          .attr("transform", function(d, i) { return "translate(" + (legend_offset / 2 + i * x_offset) + ", 0)"; })
          .on('mouseover', function(_, i) {
            var interval = vars.color.domain()[1] - vars.color.domain()[0];
            if(i == 0) {
              vars.svg.selectAll('.items__mark__circle').filter(function(d) {
                return d[vars.var_color] > interval / 3;
              }).style('display', 'none');
            } else if(i == 1) {
              vars.svg.selectAll('.items__mark__circle').filter(function(d) {
                return (d[vars.var_color] <= interval / 3) || (d[vars.var_color] > 2 * interval / 3);
              }).style('display', 'none');
            } else {
              vars.svg.selectAll('.items__mark__circle').filter(function(d) {
                return d[vars.var_color] <= 2 * interval / 3;
              }).style('display', 'none');
            }
          })
          .on('mouseleave', function(d, i) {
            vars.svg.selectAll('.items__mark__circle').style('display', 'block');
          })

      legend_items_mark_color_enter.append("rect")
          .attr("x", 0)
          .attr("width", x_offset)
          .attr("height", 18)
          .style("fill", function(d, i) {
            if(i === 0) {
              return vars.color(vars.color.domain()[0])
            } else if(i === 1) {
              return vars.color((vars.color.domain()[1] - vars.color.domain()[0]) / 2);
            } else {
              return vars.color(vars.color.domain()[1]);
            }

          });

      legend_items_mark_color_enter.append("text")
          .attr("x", 5)
          .attr("y", 9)
          .attr("dy", ".35em")
          .style("text-anchor", "start");

      legend_items_mark_color.select('text').text(function(d) { return d; });

      // Item marks and different stylings
      // Export / Non-export
      var data_items_mark = [vars.locales[vars.lang]['export'], vars.locales[vars.lang]['non-export']];
      x_offset = legend_offset / nb_color;

      var legend_items_mark = legend.selectAll(".legend_items_mark")
          .data(data_items_mark);

      var legend_items_mark_enter = legend_items_mark.enter().append("g")
          .attr("class", "legend_items_mark")
          .attr("transform", function(d, i) { return "translate(" + (1.75 * legend_offset + i * x_offset * 1.5) + ", 0)"; })
          .on('mouseover', function(d, i) {
            if(i == 0) {
              vars.svg.selectAll('.items__mark__circle').filter(function(d) {
                return d['export_rca'] <= 1;
              }).style('display', 'none');
            } else {
              vars.svg.selectAll('.items__mark__circle').filter(function(d) {
                return d['export_rca'] > 1;
              }).style('display', 'none');
            }
          })
          .on('mouseleave', function(d, i) {
            vars.svg.selectAll('.items__mark__circle').style('display', 'block');
          })

      legend_items_mark_enter.append("circle")
          .attr("cx", 10)
          .attr("cy", 10)
          .attr("r", 8)
          .attr("class", "items__mark__circle")
          .style("fill", function(d, i) { return vars.color(0); })
          .classed("selected", function(d, i) {
            return i == 0;
          })
          .style("stroke-width", "5");

      legend_items_mark_enter.append("text")
          .attr("x", 25)
          .attr("y", 9)
          .attr("dy", ".35em")
          .style("text-anchor", "start");

      legend_items_mark.select('text').text(function(d) { return d;});

      // Connect marks and different stylings
      var connect_mark = [vars.locales[vars.lang]['similarity_link']];

      var width = 100;
      x_offset = legend_offset / vars.color.domain().length;

      var legend_connect_mark = legend.selectAll(".legend_connect_mark")
          .data(connect_mark);

      var legend_connect_mark_enter = legend_connect_mark.enter().append("g")
          .attr("class", "legend_connect_mark")
          .attr("transform", function(d, i) { return "translate(" + (3 * legend_offset + i * x_offset) + ", 0)"; })
          .on('mouseover', function() {
            vars.svg.selectAll('.mark__group > circle').style('display', 'none');
          })
          .on('mouseleave', function() {
            vars.svg.selectAll('.mark__group > circle').style('display', 'block');
          })

      legend_connect_mark_enter.append("line")
          .attr("x1", 0)
          .attr("x2", 20)
          .attr("y1", 20)
          .attr("y2", 0)
          .attr("class", "connect__line")
          .style("stroke-width", "4");

      legend_connect_mark_enter.append("text")
          .attr("x", 20)
          .attr("y", 9)
          .attr("dy", ".35em")
          .style("text-anchor", "start");

      legend_connect_mark.text(function(d) { return d;});

    }

  });


    vars.evt.call('finish', null);
}


  chart.set = function(attr, concat) {
    vars.set[attr] = concat;
    return chart;
  };

  chart.params = function(x) {
    if(!arguments.length) return vars;
    vars._user_vars = x;
    return chart;
  };

  chart.param = function(attr, value) {
    if(arguments.length < 2) return vars["attr"];
    vars[attr] = value;
    return chart;
  };

  chart.container = function(x) {
    if(!arguments.length) return vars.container;
    vars.container = x;
    return chart;
  };


  setTimeout(function() {

    vars.evt.register("highlightOn", function(d) {

      // POST-RENDERING STUFF
      // Usually aimed at updating the rendering order of elements
      vars.z_index.forEach(function(d) {

        // Filter events
        if(vars.type === d.type && d.event === 'highlightOn') {

          vars.svg.selectAll(d.selector)
            .filter(function(e) {
              if(typeof d.attribute !== 'undefined') {
                return e[d.attribute];
              } else {
                return true;
              }
            })
            .each(function() {
              this.parentNode.appendChild(this);
            });
        }

      });

      d3.select(vars.container).call(vars.this_chart);

    });

    vars.evt.register("highlightOut", function(d) {

      if(vars.type !== "productspace") {
        d3.select(vars.container).call(vars.this_chart);
      }

      vars.z_index.forEach(function(d) {

        // Filter events
        if(vars.type === d.type && d.event === 'highlightOut') {

          vars.svg.selectAll(d.selector)
            .filter(function(e) {
              if(typeof d.attribute !== 'undefined') {
                return e[d.attribute];
              } else {
                return true;
              }
            })
            .each(function() {
              this.parentNode.appendChild(this);
            });
        }

      });

    });

  }, 100);

  vars.this_chart = chart;

  return chart;
}


// PUBLIC FUNCTIONS

// http://stackoverflow.com/questions/171251/how-can-i-merge-properties-of-two-javascript-objects-dynamically
vistk.utils.merge = function(d, e) {

  var obj = {},
      i = 0,
      il = arguments.length,
      key;
  for (; i < il; i++) {
      for (key in arguments[i]) {
          if (arguments[i].hasOwnProperty(key)) {
              obj[key] = arguments[i][key];
          }
      }
  }
  return obj;
};

// TODO: add accessor as argument and var_time
vistk.utils.flatten_years = function(data) {
  var flat = [];

  //for each country
  data.forEach(function(root) {

      //for each year in each country
      root.years.forEach(function(year) {
          //extend the year object with the common properties stored just once in the country object

        var current_year = vistk.utils.merge(root, year);
        delete current_year.years;

          //add it to the final flat array
          flat.push(current_year);
      })
  });

  return flat;
}

vistk.utils.find_node_by_id = function(nodes, id) {
  var res = nodes.filter(function(d) {
    return d.id == id;
  })[0];

  return res;
}

vistk.utils.find_node_coordinates_by_id = function(nodes, var_id, data_id) {

  var res = nodes.filter(function(node) {
    return node[var_id] == data_id;
  })[0];

  return res;
}

vistk.utils.max = function(data) {
  var var_time = this.var_time;
  return d3.max(data, function(d) { return d[var_time] });
}

vistk.utils.min = function(data) {
  var var_time = this.var_time;
  return d3.min(data, function(d) { return d[var_time] });
}

vistk.utils.time = {};

vistk.utils.time.current = function(data) {
  return vars.current_time;
}

vistk.utils.decode_url = function() {

  // Variables from query string
  var queryParameters = {}, queryString = location.search.substring(1),
      re = /([^&=]+)=([^&]*)/g, m, queryActivated = false;

  // Creates a map with the query string parameters
  while (m = re.exec(queryString)) {
    queryParameters[decodeURIComponent(m[1])] = decodeURIComponent(m[2]);
  }

  return queryParameters;
}

// Credits: http://bl.ocks.org/mbostock/1705868
vistk.utils.translate_along = function(path) {
  var l = path.node().getTotalLength();
  return function(d, i, a) {
    return function(t) {
      var p = path.node().getPointAtLength(t * l);
      return "translate(" + p.x + "," + p.y + ")";
    };
  };
}

vistk.utils.find_unique_values = function(data, key) {

  var unique = {};
  var result = [];

  for(var i in data){
    if(typeof(unique[data[i][key]]) == "undefined"){
      result.push(data[i][key]);
    }
    unique[data[i][key]] = 0;
  }

  return result;

}

vistk.utils.list = function(param) {
  return list[param];
}

vistk.utils.scale = {};

vistk.utils.scale.linear = function(vars) {

  return [{
    func: d3.scale.linear()
            .range([vars.margin.left, vars.width - vars.margin.left - vars.margin.right])
            .domain([vars.margin.left, vars.width - vars.margin.left - vars.margin.right])
  }];

};

