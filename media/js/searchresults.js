// searchresults.js
// =============================================
// This file creates the autocomplete list with AJAX
// And handles search UI/page navigation on submit as well as search analytics
// Gus Wezerek can answer questions about the functions below

var Autocomplete = (function() {


    // SETUP
    // =============================================

    var cache = {},
        resultsList = [],
        autocompleteSettings = {
            appendTo: '.autocomplete-wrap',
            minLength: 3,
            delay: 260,
            source: autocompleteSource
        };


    // Use the widget factory to extend the _renderItem method 
    // so that now it bolds the searched term in the autocomplete results
    // This could probably work in the _renderMenu function instead so we only
    // create on RegExp object, instead of one for each list item
    $.widget('ui.autocomplete', $.ui.autocomplete, {
        _renderItem: function(ul, item) {

            // First we find and capture the query string within the input's value
            var term = this.term.split(' ').join('|'),
                re = new RegExp('(' + term + ')', 'gi'),
                highlightClass = 'term-highlight',
                template = '<span class=' + highlightClass + '>$1</span>',
                value = item.value.replace(re, template); // Replace the value with the highlighted vlue span

            // Then we append the <li>
            var $li = $('<li/>')
                .append('<a>' + value + '</a>') // Nest an anchor inside the <li>, as that's what jQuery expects
                .appendTo(ul);

            return $li;
        }
    });



    // INIT
    // =============================================

    $('#atlas-search-js').autocomplete(autocompleteSettings);



    // HELPERS
    // =============================================

    function autocompleteSource(request, response) {
        var term = request.term;

        // Cache to prevent unecessary server requests
        if (term in cache) {
            response(cache[term]);
            return;
        }

        // Reset our results list
        resultsList = [];

        // On search input change we get the list of matching questions and their urls from the db
        $.getJSON('../api/search/', request, function( data ) {            
            _.each(data[1], function(el, i){
                resultsList.push({
                    value: data[1][i],
                    url: data[3][i]
                });
            });
            
            cache['"' + term + '"'] = resultsList;
            response(resultsList);
        });
    }

    function searchNavigate(el) {
        ga('send', {
            'hitType': 'event', // Required.
            'eventCategory': 'Search', // Required.
            'eventAction': 'submit', // Required.
            'eventLabel': el.value
        });

        // Checks if we have query parameters
        // We should remove this from the global namespace - GW
        if (typeof queryActivated !== 'undefined') {
            window.location.href = el.url + '?' + $.param(queryParameters);
        } else {
            window.location.href = el.url;
        }
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

    // When a user selects an item from the autocomplete list, nav to that page
    $('#atlas-search-js').on('autocompleteselect', function(event, ui) {
        searchNavigate(ui.item);
    });

})();