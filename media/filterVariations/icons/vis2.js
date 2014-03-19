var country_list = ["Afghanistan","Albania","Algeria","Andorra","Angola","Anguilla","Antigua &amp; Barbuda","Argentina","Armenia","Aruba","Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bermuda","Bhutan","Bolivia","Bosnia &amp; Herzegovina","Botswana","Brazil","British Virgin Islands","Brunei","Bulgaria","Burkina Faso","Burundi","Cambodia","Cameroon","Cape Verde","Cayman Islands","Chad","Chile","China","Colombia","Congo","Cook Islands","Costa Rica","Cote D Ivoire","Croatia","Cruise Ship","Cuba","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Estonia","Ethiopia","Falkland Islands","Faroe Islands","Fiji","Finland","France","French Polynesia","French West Indies","Gabon","Gambia","Georgia","Germany","Ghana","Gibraltar","Greece","Greenland","Grenada","Guam","Guatemala","Guernsey","Guinea","Guinea Bissau","Guyana","Haiti","Honduras","Hong Kong","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Isle of Man","Israel","Italy","Jamaica","Japan","Jersey","Jordan","Kazakhstan","Kenya","Kuwait","Kyrgyz Republic","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Macau","Macedonia","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Mauritania","Mauritius","Mexico","Moldova","Monaco","Mongolia","Montenegro","Montserrat","Morocco","Mozambique","Namibia","Nepal","Netherlands","Netherlands Antilles","New Caledonia","New Zealand","Nicaragua","Niger","Nigeria","Norway","Oman","Pakistan","Palestine","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Puerto Rico","Qatar","Reunion","Romania","Russia","Rwanda","Saint Pierre &amp; Miquelon","Samoa","San Marino","Satellite","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","South Africa","South Korea","Spain","Sri Lanka","St Kitts &amp; Nevis","St Lucia","St Vincent","St. Lucia","Sudan","Suriname","Swaziland","Sweden","Switzerland","Syria","Taiwan","Tajikistan","Tanzania","Thailand","Timor L'Este","Togo","Tonga","Trinidad &amp; Tobago","Tunisia","Turkey","Turkmenistan","Turks &amp; Caicos","Uganda","Ukraine","United Arab Emirates","United Kingdom","United States","Uruguay","Uzbekistan","Venezuela","Vietnam","Virgin Islands (US)","Yemen","Zambia","Zimbabwe"];

d3.select("#countrySelect").selectAll("option").data(country_list).enter().append("option").attr("class", "country").html(function(d){return d});


 
  // sample data array
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
    {"value":0.6,"name":"Commodities and Transactions Unclassified Elsewhere in SITC", "icon": "foundation/img/community_qm.png", "color":"#9c9a87"},
    {"value":0.5 ,"name":"Computers", "icon":"foundation/img/community_2.png", "color":"#ddd"},
    {"value":2 ,"name":"Airplanes", "icon":"foundation/img/community_3.png", "color":"##4169E1"},
    {"value":0.5 ,"name":"Energy Resources", "icon":"foundation/img/community_4.png", "color":"#87CEFA"},
    {"value":9 ,"name":"Marine Utilities", "icon":"foundation/img/community_5.png", "color":"#000080"},
    {"value":3 ,"name":"Metalworking Materials", "icon":"foundation/img/community_6.png", "color":"#6495ED"},
    {"value":10 ,"name":"Fine China and Kitchenware", "icon":"foundation/img/community_8.png", "color":"#FF6A6A"},
    {"value":1 ,"name":"Outdoor Plants and Seeds", "icon":"foundation/img/community_9.png", "color":"#FF6103"},
    {"value":15 ,"name":"Canned Food Products", "icon":"foundation/img/community_11.png", "color":"#CD8500"},
    {"value":12 ,"name":"Water Purification Utilities", "icon":"foundation/img/community_12.png", "color":"#CD69C9"},
    {"value":7 ,"name":"Structual Products", "icon":"foundation/img/community_13.png", "color":"#FF82AB"}                                    
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




