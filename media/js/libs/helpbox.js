$(document).ready(function(){

// Defines Placeholder Varialbes for Help Box

  var h3_holder ="Help Box";
  var p_holder = "Welcome to the Atlas of Economic Complexity. Hover over an element to see it's function.";

// Replaces displayed text with placeholder text

  function exit(){
    $("#helpBoxInner h3").html(h3_holder);
    $("#helpBoxInner p").html(p_holder);
  }

// Inserts text on mouseenter and replaces it on mouseleave

  $("#country1").mouseenter(function(){
    $("#helpBoxInner h3").html("Country Selector");
    $("#helpBoxInner p").html("This menu allows you to select the country who's data you wish to see.");
  });
  $("#country1").mouseleave(function(){
    exit();
  });

  $("#viz").mouseenter(function(){
    $("#helpBoxInner h3").html("Visualizer");
    $("#helpBoxInner p").html("Here you can find a visual representation of the data that you've selected in the left-hand query.");
  });
  $("#viz").mouseleave(function(e){
    exit();
  });

  $("#trade_flow").mouseenter(function(){
    $("#helpBoxInner h3").html("Flow Type Selector");
    $("#helpBoxInner p").html("This menu allows you to select the desired trade flow type (ie import or export).");
  });
  $("#trade_flow").mouseleave(function(e){
    exit();
  });

  $("#country-product").mouseenter(function(){
    $("#helpBoxInner h3").html("Product Type Selector");
    $("#helpBoxInner p").html("This menu allows you to select the product which is being imported or exported.");
  });
  $("#country-product").mouseleave(function(e){
    exit();
  });

  $("#country-trade-partner").mouseenter(function(){
    $("#helpBoxInner h3").html("Trade Partner Selector");
    $("#helpBoxInner p").html("This menu allows you to select the country which the primary country is either importing from or exporting to.");
  });
  $("#country-trade-partner").mouseleave(function(e){
    exit();
  });

  $("#shareThisPlaceholder").mouseenter(function(){
    $("#helpBoxInner h3").html("Sharing Buttons");
    $("#helpBoxInner p").html("These buttons allow you to share the current visualization through social media or email.");
  });
  $("#shareThisPlaceholder").mouseleave(function(e){
    exit();
  });

  $("#createStoryPlaceHolder").mouseenter(function(){
    $("#helpBoxInner h3").html("Story Creation Button");
    $("#helpBoxInner p").html("This button allows you to create a Story using the current visualization.");
  });
  $("#createStoryPlaceHolder").mouseleave(function(e){
    exit();
  });

  $("#feedbackPlaceholder").mouseenter(function(){
    $("#helpBoxInner h3").html("Feedback Button");
    $("#helpBoxInner p").html("Here, you can let us know if there is anything we can do to improve the Atlas (bug fixes, etc.).");
  });
  $("#feedbackPlaceholder").mouseleave(function(e){
    exit();
  });   
});