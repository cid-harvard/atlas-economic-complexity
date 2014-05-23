$.ajax({
	dataType: "json",
	url: "http://localhost:8000/api/dropdowns/products/"
})
.done(function( data ){
	for(var i = 0; i < data.length; i++){
		$("#country_product_select").append("<option value='"+data[i][1]+"'>"+data[i][0]+"</option>");
	}
});