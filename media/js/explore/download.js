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
        var svg_content = $("#viz svg")[0].outerHTML;
        form.children("#content").val(svg_content);
        form.submit();
    });

});
