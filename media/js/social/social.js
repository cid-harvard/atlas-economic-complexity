// HELPERS

// Creates a popup with the passed URL in the center of the page. Useful for social popups. - GW
function popupCenter(url, w, h) {
    // Fixes dual-screen position                         Most browsers      Firefox
    var dualScreenLeft = window.screenLeft !== undefined ? window.screenLeft : screen.left;
    var dualScreenTop = window.screenTop !== undefined ? window.screenTop : screen.top;
    var width = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;
    var height = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;

    var left = ((width / 2) - (w / 2)) + dualScreenLeft;
    var top = ((height / 2) - (h / 2)) + dualScreenTop;
    var newWindow = window.open(url, 'atlas.cid.harvard.edu', 'scrollbars=no, width=' + w + ', height=' + h + ', top=' + top + ', left=' + left);

    // Puts focus on the newWindow
    if (window.focus) {
        newWindow.focus();
    }
}


// We should think about a better way to store share popup widths across the site
// rather than hardcoding each time as data attributes - GW
function shareClick(event) {
    event.preventDefault();

    var $el = $(event.currentTarget),
        url = $el.attr('href'),
        width = $el.data("popup-width"),
        height = $el.data("popup-height");

    if (url && url !== '#') {
        popupCenter(url, width, height);
    }
}


// HANDLERS

// $('.follow-atlasfacts-btn').on('click', shareClick());

$('.follow-atlasfacts-btn').on('click', function(event) {
    event.preventDefault();

    var $el = $(event.currentTarget),
        url = $el.attr('href'),
        width = $el.data("popup-width"),
        height = $el.data("popup-height");

    if (url && url !== '#') {
        popupCenter(url, width, height);
    }
});
