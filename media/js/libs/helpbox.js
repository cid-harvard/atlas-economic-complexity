$(document).ready(function(){

  // Defines Placeholder Varialbes for Help Box
  if(app_name == "product_space"){
    var h3_holder ="Product Space";
    var p_holder = "Explore how related products are based on the know-how required to produce them.";

  } else if(app_name == "pie_scatter"){
    var h3_holder = "Product Feasibility";
    var p_holder = "Determine how plausible it is for a country to produce a specific product based on what they're already producing.";
  } else{
    var h3_holder ="";
    var p_holder = "Welcome to the Atlas of Economic Complexity. Hover over an element to see it's function.";
  }

  // Replaces displayed text with placeholder text

  function exit(){
    if(app_name == "pie_scatter" || app_name == "product_space"){
      $("#helpBoxInner").hide();
    }
    $("#helpBoxInner h3").html(h3_holder);
    $("#helpBoxInner p").html(p_holder);
  }
  exit();
  // Inserts text on mouseenter and replaces it on mouseleave
  $("#helpBoxInner").show();

  $("#country1").mouseenter(function(){
    $("#helpBoxInner").show();
    $("#helpBoxInner h3").html("Country Selector");
    $("#helpBoxInner p").html("Select the country you want to expore.");
  });
  $("#country1").mouseleave(function(){
    exit();
  });

  $("#viz").mouseenter(function(){
    $("#helpBoxInner").show();
    $("#helpBoxInner h3").html("Visualization");
    $("#helpBoxInner p").html("The visualization displays the query you have selected.");
  });
  $("#viz").mouseleave(function(e){
    exit();
  });

  $("#trade_flow").mouseenter(function(){
    $("#helpBoxInner").show();
    $("#helpBoxInner h3").html("Flow Type Selector");
    $("#helpBoxInner p").html("Choose whether you would like to explore import or export data.");
  });
  $("#trade_flow").mouseleave(function(e){
    exit();
  });

  $("#country-product").mouseenter(function(){
    $("#helpBoxInner").show();
    $("#helpBoxInner h3").html("Product Type Selector");
    $("#helpBoxInner p").html("Select which product you would like to explore.");
  });
  $("#country-product").mouseleave(function(e){
    exit();
  });

  $("#country-trade-partner").mouseenter(function(){
    $("#helpBoxInner").show();
    $("#helpBoxInner h3").html("Trade Partner Selector");
    $("#helpBoxInner p").html("Choose if you would like to explore the trade relationship with a specific partner.");
  });
  $("#country-trade-partner").mouseleave(function(e){
    exit();
  });

  $("#shareThisPlaceholder").mouseenter(function(){
    $("#helpBoxInner").show();
    $("#helpBoxInner h3").html("Sharing Buttons");
    $("#helpBoxInner p").html("Found something interesting? Share it with others on Facebook, Twitter, Google+ or via email.");
  });
  $("#shareThisPlaceholder").mouseleave(function(e){
    exit();
  });

  $("#createStoryPlaceHolder").mouseenter(function(){
    $("#helpBoxInner").show();
    $("#helpBoxInner h3").html("Story Creation Button");
    $("#helpBoxInner p").html("Begin a story and add this visualization to the story you want to tell.");
  });
  $("#createStoryPlaceHolder").mouseleave(function(e){
    exit();
  });

  $("#feedbackPlaceholder").mouseenter(function(){
    $("#helpBoxInner").show();
    $("#helpBoxInner h3").html("Feedback Button");
    $("#helpBoxInner p").html("Let us know how we can improve the Atlas (bug fixes, content layout, etc.).");
  });
  $("#feedbackPlaceholder").mouseleave(function(e){
    exit();
  });
  if(previous_image == "http://atlas.cid.harvard.edu/media/img/all/loader.gif"){
    $("#history, #historyTab").hide();
  }
  if(app_name == "product_space" || app_name == "pie_scatter"){
    $("#helpBoxInner").css("display", "none");
  }
});
