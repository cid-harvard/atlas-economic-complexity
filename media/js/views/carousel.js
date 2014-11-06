// GLOBALS
// =============================================
var CONFIG = {
	mainExample: $('.example-main'),
	subExamples: $('.example-sub'),
	exampleCounter: 0,
	carouselLen: $('.example-sub').length,
	carouselTimer: 0,
	carouselInterval: 5000
};

updateCarousel();
startCarousel();


// HELPERS
// =============================================

// Only runs on page load
function startCarousel() {
	// Don't start the carousel if the main example mod is hidden
	if ( CONFIG.mainExample.css('display') !== 'block' ) {
		addExampleImg();
		return;
	}
	CONFIG.carouselTimer = setInterval(advanceCarousel, CONFIG.carouselInterval);
}

function advanceCarousel() {
	// End the carousel if the main example mod is hidden
	if ( CONFIG.mainExample.css('display') !== 'block' ) {
		clearInterval(CONFIG.carouselTimer);
	}
	if (CONFIG.exampleCounter === CONFIG.carouselLen - 1) {
		CONFIG.exampleCounter = 0;
	} else {
		CONFIG.exampleCounter += 1;
	}

	updateCarousel();
}

function updateCarousel() {
	// Give the new tease the active class
	setActiveTease();

	// Swap the main img to the hovered tease
	setMain();
}

function setActiveTease() {
	CONFIG.subExamples.addClass('example-inactive').removeClass('example-active');
	CONFIG.subExamples.eq(CONFIG.exampleCounter).addClass('example-active');
}

function setMain() {
	var $newTease = CONFIG.subExamples.eq(CONFIG.exampleCounter);

	// Switch src of main img
	CONFIG.mainExample.find('.example-img-wrap').css('background-image', 'url(' + $newTease.data('img-src') + ')');

	// Switch caption of main img
	var $newCaption = CONFIG.mainExample.find('.example-caption-wrap').html($newTease.find('.example-caption-wrap').html());

	// Set product label, this should probably be templated - GW
	$newCaption.find('.example-link').prepend("<p class='example-slug label'>" + $newTease.data('graph-type') + "</p>");
}

function restartTimer() {
	clearInterval(CONFIG.carouselTimer);
	startCarousel();
}

function addExampleImg() {
	
}


// HANDLERS
// =============================================

CONFIG.subExamples.on({
	mouseenter: function() {
		var $this = $(this);
		var newIndex = CONFIG.subExamples.index($(this));
		CONFIG.exampleCounter = newIndex;

		updateCarousel();

		// Restart carousel timer
		restartTimer();
	},
	mouseleave: function() {
		CONFIG.subExamples.addClass('example-inactive').removeClass('example-active');
		CONFIG.subExamples.eq(CONFIG.exampleCounter).addClass('example-active');
	}
});


// WINDOW RESIZE
// =============================================

var lazyLayout = _.debounce(function() {
	if ( CONFIG.mainExample.css('display') === 'block' ) {
		restartTimer();
	}
}, 100);

$(window).resize(lazyLayout);