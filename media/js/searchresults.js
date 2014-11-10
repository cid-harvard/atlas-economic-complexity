// searchresults.js
// =============================================
// This file creates the autocomplete list with AJAX
// And prepares the string 
// Romain is the original author, go to him with questions

$(function() {

  // Bolding the searched for term
  // Adds Google analytics to the autocomplete items
  // Tracks where the search is coming from based on ID
  $.ui.autocomplete.prototype._renderItem = function( ul, item){
    console.log(this);

    var term = this.term.split(' ').join('|');
    var re = new RegExp('(' + term + ')', 'gi') ;
    var t = item.label.replace(re,'<b>$1</b>');

    var suggestion_page = 'Title';
    if($('#searchbar').length > 0) {
      suggestion_page = 'Home';
    }

    return $( '<li></li>' )
       .data( 'item.autocomplete', item )
       .append('<a onclick="_gaq.push([\'_trackEvent\', \'Suggestion-' + suggestion_page + '\', \'Clicked\', \'' + this.term + '\'])">' + t + '</a>' )
       .appendTo( ul );
  };

  // Set up autocomplete callback
  var cache = {};
  var search_data_source = function(request, response) {
      if(request.term.length == 0) {
         request.term = $('#text_title').val();
      }

      request.search_var = search_var;
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
});
