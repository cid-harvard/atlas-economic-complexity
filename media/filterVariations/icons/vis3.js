var country_list = ["Afghanistan","Albania","Algeria","Andorra","Angola","Anguilla","Antigua &amp; Barbuda","Argentina","Armenia","Aruba","Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bermuda","Bhutan","Bolivia","Bosnia &amp; Herzegovina","Botswana","Brazil","British Virgin Islands","Brunei","Bulgaria","Burkina Faso","Burundi","Cambodia","Cameroon","Cape Verde","Cayman Islands","Chad","Chile","China","Colombia","Congo","Cook Islands","Costa Rica","Cote D Ivoire","Croatia","Cruise Ship","Cuba","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Estonia","Ethiopia","Falkland Islands","Faroe Islands","Fiji","Finland","France","French Polynesia","French West Indies","Gabon","Gambia","Georgia","Germany","Ghana","Gibraltar","Greece","Greenland","Grenada","Guam","Guatemala","Guernsey","Guinea","Guinea Bissau","Guyana","Haiti","Honduras","Hong Kong","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Isle of Man","Israel","Italy","Jamaica","Japan","Jersey","Jordan","Kazakhstan","Kenya","Kuwait","Kyrgyz Republic","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Macau","Macedonia","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Mauritania","Mauritius","Mexico","Moldova","Monaco","Mongolia","Montenegro","Montserrat","Morocco","Mozambique","Namibia","Nepal","Netherlands","Netherlands Antilles","New Caledonia","New Zealand","Nicaragua","Niger","Nigeria","Norway","Oman","Pakistan","Palestine","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Puerto Rico","Qatar","Reunion","Romania","Russia","Rwanda","Saint Pierre &amp; Miquelon","Samoa","San Marino","Satellite","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","South Africa","South Korea","Spain","Sri Lanka","St Kitts &amp; Nevis","St Lucia","St Vincent","St. Lucia","Sudan","Suriname","Swaziland","Sweden","Switzerland","Syria","Taiwan","Tajikistan","Tanzania","Thailand","Timor L'Este","Togo","Tonga","Trinidad &amp; Tobago","Tunisia","Turkey","Turkmenistan","Turks &amp; Caicos","Uganda","Ukraine","United Arab Emirates","United Kingdom","United States","Uruguay","Uzbekistan","Venezuela","Vietnam","Virgin Islands (US)","Yemen","Zambia","Zimbabwe"];

d3.select("#countrySelect").selectAll("option").data(country_list).enter().append("option").attr("class", "country").html(function(d){return d});


 
  // sample data array
  var SITC = [
    {"value": 3, "name": "Food/Live Animals for Food", "icon": "foundation/img/community_0.png", "color":"#ffe999"},
    {"value": 0.46, "name": "Drinks and Tobacco", "icon": "foundation/img/community_10.png", "color":"#6e451e"},
    {"value": 17, "name": "Crude Materials, Inedible, exc. Fuels", "icon": "foundation/img/community_18.png", "color":"#d66011"}                                
  ]

 
  // instantiate d3plus
  var visualization = d3plus.viz()
    .container("#vis")  // container DIV to hold the visualization
    .data(SITC)  // data to use with the visualization
    .type("tree_map")   // visualization type
    .id("name")         // key for which our data is unique on
    .text("name")       // key to use for display text
    .size("value")      // sizing of blocks
    .icon("icon")
    .color("color")
    .draw()             // finally, draw the visualization!

$(document).ready(function(){
	var resized = false;
	$(window).resize(function(){
		if(window.innerWidth <= 1281 && resized == false){
			d3.select("#d3plus").remove();
			$("#vis").css("width", "100%");
			var visualization = d3plus.viz()
		    .container("#vis")  // container DIV to hold the visualization
		    .data(SITC)  // data to use with the visualization
		    .type("tree_map")   // visualization type
		    .id("name")         // key for which our data is unique on
		    .text("name") 
		    .html("value")      // key to use for display text
		    .size("value")      // sizing of blocks
		    .icon("icon")
		    .color("color")
		    .draw()                // finally, draw the visualization!
		    resized = true;

		} else if(window.innerWidth >= 1279 && resized == true){
			d3.select("#d3plus").remove();
			$("#vis").css("width", "100%");
			var visualization = d3plus.viz()
		    .container("#vis")  // container DIV to hold the visualization
		    .data(SITC)  // data to use with the visualization
		    .type("tree_map")   // visualization type
		    .id("name")         // key for which our data is unique on
		    .text("name")       // key to use for display text
		    .html("value")
		    .size("value")      // sizing of blocks
		    .icon("icon")
		    .color("color")
		    .draw()                // finally, draw the visualization!
		    resized = false;
		}
	});
});




