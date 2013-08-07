$(document).ready(function() {
	getMovies()
});

$(function() {
	// When the testform is submitted
	$("#testform").submit(function() {
		// post the form values via AJAX
		var postdata = {
			name : $("#name").val()
		};
		$.post('/submit', postdata, function(data) {
			// and set the title with the result
			$("#title").html(data['title']);
		});
		return false;
	});
});