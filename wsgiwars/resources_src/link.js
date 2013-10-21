$( document ).ready(function() {
    $("#link" ).change(function() {
	$.post('/ajax/gettitle',
	       {'url': $(this).val()},
	       function (data) {
		   $("#title").val(data['title']);
	       }
	      );
    });
});
