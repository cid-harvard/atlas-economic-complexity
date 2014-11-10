// searchresults.js
// =============================================
// This file creates the autocomplete list with AJAX
// And prepares the string 
// Romain Vuillemot is the original author, go to him with questions

// GLOBALS
// =============================================
var cache = {};
var autocomplete_settings = {};



// SETUP
// =============================================

// Override the _renderItem method to bold the searched term in the autocomplete results
$.widget( 'ui.autocomplete', $.ui.autocomplete, {

   _renderItem: function( ul, item ) {

      // First we find and capture the query string within the item label
      var term = this.term.split(' ').join('|'),
          re = new RegExp( '(' + term + ')', 'gi' ),
          template = '<span class="term-highlight">$1</span>',
          label = item.label.replace( re, template );              // Replace the term with the highlighted term span
         
      // Then we append the <li>
      var $li = $( '<li/>' )
        .data( 'item.autocomplete', item )
        .append( '<a>' + label + '</a>' )                              // Nest an anchor inside the <li>, as that's what jQuery expects
        .appendTo( ul );

     return $li;
   }

});


// HELPERS
// =============================================

// Preserves the url query params on navigate
var search_select_function = function(event, ui){
    // Go to selected URL
    event.preventDefault();
    $(this).val(ui.item.label);

    if(typeof(queryActivated) != 'undefined' && queryActivated) {
      window.location.href=ui.item.value+'?'+$.param(queryParameters);
    } else {
      window.location.href=ui.item.value; 
    }
};

var search_focus_function = function(event){
    // Get rid of behavior where keyboard up down arrow replaces textbox with
    // url instead of search result.
    event.preventDefault();
};



// HANDLERS
// =============================================

// Set up autocomplete callback
var search_data_source = function(request, response) {
    if(request.term.length == 0) {
       request.term = $('#text_title').val();
    }

    var term = request.term;
    if (term in cache) {
        response(cache[term]);
        return;
    }
    $.getJSON( '../api/search/',
        request,
        function(data) {
            var reshaped_data = [];
            for (var i = 0; i < data[1].length; i += 1){
                reshaped_data.push({label: data[1][i], value: data[3][i]});
            }
            cache[term] = reshaped_data;
            response(reshaped_data);
    });

    if($('#searchbar').length > 0) {
      _gaq.push(['_trackEvent', 'Search-Home', 'Typing', $('#searchbar').val()]);
    }

    if($('#text_title').length > 0) {
      _gaq.push(['_trackEvent', 'Search-Page', 'Typing', $('#text_title').val()]);
    }
};

// FOR EXPLORE PAGE
var autocomplete_settings = {
    minLength: 0,
    delay: 260,
    source: search_data_source,
    select: search_select_function,
    focus: search_focus_function
};

$('#text_title').autocomplete(autocomplete_settings);
$('#text_title').blur();

$('#text_title').click(function() {
  $(this).autocomplete( 'search', '');
  _gaq.push(['_trackEvent', 'Search-Page', 'Focus', $(this).val()]);
});

// FOR HOME PAGE
var autocomplete_settings_home = {
  appendTo: '.autocomplete-wrap',
  minLength: 3,
  delay: 260,
  source: search_data_source,
  select: search_select_function,
  focus: search_focus_function,
};

$('#searchbar').autocomplete(autocomplete_settings_home);

$('#searchbar').click(function() {
  _gaq.push(['_trackEvent', 'Search-Home', 'Focus', $(this).val()]);
  $(this).autocomplete( 'search', '' );
});
