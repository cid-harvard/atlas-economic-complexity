
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

$('.js-select-countries').on('change', function() {
  var $this = $(this);
  ga('send', {
    'hitType': 'event', // Required.
    'eventCategory': 'Explore by Country', // Required.
    'eventAction': 'click', // Required.
    'eventLabel': $this.find('option:selected').text()
  });
  window.location.href = '../explore/tree_map/export/' + $this.val() + '/all/show/2012/';
});

$('.js-select-products').on('change', function() {
  var $this = $(this);
  ga('send', {
    'hitType': 'event', // Required.
    'eventCategory': 'Explore by Product', // Required.
    'eventAction': 'click', // Required.
    'eventLabel': $this.find('option:selected').text()
  });
  window.location.href = '../explore/tree_map/export/show/all/' + $this.val() + '/2012/';
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