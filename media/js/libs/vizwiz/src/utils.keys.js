function Key() {
  
  var prefix = 1
      
  function util(selection) {
    
    selection.each(function(data) {
      
      var key = this,
          margin = 2,
          spacing = 5,
          popup = Popup(),
          max_size = 36,
          cats = d3.values(data).filter(function(d){return d.id.length == prefix})
          
      cats.sort(function(a, b){
        if (a.attr_type == "munic" || a.attr_type == "country") {
          var a_name = a.name
          var b_name = b.name
        } else {
          var a_name = d3.rgb(a.color).hsl().h
          var b_name = d3.rgb(b.color).hsl().h
          if (d3.rgb(a.color).hsl().s == 0) a_name = 361
          if (d3.rgb(b.color).hsl().s == 0) b_name = 361
        }
        if(a_name < b_name) return -1;
        if(a_name > b_name) return 1;
        return 0;
      })
  
      key.style.padding = spacing+'px 0px '+margin+'px '+spacing+'px'
  
      var area = window.innerWidth-10
      var key_width = (cats.length*(size+(margin*2)+spacing))+spacing
      var size = parseInt((area/cats.length)-spacing-(margin*2))
      if (size > max_size) size = max_size
 
      key.style.marginLeft = '-'+(key_width/2)+'px'
      
      cats.forEach(function(d,i){
        var cat = document.createElement('div')
        cat.setAttribute('id','key_'+i)
        cat.style.width = size+(margin*2)+spacing+"px"
        key.appendChild(cat)
    
        var link = document.createElement('a')
        if (d.attr_type != 'country') {
          link.style.backgroundImage = 'url("/media/img/icons/'+d.attr_type+'/'+d.attr_type+'_'+d.id+'.png")'
        }
        link.style.backgroundColor = d.color
        link.style.backgroundSize = size+'px'
        link.style.width = size+'px'
        link.style.height = size+'px'
        link.style.margin = margin+'px '+(margin+spacing)+'px '+margin+'px '+margin+'px'
        cat.appendChild(link)
    
        cat.addEventListener(click_event,function(e){
          if(app.deselected) {
            var div = document.getElementById("key_"+i)
            if(div.firstChild.style.backgroundColor == "rgb(230,230,230)"){
              div.firstChild.style.backgroundColor = d.color;
              if(app.highlight) d3.select('#app').call(app.highlight(d.id))
            }
            else {
              div.firstChild.style.backgroundColor = "rgb(230,230,230)";
              if(app.highlight) d3.select('#app').call(app.highlight())
            }
            d3.select('#app').call(app.deselected(d.id))
          }
        })

        cat.addEventListener(over_event,function(e){
        
          var p = document.createElement('div')
          p.id = 'key_popup'
          key.parentNode.parentNode.appendChild(p)
          
          var x_pos = this.offsetLeft+(this.offsetWidth/2)-(margin*1.5)
          var y_pos = window.innerHeight-key.parentNode.offsetHeight+key.offsetTop+this.offsetTop
          d3.select('div#key_popup')
            .datum({'key': d.name.toTitleCase()})
            .call(popup)
            
          popup.position(x_pos,y_pos)

          if(app.highlight) d3.select('#app').call(app.highlight(d.id))
          
        })
    
        cat.addEventListener(out_event,function(e){
          d3.select('div#key_popup').remove()
          if(app.highlight) d3.select('#app').call(app.highlight())
        })
      })
      
    })
  }
  
  util.prefix = function(value) {
    prefix = value
    return util
  }
  
  return util
}