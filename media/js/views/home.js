
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
    window.location.href = '../explore/tree_map/export/' + $(this).val() + '/all/show/2012/';
});


$('.js-select-products').on('change', function(){
    window.location.href = '../explore/tree_map/export/show/all/' + $(this).val() + '/2012/';
});

sublime.ready(function(){
    sublime.player('js-hausman-vid').on('start', function(player) {
        ga('send', {
          'hitType': 'event',          // Required.
          'eventCategory': 'video',   // Required.
          'eventAction': 'click',      // Required.
          'eventLabel': 'play'
        });
        $('.video-wrap').fadeOut(200);
    });
});
