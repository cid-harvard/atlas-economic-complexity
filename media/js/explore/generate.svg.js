/**
 *  Generate SVG
 *  ~~~~~~~~~~~~
 */

/** IMPORTS **/
// Core
var fs = require( 'fs' );
var system = require( 'system' );
var page = require( 'webpage' ).create();

/** FUNCTIONS **/
/**
 * Wait until the test condition is true or a timeout occurs. Useful for waiting
 * on a server response or for a ui change (fadeIn, etc.) to occur.
 *
 * @param testFx javascript condition that evaluates to a boolean,
 * it can be passed in as a string (e.g.: "1 == 1" or "$('#bar').is(':visible')" or
 * as a callback function.
 * @param onReady what to do when testFx condition is fulfilled,
 * it can be passed in as a string (e.g.: "1 == 1" or "$('#bar').is(':visible')" or
 * as a callback function.
 * @param timeOutMillis the max amount of time to wait. If not specified, 3 sec is used.
 */
function waitFor(testFx, onReady, timeOutMillis) {
    var maxtimeOutMillis = timeOutMillis ? timeOutMillis : 3000, //< Default Max Timout is 3s
        start = new Date().getTime(),
        condition = false,
        interval = setInterval(function() {
            if ( (new Date().getTime() - start < maxtimeOutMillis) && !condition ) {
                // If not time-out yet and condition not yet fulfilled
                condition = (typeof(testFx) === "string" ? eval(testFx) : testFx()); //< defensive code
            } else {
                if(!condition) {
                    // If condition still not fulfilled (timeout but condition is 'false')
                    phantom.exit(1);
                } else {
                    // Condition fulfilled (timeout and/or condition is 'true')
                    typeof(onReady) === "string" ? eval(onReady) : onReady(); //< Do what it's supposed to do once the condition is fulfilled
                    clearInterval(interval); //< Stop this interval
                }
            }
        }, 750); //< repeat check every 750ms
};

// Parse command line arguments
if ( system.args.length != 3 ) {
    // We cannot proceed just exit at this point

    // Exit out of the program at this point
    phantom.exit( 1 );
}

// We are good at this so let us proceed with the request of the page and
// download of the svg to a file
var file_name = system.args[1];
var page_url = encodeURI( system.args[2] );

// Open the specific page and get the svg data
page.open( page_url, function ( status ) {
    // Check for page load success
    if ( status !== "success" ) {
        // We are having an issue it seems at this point
        console.log( "Unable to access page: " + page_url );
    } else {
        // Wait for the svg data to be generated, or rather the loader to disappear
        waitFor( function() {
            // Check in the page if the loader is gone
            return page.evaluate( function() {
                return !$( "#loader" ).is( ":visible" );
            } );
        }, function() {
            // Debug
	    console.log("Generating SVG for URL : " + page_url);	
            // Get the page content now
            result = page.evaluate( function () {
                // Setup the visualization container
                var _viz_container = document.getElementById( "viz" );
                
                // Setup the contents of the viz container
                var _viz_container_content = _viz_container.innerHTML;

                // Let us be safer in case there are nodes prior to the SVG node
                var _viz_svg_split = _viz_container_content.split( '<svg' );
                
                // Split with what we want
                var _viz_content_split = _viz_svg_split[1].split( '</svg>' );
                
                // Return the svg content only
                return "<svg" + _viz_content_split[0] + "</svg>";

                // Check if visualization container has zoom node
                /*if ( $( "#viz" ).children( "svg" ) ) {
                    // Return just the SVG data and nothing else that
                    // might be in the #viz container
                    return document.getElementById( "viz" ).firstChild.nodeName;
                } else if ( $( "#viz" ).children( "#zoom_controls" ) ) {
                    // Now that we have removed unnecessary data from the 
                    // container, return the remaining content
                    $( "#zoom_controls" ).remove();
                    
                    // Return the html now
                    return "Zoom condition"; //document.getElementById( "viz" ).innerHTML;
                } else if ( $( "#viz" ).children( "#d3plus_loader" ) ) {
                    // Now that we have removed unnecessary data from the 
                    // container, return the remaining content
                    $( "#d3plus_loader" ).remove();
                    
                    // Return the html now
                    return "Loader condition"; //document.getElementById( "viz" ).innerHTML;
                } else {
                    // Return the entire HMTL as is
                    return document.getElementById( "viz" ).innerHTML;
                }*/
            } );

            // Write the content to file
            try {
                fs.write( file_name, result.trim(), 'w' );
            } catch( e ) {
                // Debug the exception
                // console.log( e ); 
            }
            console.log("SVG Generated");
            // Get out now
            phantom.exit();
        } );
    }
} );
