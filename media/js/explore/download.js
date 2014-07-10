$(function(){

    /* No nice ajax-y way to force user agents to do a download. The other
     * alternative is pointing window.location to the download view, but can't
     * do POST params with that. I don't know if the SVG will overflow the max
     * URL size limit, so doing this. */

    $("#download #png, #download #pdf, #download #svg")
    .click(function(){
        var form = $(this).parent();
        var file_type = this.id;
        form.children("#file_format").val(file_type);
        var svg_elem = $("#viz svg")[0];
        if (svg_elem.outerHTML !== undefined){
            form.children("#file_content").val(svg_elem.outerHTML);
        } else if (typeof XMLSerializer !== undefined) {
            form.children("#file_content").val((new XMLSerializer).serializeToString(svg_elem));
        } else if (xmlNode.xml) {
            form.children("#file_content").val(svg_elem.xml);
        } else {
            alert("Sorry, your browser doesn't support this feature. Please try the newest Google Chrome or Mozilla Firefox.");
            return;
        }
        form.submit();
    });

});
