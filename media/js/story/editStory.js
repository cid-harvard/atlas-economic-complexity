/**
* Edit story functionality
*/
$(function() {
	  var fixHelper = function(e, ui) {
			ui.children().each(function() {
				$(this).width($(this).width());
			});
			return ui;
		};

		$("#sortChapters tbody").sortable({
			 update: function(event, ui){ 
				 var i=1;
	              $('table tr').each(function(){
	            	  if($(this).data("isremoved")=="N"){
	              $(this).children('td:first-child').html(i);
	              i++;
	            	  }
	              })
			 },
			helper: fixHelper
		}).disableSelection();
		
		$("#sortChapters .editBtn").on('click tap', function(e) {
		    editTable(this);
		    e.preventDefault();
		  });
		
		$("#sortChapters .del").on('click tap', function(e) {
		    deleteTable(this);
		    e.preventDefault();
		  });
		$("#updateStoryBtn").on('click tap',function(e){
			checkChapterEditMode(this);
			createJsonObject(this);
		})
		
		
		
	
});
  
/**
* Edit story title and description on click of edit button
*/
   function editTitle(button)
	{
			var $editableBlock=$(button).parents(".editable");
			var $editableText=$editableBlock.children(".editableText");
			if($editableBlock.data('flag')) { 
				$editableText.html($editableBlock.find('textarea').val());
			   $editableBlock.data('flag',false);

			  }
			else{
				$editableText.data('text', $editableText.html()).html('');
				var $input = $('<textarea rows="2"  style="float:left;" maxLength="200"/>')
		        .val($editableText.data('text').split('<br>').join('\n').split('&nbsp;').join(' '))
		        .width($editableText.width()-10);
				$editableText.append($input);
			    $editableBlock.data('flag', true);
				
			}
			
		}

/**
* Check if chapter is in edit mode and return
*/
  function checkChapterEditMode(button)
  {
	 
	  var $tbody=$("#sortChapters").children('tbody');
      var $rows=$tbody.children('tr');
	  $rows.each(function(){
		  var _row=$(this);
		  var $cells = _row.children(".cdText,.ctText").not('.edit');
	 
	  if(_row.data('flag')) { // in edit mode, move back to table
		    // cell methods
		    $cells.each(function () {
		      var _cell = $(this);
		      _cell.html(_cell.find('textarea').val());
		    })
		    
		    _row.data('flag',false);
		  } 
	  })
	  checkTitleEditMode();
  }
  /**
  * Check if title and description is in edit mode and return
  */ 
 function  checkTitleEditMode()
 {
	 var $editables=$("#MainQueueForm").children(".editable");
	 $editables.each(function(){
		  var _editable=$(this);
		  var $cells = _editable.children(".editableText").not('.edit');
	 
	  if(_editable.data('flag')) { // in edit mode, move back to table
		    // cell methods
		    $cells.each(function () {
		      var _cell = $(this);
		      _cell.html(_cell.find('textarea').val());
		    })
		    
		    _editable.data('flag',false);
		  } 
	  })
 }
  
/**
* Edit Chapter on click of edit button
*/
		function editTable(button)
		{
			var $button = $(button);
		    var $row = $button.parents('tbody tr');
		    var $cells = $row.children(".cdText,.ctText").not('.edit');
		  
		  if($row.data('flag')) { // in edit mode, move back to table
		    // cell methods
		    $cells.each(function () {
		      var _cell = $(this);
		      _cell.html(_cell.find('textarea').val());
		    })
		    
		    $row.data('flag',false);
		  } 
		  else { // in table mode, move to edit mode 
		    // cell methods
		    $cells.each(function() {
		      var _cell = $(this);
		      _cell.data('text', _cell.html()).html('');
		      
		      var $input = $('<textarea rows="4" maxLength="300"/>')
		        .val(_cell.data('text').split('<br>').join('\n').split('&nbsp;').join(' '))
		        .width(_cell.width()-30);
		        
		      _cell.append($input);
		    })
		    
		    $row.data('flag', true);
		    
		  }
		  }
/**
* Delete chapter
*/
		function deleteTable(button)
		{
			var $button = $(button);
		    var $row = $button.parents('tbody tr');
		    $row.attr('data-isremoved',"Y");
		    $row.hide();
		    
		    var $table=$row.parents("tbody");
		    var $rows=$table.children("tr[data-isremoved='N']");
		    var i=1;
		    $rows.each(function(){	  
		        $(this).children('td:first-child').html(i);
		        i++;
		        })		
		}		
/**
* Create JSON object of edited story Content
*/
		function createJsonObject(button)
		{
			var jsonObj = [];
			var $rows=$("#sortChapters tbody").children();
			$rows.each(function(){
				var $row=$(this);
				var order=parseInt($row.children('td:first-child').html());
				var chapterTitle=$row.children('td:nth-child(2)').html();
				var chapterDesc=$row.children('td:nth-child(3)').html();
				var isRemoved=$row.data('isremoved');
				var chapterId=$row.data('chapter');
				
				var item={};
				item["order"]=order;
				item["chapterTitle"]=chapterTitle;
				item["chapterDesc"]=chapterDesc;
				item["isRemoved"]=isRemoved;
				item["chapterId"]=chapterId;
				jsonObj.push(item);				
			});	
			
			$("#chapterJson").val(JSON.stringify(jsonObj));		
			$("#storyTitle").val($("#editStoryName .editableText").html());
			$("#storyDesc").val($("#editStoryDesc .editableText").html());
		}  