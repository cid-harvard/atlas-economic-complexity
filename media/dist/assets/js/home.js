
// carousel.js
// =============================================
// This file contains the logic related to the carousel on the homepage
// Gus Wezerek is the original author, go to him with questions


// GLOBALS
// =============================================
var CONFIG = {
	mainExample: $('.example-main'),
	subExamples: $('.example-sub'),
	exampleCounter: 0,
	carouselLen: $('.example-sub').length,
	carouselTimer: 0,
	carouselInterval: 5000,
	exampleTemplate: _.template($('.atlas-example-template').html())
};

// Add our first image
updateCarousel();

// Start the carousel
startCarousel();

// When everything else is ready, load the example thumbnails
$(window).load(addExampleImg());

// HELPERS
// =============================================

function startCarousel() {
	// Don't start the carousel if the main example mod is hidden
	if ( CONFIG.mainExample.css('display') !== 'block' ) {
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

	// Swap the content of the hovered tease
	setMain();
}

function setActiveTease() {
	CONFIG.subExamples.addClass('example-inactive').removeClass('example-active');
	CONFIG.subExamples.eq(CONFIG.exampleCounter).addClass('example-active');
}

function setMain() {
	var $newTease = CONFIG.subExamples.eq(CONFIG.exampleCounter);
	var toAppendString = CONFIG.exampleTemplate({
      img_src: $newTease.data('img-src'),
      caption: $newTease.find('.example-copy').text(),
      slug: $newTease.data('graph-type'),
      ga_label:$newTease.data('ga-label'),
      url: $newTease.find('.example-link').attr('href')
    });

    CONFIG.mainExample.html(toAppendString);
}

// Restarts the carousel timer so the li you just hovered on doesn't advance 
// a second later because of the setInterval in the bground
function restartTimer() {
	clearInterval(CONFIG.carouselTimer);
	startCarousel();
}

function pauseTimer() {
	clearInterval(CONFIG.carouselTimer);
}

function addExampleImg() {
	_.each(CONFIG.subExamples, function(el){
		var $el = $(el);
		$el.find('.example-img').attr('src', $el.data('img-src'));
	});
}


// HANDLERS
// =============================================

CONFIG.subExamples.on({
	mouseenter: function() {
		var newIndex = CONFIG.subExamples.index($(this));
		CONFIG.exampleCounter = newIndex;

		updateCarousel();
		pauseTimer();
	},
	mouseleave: function() {
		CONFIG.subExamples.addClass('example-inactive').removeClass('example-active');
		CONFIG.subExamples.eq(CONFIG.exampleCounter).addClass('example-active');

		restartTimer();
	},

});


// WINDOW RESIZE
// =============================================

// Debounce so that we're not constantly checking for window resizing
var lazyLayout = _.debounce(function() {
	if ( CONFIG.mainExample.css('display') === 'block' ) {
		restartTimer();
	}
}, 100);

$(window).resize(lazyLayout);

// home.js
// =============================================
// This file contains the logic related to the homepage.
// Gus Wezerek is the original author; go to him with questions.


// SETUP
// =============================================

var selectTemplate = _.template($('.atlas-select-template').html());
var bodyEl = document.body;
var openbtn = document.getElementById('open-button');
var closebtn = document.getElementById('close-button');
var isOpen = false;

initSlideinNav();

function initSlideinNav() {
  openbtn.addEventListener('click', toggleNav);
  if (closebtn) {
    closebtn.addEventListener('click', toggleNav);
  }

  // close the menu element if the target is not the menu element or one of its descendants
  $('.js-content-wrap').on('click', function(e) {
    var target = e.target;
    if (isOpen && target !== openbtn) {
      toggleNav();
    }
  });
}


// HELPERS
// =============================================

function populateSelect(options, menu) {
  // Calculate which dropdowns to populate
  var toAppendString = '';

  // Sort the options alphabetically
  options.sort(function(a, b) {
    return a[0] > b[0] ? 1 : -1;
  });

  _.each(options, function(e, i) {
    toAppendString += selectTemplate({
      option: options[i]
    });
  });

  menu.html(toAppendString);
}

function toggleNav() {
  if (isOpen) {
    $(bodyEl).removeClass('show-site-nav-slidein');
  } else {
    $(bodyEl).addClass('show-site-nav-slidein');
  }
  isOpen = !isOpen;
}


// HANDLERS
// =============================================

$.ajax({
  dataType: 'json',
  url: 'api/dropdowns/countries/'
}).done(function(data) {
  populateSelect(data, $('.js-select-countries'));
});

// Page redirect for country and product selects
$('.js-country-or-product').on('click', function() {
  var $this = $(this);
  var selected = $this.siblings('.select-menu-wrap').find('option:selected');
  var url = '';

  ga('send', {
    'hitType': 'event', // Required.
    'eventCategory': $this.data('ga-category'), // Required.
    'eventAction': 'click', // Required.
    'eventLabel': selected.text()
  });

  if ( $this.hasClass('js-country') ) {
    url = '../explore/tree_map/export/' + selected.val() + '/all/show/2014/';
  } else if ( $this.hasClass('js-product') ) {
    url = '../explore/tree_map/export/show/all/' + selected.val() + '/2014/';
  }

  window.location.href = url;
  return false; // Stops the form from submitting and pre-empting the href change
});


$('.track-click').on('click', function() {
  var $this = $(this);
  ga('send', {
    'hitType': 'event', // Required.
    'eventCategory': $this.data('ga-category'), // Required.
    'eventAction': 'click', // Required.
    'eventLabel': $this.data('ga-label')
  });
});
