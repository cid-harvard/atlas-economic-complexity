
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

// $.ajax({
//     dataType: "json",
//     url: "api/dropdowns/products/hs4/"
// }).done(function(data) {
//     populateSelect(data, $(".js-select-products"));
// });
