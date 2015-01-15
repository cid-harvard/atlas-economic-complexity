
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

// Function to read query parameters
function getQueryParameterByName(name) {
    var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
    return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
}

function is_in_iframe() {
  try {
      return window.self !== window.top;
  } catch (e) {
      return true;
  }
}

function update_url(a, b, c) {
  if(!in_iframe)
    window.history.pushState(a, b, c);
  else
    console.log(a,b,c, myIframe.contentWindow)
}
