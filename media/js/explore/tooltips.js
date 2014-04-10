toolTips = [];

$.ajax({
  url: "/about/glossary/",
  cache: false
})

.done(function( html ) {

	var text = $("dl dd");

	text.each(function(){

		var elem = $(this);

		var textParts = elem.html().split("."); // Breaks text at period and puts groups into array

		var first = textParts.shift(); // removes and returns first element of said array

		toolTips.push(first); // pushes said element to toolTips[]
	})

});

// var newstr = str.replace("what", "<span title=' ' toolTip='2'>what</span>", "gi");
// $('body').html(newstr);

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


 

