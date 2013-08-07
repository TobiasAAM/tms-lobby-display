function getMovies() {
	$("#loadingAnimation").show("slow");
	$.post('/getmovies', function(movies) {
		/* Get the movies array from the data */
		/* Remove current set of movie template items */
		$("#movieList").empty();
		$("#loadingAnimation").fadeOut("slow", function() {
			/* Render the template items for each movie
			and insert the template items into the "movieList" */
			$("#movieTemplate").tmpl(movies).appendTo("#movieList")
			$("#movieList").fadeIn("slow");
		});
	});
}