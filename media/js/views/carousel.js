// GLOBALS
// =============================================
var CONFIG = {
	mainExample: $(".example-main"),
	subExamples: $(".example-sub"),
	exampleCounter: 0
};


// HELPERS
// =============================================

function showCorrect($item) {
	$item.find(".example-expander").show().css("height", "auto");
}



// HANDLERS
// =============================================

CONFIG.subExamples.on({
	mouseenter: function() {
		CONFIG.subExamples.addClass("example-inactive").removeClass("example-active");
		$(this).addClass("example-active");
	},
	mouseleave: function() {
		CONFIG.subExamples.addClass("example-inactive").removeClass("example-active");
		CONFIG.subExamples.eq(CONFIG.exampleCounter).addClass("example-active");
	}
});

CONFIG.subExamples.on("click", function() {
	var newIndex = CONFIG.subExamples.index($(this));
	CONFIG.exampleCounter = newIndex;
	console.log(newIndex);

	// if ($item.hasClass("example-expanded")) {
	// 	CONFIG.trueSelect = $item;
	// 	$item.addClass("example-expanded").addClass("example-active");
	// 	showCorrect($item);
	// 	setHeight($item);
	// }
});




// PSEUDOCODE
// 