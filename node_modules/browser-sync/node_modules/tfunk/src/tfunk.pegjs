start
  = body

body
  = p:item*

item
  = tag / buffer / reset

buffer "buffer"
  = e:eol w:ws*
  { return {"buffer": e + w.join('')} }
  / b:(!tag !reset c:. { return c })+
  { return {"buffer": b.join('')} }

tag
  = ld c:color ":" e:(!ld !rd b:. {return b})+ { return {color: c, text: e.join('')}}

color
  = c:[a-zA-Z\.]+ { return c.join('') }

reset
  = rd e:after? {return {reset: true, text: e ? e.join('') : '' }}

after
  = (!ld !rd after:. {return after})+

ld
  = "{"

rd
  = "}"

eol
  = "\n"        //line feed
  / "\r\n"      //carriage + line feed
  / "\r"        //carriage return
  / "\u2028"    //line separator
  / "\u2029"    //paragraph separator

ws
  = [\t\v\f \u00A0\uFEFF] / eol