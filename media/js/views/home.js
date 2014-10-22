
// SETUP

var selectTemplate = _.template($(".atlas-select-template").html());


// HELPERS

function populateSelect(options, menu) {
    // Calculate which dropdowns to populate
    var toAppendString = "";

    // Sort the options alphabetically
    options.sort(function(a, b) {
        return a[0] > b[0] ? 1 : -1;
    });

    _.each(options, function(e, i){
        toAppendString += selectTemplate({ option: options[i] });
    });

    menu.html(toAppendString);
}


// HANDLERS

$.ajax({
    dataType: "json",
    url: "api/dropdowns/countries/"
}).done(function(data) {
    populateSelect(data, $(".js-select-countries"));
});

$('.js-select-countries').on('change', function(){
    var $this = $(this);
    ga('send', {
      'hitType': 'event',          // Required.
      'eventCategory': 'Explore by Country',   // Required.
      'eventAction': 'click',      // Required.
      'eventLabel': $this.find('option:selected').text()
    });
    window.location.href = '../explore/tree_map/export/' + $this.val() + '/all/show/2012/';
});


$('.js-select-products').on('change', function(){
    var $this = $(this);
    ga('send', {
      'hitType': 'event',          // Required.
      'eventCategory': 'Explore by Product',   // Required.
      'eventAction': 'click',      // Required.
      'eventLabel': $this.find('option:selected').text()
    });
    window.location.href = '../explore/tree_map/export/show/all/' + $this.val() + '/2012/';
});

sublime.ready(function(){
    sublime.player('js-hausman-vid').on('start', function(player) {
        ga('send', {
          'hitType': 'event',          // Required.
          'eventCategory': 'Hausman Video',   // Required.
          'eventAction': 'click',      // Required.
          'eventLabel': 'Play'
        });
        $('.video-wrap').fadeOut(200);
    });
});

$('.track-click').on('click', function(){
    var $this = $(this);
    ga('send', {
      'hitType': 'event',          // Required.
      'eventCategory': $this.data('ga-category'),   // Required.
      'eventAction': 'click',      // Required.
      'eventLabel': $this.data('ga-label')
    });
});

jQuery.ui.autocomplete.prototype._resizeMenu = function () {
  var ul = this.menu.element;
  ul.outerWidth(this.element.outerWidth());
}
