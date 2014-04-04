var country_list = ["Afghanistan","Albania","Algeria","Andorra","Angola","Anguilla","Antigua &amp; Barbuda","Argentina","Armenia","Aruba","Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bermuda","Bhutan","Bolivia","Bosnia &amp; Herzegovina","Botswana","Brazil","British Virgin Islands","Brunei","Bulgaria","Burkina Faso","Burundi","Cambodia","Cameroon","Cape Verde","Cayman Islands","Chad","Chile","China","Colombia","Congo","Cook Islands","Costa Rica","Cote D Ivoire","Croatia","Cruise Ship","Cuba","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Estonia","Ethiopia","Falkland Islands","Faroe Islands","Fiji","Finland","France","French Polynesia","French West Indies","Gabon","Gambia","Georgia","Germany","Ghana","Gibraltar","Greece","Greenland","Grenada","Guam","Guatemala","Guernsey","Guinea","Guinea Bissau","Guyana","Haiti","Honduras","Hong Kong","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Isle of Man","Israel","Italy","Jamaica","Japan","Jersey","Jordan","Kazakhstan","Kenya","Kuwait","Kyrgyz Republic","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Macau","Macedonia","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Mauritania","Mauritius","Mexico","Moldova","Monaco","Mongolia","Montenegro","Montserrat","Morocco","Mozambique","Namibia","Nepal","Netherlands","Netherlands Antilles","New Caledonia","New Zealand","Nicaragua","Niger","Nigeria","Norway","Oman","Pakistan","Palestine","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Puerto Rico","Qatar","Reunion","Romania","Russia","Rwanda","Saint Pierre &amp; Miquelon","Samoa","San Marino","Satellite","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","South Africa","South Korea","Spain","Sri Lanka","St Kitts &amp; Nevis","St Lucia","St Vincent","St. Lucia","Sudan","Suriname","Swaziland","Sweden","Switzerland","Syria","Taiwan","Tajikistan","Tanzania","Thailand","Timor L'Este","Togo","Tonga","Trinidad &amp; Tobago","Tunisia","Turkey","Turkmenistan","Turks &amp; Caicos","Uganda","Ukraine","United Arab Emirates","United Kingdom","United States","Uruguay","Uzbekistan","Venezuela","Vietnam","Virgin Islands (US)","Yemen","Zambia","Zimbabwe"];

d3.select("#countrySelect").selectAll("option").data(country_list).enter().append("option").attr("class", "country").html(function(d){return "<img class='listIcon' src='foundation/img/community_0.png'/>"+ "<p class='listItem'>" + d +"</p>"});

// Data Array for SITC Product Class
var SITC = [
	{"value": 3, "name": "Food/Live Animals for Food", "icon": "foundation/img/community_0.png", "color":"#ffe999"},
	{"value": 0.46, "name": "Drinks and Tobacco", "icon": "foundation/img/community_10.png", "color":"#6e451e"},
	{"value": 17, "name": "Crude Materials, Inedible, exc. Fuels", "icon": "foundation/img/community_18.png", "color":"#d66011"},
	{"value": 16, "name": "Mineral Fuels, Lubricants, and Related Materials", "icon": "foundation/img/community_19.png", "color":"#330000"},
	{"value": 0.02, "name": "Animal and Vegetable Oils, Fats, and Waxes", "icon": "foundation/img/community_24.png", "color":"#ffc41c"},
	{"value": 0.55, "name": "Chemicals and Related Products", "icon": "foundation/img/community_14.png", "color":"#71144b"},
	{"value": 23,"name": "Manufactured Goods Classified Chiefly by Material", "icon": "foundation/img/community_7.png", "color":"#ff0000"},
	{"value": 6, "name": "Machinery and Transport Equipment", "icon": "foundation/img/community_car.png", "color":"#9edae5"},
	{"value":33, "name": "Misc. Manufactured Articles", "icon": "foundation/img/community_1.png", "color":"#5493c9"},
	{"value":0.6,"name":"Commodities and Transactions Unclassified Elsewhere in SITC", "icon": "foundation/img/community_qm.png", "color":"#9c9a87"}                                  
]
 

  var visualization = d3plus.viz()
    .container("#vis") 
    .data(SITC) 
    .type("tree_map")  
    .id("name")         
    .text("name")       
    .size("value")      
    .icon("icon")
    .color("color")
    .draw();	
   d3.select("#bg").attr("fill","none");
   d3.select("svg g#container").attr("fill","#fff");
