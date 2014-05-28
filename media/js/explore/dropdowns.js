$.ajax({
	dataType: "json",
	url: "http://localhost:8000/api/dropdowns/products/"
})
	.done(function( data ){
		for(var i = 0; i < data.length; i++){
			$("#country_product_select").append("<option value='"+data[i][1]+"'>"+data[i][0]+"</option>");	
		}
	})

$.ajax({
	dataType: "json",
	url: "http://localhost:8000/api/dropdowns/countries/"
})

	.done(function( data ){
		for(var i = 0; i < data.length; i++){
			if (country1 == data[i][0]){
				$("#country1_select").append("<option value='"+data[i][1]+"' selected>"+data[i][0]+"</option>");
			} else {
				$("#country1_select").append("<option value='"+data[i][1]+"'>"+data[i][0]+"</option>");
			}
			if (country2 == data[i][0]){
				$("#country_trade_partner_select").append("<option value='"+data[i][1]+"' selected>"+data[i][0]+"</option>");
			} else {
				$("#country_trade_partner_select").append("<option value='"+data[i][1]+"'>"+data[i][0]+"</option>");
			}
		}
	})

	.then(function(){
		$('#country1_select, #country_trade_partner_select').chosen({ allow_single_deselect: true });
		$('#country_product_select').chosen({ allow_single_deselect: true });		
	  	$("#country1_select_chosen .chosen-single span").css("background", "url('media/img/icons/flag_"+$("#country1 select").val()+".png') no-repeat")
	  		.css("background-size", "25px")
	  		.css("padding-left", "30px")
	  		.css("margin-top", "-2px");	 		
	});

// initialize other dropdowns
$(document).ready(function(){
	$('#year1_select, #year2_select').chosen({ allow_single_deselect: true });
});	