$(document).ready(function() {
	$('#scheduling').click(function() {
        get_scheduling("2013-08-06 10:00:00", "2013-08-19 10:00:00");
    });
	getMovies();
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