// Resize Functions 
$(document).ready(function(){
	$(".ui-rangeSlider .ui-rangeSlider-handle").html("year");
	var resized = false;
	var tablet = false;
	$(window).resize(function(){
		if(window.innerWidth <= 1281 && resized == false){
			d3.select("#d3plus").remove();
			$("#vis").css("width", "100%");
			var visualization = d3plus.viz()
		    .container("#vis")  
		    .data(SITC)  
		    .type("tree_map")   
		    .id("name")         
		    .text("name") 
		    .html("value")      
		    .size("value")      
		    .icon("icon")
		    .color("color")
		    .draw()     
		       d3.select("#bg").attr("fill","none")           
		    resized = true;
			d3.select("#countrySelect").selectAll("option").data(country_list).enter().append("option").attr("class", "country").html(function(d){return d});
		} 
		else if(window.innerWidth >= 1279 && resized == true){
			d3.select("#d3plus").remove();
			$("#vis").css("width", "100%");
			var visualization = d3plus.viz()
		    .container("#vis")  
		    .data(SITC)  
		    .type("tree_map")   
		    .id("name")         
		    .text("name")       
		    .html("value")
		    .size("value")      
		    .icon("icon")
		    .color("color")
		    .draw()         
		       d3.select("#bg").attr("fill","none")       
		    resized = false;
		    d3.select("#countrySelect").selectAll("option").data(country_list).enter().append("option").attr("class", "country").html(function(d){return d});
		}
		if(window.innerWidth <= 1025 && tablet == false){
			d3.select("#d3plus").remove();
			$("#vis").css("width", 768);
			var visualization = d3plus.viz()
		    .container("#vis")  
		    .data(SITC)  
		    .type("tree_map")   
		    .id("name")         
		    .text("name") 
		    .html("value")      
		    .size("value")      
		    .icon("icon")
		    .color("color")
		    .draw()    
		       d3.select("#bg").attr("fill","none")            
		    tablet = true;
			d3.select("#countrySelect").selectAll("option").data(country_list).enter().append("option").attr("class", "country").html(function(d){return d});
		} 
		else if(window.innerWidth > 1024 && tablet == true){
			d3.select("#d3plus").remove();
			$("#vis").css("width", "100%");
			var visualization = d3plus.viz()
		    .container("#vis")  
		    .data(SITC)  
		    .type("tree_map")   
		    .id("name")         
		    .text("name")       
		    .html("value")
		    .size("value")      
		    .icon("icon")
		    .color("color")
		    .draw()     
		       d3.select("#bg").attr("fill","none")           
		    tablet = false;
		    d3.select("#countrySelect").selectAll("option").data(country_list).enter().append("option").attr("class", "country").html(function(d){return d});
		}
	});
});

var years = [];

for(i=1995; i<=2010; i++){
	years.push(i);
}

var left = [];

for(i=0; i < years.length; i++){
	left.push(i);
}

var svg = d3.select(".ui-rangeSlider-innerBar").append("svg");

var blockWidth = 653/left.length;

var ticks = svg.selectAll("text")
	.data(left).enter()
	.append("text")
	.html("year")
	.attr("width", blockWidth)
	.attr("height", 16)
	.attr("fill", "#fff")
	.style("font-size", 12)
	.attr("x", function(d){return (blockWidth*d)+10;})
	.attr("y", 12);






