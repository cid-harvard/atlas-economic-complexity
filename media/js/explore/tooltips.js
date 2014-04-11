toolTips = [];

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

var replace = {
	"Capability Distance": "<span title='0 void' toolTip='2'>Capability Distance</span>",
	"Diversity": "<span title='0 void' toolTip='2'>Diversity</span>",
	"Economic Complexity": "<span title='0 void' toolTip='2'>Economic Complexity</span>",
	"Economic Complexity Indicator": "<span title='0 void' toolTip='2'>Economic Complexity Indicator</span>",	
	"Expected Growth": "<span title='0 void' toolTip='2'>Expected Growth</span>",	
	"Nearby (adjacent possible)": "<span title='0 void' toolTip='2'>Nearby (adjacent possible)</span>",
	"Productive Knowlege": "<span title='0 void' toolTip='2'>Productive Knowlege</span>",
	"Product Complexity": "<span title='0 void' toolTip='2'>Product Complexity</span>",
	"Product Complexity Index": "<span title='0 void' toolTip='2'>Product Complexity Index</span>",
	"The Product Space": "<span title='0 void' toolTip='2'>The Product Space</span>",
	"Proximity": "<span title='0 void' toolTip='2'>Proximity</span>"

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


 

