toolTips = [];
if($("body").attr("id") != "about"){
	$.ajax({
	  url: "/about/glossary/",
	  cache: false
	})

	.done(function( html ) { // creates array containing first sentences 

		var text = $("dl dd");

		text.each(function(){

			var elem = $(this);

			var textParts = elem.html().split("."); // Breaks text at period and puts groups into array

			var first = textParts.shift(); // removes and returns first element of said array

			toolTips.push(first); // pushes said element to toolTips[]
		})

	});
}

else{

	var text = $("dl dd");

	text.each(function(){

		var elem = $(this);

		var textParts = elem.html().split("."); // Breaks text at period and puts groups into array

		var first = textParts.shift(); // removes and returns first element of said array

		toolTips.push(first); // pushes said element to toolTips[]
	})	
}

var replace = {
	"Capability Distance": "<span class='gTerm'title='Measures a country’s ability to make a specific product based upon its current export basket and productive capabilities.' toolTip='2'>Capability Distance</span>",
	"Diversity": "<span class='gTerm'title='Measures how many different types of products a country is able to make.' toolTip='2'>Diversity</span>",
	"Economic Complexity": "<span class='gTerm'title='A measure of the knowledge in a society that gets translated into the products it makes.' toolTip='2'>Economic Complexity</span>",
	"Economic Complexity Indicator": "<span class='gTerm'title='ECI is a scale that shows which countries are economically complex and which are not.' toolTip='2'>Economic Complexity Indicator</span>",	
	"Expected Growth": "<span class='gTerm'title='Predicts the degree to which a country will grow dependent upon its current level of Economic Complexity, its location within The Product Space, as well as current GDP.' toolTip='2'>Expected Growth</span>",	
	"Nearby (adjacent possible)": "<span class='gTerm'title='Describes a product that requires similar productive capabilities to another product.' toolTip='2'>Nearby (adjacent possible)</span>",
	"Productive Knowlege": "<span class='gTerm'title='A form of knowledge or know-how to produce things.' toolTip='2'>Productive Knowlege</span>",
	"Product Complexity Index": "<span class='gTerm'title='A measure of how complex a product is, calculated as the mathematical limit of a measure based on how many countries export the product and how diversified those exporters are.' toolTip='2'>Product Complexity Index</span>",
	"The Product Space": "<span class='gTerm'title='A map that depicts the network of possible export products, and shows paths through which productive knowledge is more easily accumulated.' toolTip='2'>The Product Space</span>",
	"Proximity": "<span class='gTerm'title='A characteristic of a pair of products, showing how close the products are located to one another within the Product Space.' toolTip='2'>Proximity</span>"

}

for(var key in replace){

	var s = $("#main").html();

	var re = new RegExp(key,"gi");

	var result = s.replace(re, replace[key]);

	$("#main").html(result);

}

$("*").mouseover(function(){
	if($(this).attr("toolTip")){
		$(this).attr("title", toolTips[$(this).attr("toolTip")]);
	}
});

$("*").mouseleave(function(){
	if($(this).attr("toolTip")){
		console.log(toolTips[$(this).attr("toolTip")]);
	}			
});


 

