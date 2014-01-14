$(document).ready(function(){
  var p_holder = "Welcome to the Atlas of Economic Complexity. Hover over an element to see it's function";
  var h3_holder ="Help Box";

  function exit(){
    $("#helpBoxInner h3").html(h3_holder);
    $("#helpBoxInner p").html(p_holder);
  }


  $("#viz").mouseenter(function(){
    $("#helpBoxInner h3").html("Visualizer");
    $("#helpBoxInner p").html("");
  });

  $("#viz").mouseleave(function(e){
    exit();
  });
});