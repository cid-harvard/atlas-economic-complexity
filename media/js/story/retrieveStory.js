$(document).ready(function() {
	    
//initialize login modal popup	
 $('#dialog-modal-browseStory').modal({
		show: false,
		keyboard: false
		});
//initialize delete confirmation modal popup	
 $('dialog-modal-confirmDelete').modal({
		show: false,
		keyboard: false
		});

});

/**
 * populate tabs with stories after receiving json data
 */
function populateTable(jsonObj,tab,isAdmin)
{
	$("#"+tab+" table").dataTable().fnClearTable();
	 $("#"+tab+" table").dataTable().fnDestroy();
	var storyList=[];
	 for(var i=0;i<jsonObj.length;i++)
		 {
		 var dataItem={};
		 dataItem["pk"]= jsonObj[i].pk;
		 dataItem["story_name"] = jsonObj[i].fields.story_name;
		 if(jsonObj[i].fields.published)
		    dataItem["published"] = "checked";
		 else
		    dataItem["published"] = "";
		 if(jsonObj[i].fields.featured)
		    dataItem["featured"] = "checked";
		 else
		    dataItem["featured"] = "";
	     if(jsonObj[i].fields.number_of_chapters==0)
		    dataItem["number_of_chapters"] = "disabled";
	     else
		    dataItem["number_of_chapters"] = "";
		 storyList.push(dataItem);		 
		 //populate different table templates based on tab
		if(tab=="mystories"||(tab=="published" && isAdmin=="True" ))
			{ 
		 $( "#storyListTemplate1" ).tmpl(storyList[i] ).appendTo( "#"+tab+" tbody" );
			}
		 else
			{
			 $( "#storyListTemplate2" ).tmpl(storyList[i] ).appendTo( "#"+tab+" tbody" );
			}
	   }
	 if(tab=="mystories"||(tab=="published" && isAdmin=="True" ))
		 {
		 $("#"+tab+" table").dataTable({
				"bPaginate": true,
				"bLengthChange": true,
				"bFilter": true,
				"bSort": true,
				"sDom": '<"top"i>rt<"bottom"flp><"clear">',
				"aaSorting": [[ 0, "desc" ]],
				"aoColumns": [
				              { sWidth: '50%' },
				              { sWidth: '10%' },
				              { sWidth: '10%' },
				              { sWidth: '10%' },
				              { sWidth: '10%' },
				              { sWidth: '10%' }]
			});
		 }
	 else
		 {
		 $("#"+tab+" table").dataTable({
				"bPaginate": true,
				"bLengthChange": true,
				"bFilter": true,
				"bSort": true,
				"sDom": '<"top"i>rt<"bottom"flp><"clear">',
				"aaSorting": [[ 0, "desc" ]],
				"aoColumns": [
				              { sWidth: '80%' },
				              { sWidth: '20%' }
				             ]
			});
		 }
}
/**
 * ajax call to update tabs
 */
function ajaxTabUpdater(url,csrf_token)
{
	return	$.ajax
	({
	    type:"POST",
	    contentType: "application/json",
	    async:true,
	    url:url,
	    'data': {
			'csrfmiddlewaretoken': csrf_token,
		},   
	});	
}
	

 /**
 * feature or unfeature a story
 */
 function featureStory(option,csrf_token)
 {
	 var storyId=$(option).val();
		$.ajax({
			'type': 'POST',
			'url': 'featurestory/',
			'data': {
				'csrfmiddlewaretoken': csrf_token,
				'storyId':storyId,
			},
			'success': function(data) {
			},
			'error': function(xhr, textStatus, errorThrown) {
			}
		}); 
 }
 /**
  * publish or unpublish a story
  */
 function publishStory(option,csrf_token)
 {
		var storyId=$(option).val();
		$.ajax({
			'type': 'POST',
			'url': 'publishstory/',
			'data': {
				'csrfmiddlewaretoken': csrf_token,
				'storyId':storyId,
			},
			'success': function(data) {
				var $tab=$(option).parents("tbody");
				if($tab.prop("id")=="publishedData")
					{
				$(option).parents("tr").remove();
					}
			},
			'error': function(xhr, textStatus, errorThrown) {
			alert(errorThrown);
			}
		});
 }
 /**
  * delete a story
  */
 function deleteStory(option,csrf_token)
 {
		var storyId=$(option).data("value");
		$.ajax({
			'type': 'POST',
			'url': 'deleteStory/',
			'data': {
				'csrfmiddlewaretoken': csrf_token,
				'storyId':storyId,
			},
			'success': function(data) {
				$(option).parents("tr").remove();
			},
			'error': function(xhr, textStatus, errorThrown) {
				alert(errorThrown)
			}
		});
 }
 

 /**
  * show confirm delete message
  */
 function showConfirmDeleteDialog(option,csrf_token)
 {
 $("#dialog-modal-confirmDelete").modal('show');
 $("#deleteConfirmed").on("click",function(){
	 deleteStory(option,csrf_token);
 });
 }