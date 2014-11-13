// searchresults.js
// =============================================
// This file creates the autocomplete list with AJAX
// And handles search UI/page navigation on submit as well as search analytics
// Gus Wezerek can answer questions about the functions below

// GLOBALS
// =============================================
var cache = {};
var autocomplete_settings = {};


// INIT
// =============================================

// Preserves the url query params on navigate
var search_select_function = function(event, ui) {
  event.preventDefault();

  if (typeof queryActivated !== 'undefined') {
    window.location.href = ui.item.url + '?' + $.param(queryParameters);
  } else {
    window.location.href = ui.item.url;
  }
};

// 
var refactoredSearchSelect = function(event, ui) {
  // event.preventDefault();
  searchNavigate(ui.item);
}

// Set up autocomplete callback
var search_data_source = function(request, response) {
  var term = request.term;

  // I think this covers situations where the input is prepoulated, like on the explore page? - GW
  if (term.length === 0) {
    request.term = $('#text_title').val();
  }

  // Cache to prevent unecessary server requests
  if (term in cache) {
    response(cache[term]);
    return;
  }

  // On search input change we get the list of matching questions and their urls from the db
  $.getJSON('../api/search/', request, function(data) {
    var reshaped_data = [];

    for (var i = 0; i < data[1].length; i += 1) {
      reshaped_data.push({
        value: data[1][i],
        url: data[3][i]
      });
    }

    cache['"' + term + '"'] = reshaped_data;
    response(reshaped_data);
  });

};


// Init config for the explore page
// TODO: Investigate combining these and the inits below them
var configExplore = {
  minLength: 0,
  delay: 260,
  source: search_data_source,
  select: search_select_function
};

// Init config for the homepage
var configHome = {
  appendTo: '.autocomplete-wrap',
  minLength: 3,
  delay: 260,
  source: search_data_source,
  select: refactoredSearchSelect
};

// Init the autocomplete!
$('#text_title').autocomplete(configExplore);
$('#atlas_search_js').autocomplete(configHome);

// Override the _renderItem method to bold the searched term in the autocomplete results
$.widget('ui.autocomplete', $.ui.autocomplete, {

  _renderItem: function(ul, item) {

    // First we find and capture the query string within the input's value
    var term = this.term.split(' ').join('|'),
      re = new RegExp('(' + term + ')', 'gi'),
      highlightClass = 'term-highlight',
      template = '<span class=' + highlightClass + '>$1</span>',
      value = item.value.replace(re, template); // Replace the vlue with the highlighted vlue span

    // Then we append the <li>
    var $li = $('<li/>')
      .data('item.autocomplete', item)
      .append('<a>' + value + '</a>') // Nest an anchor inside the <li>, as that's what jQuery expects
      .appendTo(ul);

    return $li;
  }

});



// HELPERS
// =============================================

function searchNavigate(el) {
  ga('send', {
    'hitType': 'event', // Required.
    'eventCategory': 'Search', // Required.
    'eventAction': 'submit', // Required.
    'eventLabel': el.value
  });

  window.location.href = el.url;
}

function showValidationError() {
  // TODO - GW
}


// HANDLERS
// =============================================

// Validate and navigate on search submit
$('.search-wrap').on('submit', function(event) {
  event.preventDefault();

  var searchTerm = $(this).find('.atlas-search').val();

  // Search the cached AJAX results for a value that matches what's in the input
  // And navigate to that value's corresponding val, or show validation error
  _.each(cache['"' + searchTerm + '"'], function(el) {
    if (searchTerm.toUpperCase() === el.value.toUpperCase()) {
      searchNavigate(el);
    } else {
      showValidationError();
    }
  });
});

$('#atlas_search_js, #text_title').on('autocompletefocus', function(event, ui) {
  // Replace input value with label instead of url, which jQuery UI defaults to
  // event.preventDefault();
  // $(this).val(ui.item.label);
});


