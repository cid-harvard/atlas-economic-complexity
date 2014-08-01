
// initialize other dropdowns
$(document).ready(function(){

    $.ajax({
        dataType: "json",
        data: {lang: lang},
        url: "api/dropdowns/products/" + prod_class + "/"
    })
    .done(function( data ){

        var product_dropdowns = ["#country_product_select"];
        var highlight_contains_products = (app_type == "casy" || app_type == "ccsy");
        if(highlight_contains_products){
            product_dropdowns.push("#highlight_select");
        }

        for(var i = 0; i < data.length; i++){
            $(product_dropdowns.join(", ")).append($('<option/>').val(data[i][1]).text(data[i][0]));
        }

        var product_options = {
            placeholder:"All Products",
            allowClear: true,
        };

        $("#country_product_select")
            .select2(product_options)
            .select2("val", product_code);

        if (highlight_contains_products){
            $("#highlight_select")
                .select2(product_options);
        }
    })

    $.ajax({
        dataType: "json",
        data: {lang: lang},
        url: "api/dropdowns/countries/"
    })
    .done(function( data ){

        // Calculate which dropdowns to populate
        var country_dropdowns = ["#country1_select", "#country_trade_partner_select"];
        var highlight_contains_countries = (app_type == "cspy" || app_type == "csay" || app_type == "sapy");
        if(highlight_contains_countries){
            country_dropdowns.push("#highlight_select");
        }

        for(var i = 0; i < data.length; i++){
            $(country_dropdowns.join(", ")).append($('<option/>').val(data[i][1]).text(data[i][0]));
        }

        var c1 = country1_3char.toLowerCase();
        var c2 = country2_3char.toLowerCase();

        function format_country_dropdown(country){
            return "<img class='flag' src='media/img/icons/flag_" + country.id + ".png' width='20%'/> " + country.text;
        }

        var country_options = {
            placeholder:"All Countries",
            formatResult: format_country_dropdown,
            formatSelection: format_country_dropdown,
            allowClear: true,
        };

        $("#country1_select")
            .select2(country_options)
            .select2("val", c1);

        $("#country_trade_partner_select")
            .select2(country_options)
            .select2("val", c2);

        if (highlight_contains_countries){
            $("#highlight_select")
                .select2(country_options);
        }

    });

    $('#year1_select, #year2_select').select2();
    $('.language_select select').select2();
});
