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

startCarousel();


// HELPERS
// =============================================

// Only runs on page load
function startCarousel() {
	CONFIG.carouselTimer = setInterval(advanceCarousel, CONFIG.carouselInterval);
	CONFIG.carouselInterval = 0
}

function advanceCarousel() {
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
	CONFIG.mainExample.find('.example-img').attr('src', $newTease.data('img-src'));

	// Switch caption of main img
	var $newCaption = CONFIG.mainExample.find('.example-caption-wrap').html($newTease.find('.example-caption-wrap').html());

	// Set product label, this should probably be templated - GW
	$newCaption.find('.example-link').prepend("<p class='example-slug label'>" + $newTease.data('graph-type') + "</p>");
}

function restartTimer() {
	// clearInterval(CONFIG.carouselTimer);
	// startCarousel();
	// window.setTimeout(startCarousel, CONFIG.carouselInterval);
}


// HANDLERS
// =============================================

CONFIG.subExamples.on({
	mouseenter: function() {
		var $this = $(this);
		var newIndex = CONFIG.subExamples.index($(this));
		CONFIG.exampleCounter = newIndex;

		updateCarousel();

		// Restart carousel timer - TK
		restartTimer();
	},
	mouseleave: function() {
		CONFIG.subExamples.addClass('example-inactive').removeClass('example-active');
		CONFIG.subExamples.eq(CONFIG.exampleCounter).addClass('example-active');
	}
});