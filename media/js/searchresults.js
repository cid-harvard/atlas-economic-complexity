if(!queryParameters['disable_search']) {

  $(function() {
    $("#text_title").click(function() {
      var current_content = $(this).html();
      var new_input = $("<input type='text' id='text_title' />");
      new_input.val(current_content);
      $(this).replaceWith(new_input);
      new_input.focus();
      new_input.autocomplete(autocomplete_settings);
      $(".typed-cursor").remove()
    });

    $.ui.autocomplete.prototype._renderItem = function( ul, item){
      var term = this.term.split(' ').join('|');
      var re = new RegExp("(" + term + ")", "gi") ;
      var t = item.label.replace(re,"<b>$1</b>");
      return $( "<li></li>" )
         .data( "item.autocomplete", item )
         .append( "<a>" + t + "</a>" )
         .appendTo( ul );
    };

    // Set up autocomplete callback
    var cache = {};
    var search_data_source = function(request, response) {
        var term = request.term;
        if (term in cache) {
            response(cache[term]);
            return;
        }
        $.getJSON( "../api/search/",
            request,
            function(data, status, xhr) {
                var reshaped_data = [];
                for (var i = 0; i < data[1].length; i++){
                    reshaped_data.push({label: data[1][i], value: data[3][i]});
                }
                cache[term] = reshaped_data;
                response(reshaped_data);
        });
    };

    var search_select_function = function(event, ui){
        // Go to selected URL
        event.preventDefault();
        $(this).val(ui.item.label);

        window.location.href=ui.item.value+"?"+$.param(queryParameters);
    };

    var search_focus_function = function(event, ui){
        // Get rid of behavior where keyboard up down arrow replaces textbox with
        // url instead of search result.
        event.preventDefault();
    };

    autocomplete_settings = {
        minLength: 3,
        delay: 260,
        source: search_data_source,
        select: search_select_function,
        focus: search_focus_function,
    }

    $("#searchbar").autocomplete(autocomplete_settings);


    querystring = getQueryParameterByName("term");
    var bar = $("#searchbar");
    bar.val(querystring);
    bar.autocomplete("search", querystring);
    bar.focus();

    $("#text_blink").typed({
      strings: [""],
      typeSpeed: 0,
      callback: function() { 

        // Check to see if the title overflows (in the case of long product names)
        function isOverflowed(element){
            return element.scrollHeight > element.clientHeight || element.scrollWidth > element.clientWidth;
        }

        var title = d3.select("#title")
        var shrink_size = 30;

        while(isOverflowed(title.node())) {
          $("#title").children().children().css("font-size", shrink_size+"px")
          shrink_size -= 1;
        }

          }
      });

  });
}
