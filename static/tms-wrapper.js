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

username = "admin";
password = "admin";
core_api="http://172.17.140.33:8080/core/";

var movies=[];

var TmsLobby = function() {};

$(document).bind("ajaxStop", function(){
	$("#movieList").empty();
	$("#loadingAnimation").fadeOut("slow", function() {
		/* Render the template items for each movie
		and insert the template items into the "movieList" */
		$("#movieTemplate").tmpl(movies).appendTo("#movieList")
		$("#movieList").fadeIn("slow");
	});
});

function get_scheduling(start, end) {
	$.post(
		core_api + "scheduling/schedule",
		{ username: username, password: password, start_time:JSON.stringify(start), end_time:JSON.stringify(end) },
		function(data) {
			process_scheduling(data["data"]);
		}, "json"
	);
}

function process_scheduling(schedule) {
	$.each(schedule, function() {
		var tms_lobby = new TmsLobby();
		
		tms_lobby.start_time = this["start_time"];
		tms_lobby.start_date = this["start_date"];
		duration = this["duration"];
		duration_m = Math.floor(parseInt(duration,10)/60);
		tms_lobby.duration_h = Math.floor(duration_m/60);
		tms_lobby.duration_m = duration_m%60;
		
		tms_lobby.device_id = this["device_information"]["device_uuid"];
		tms_lobby.playlist_id = this["device_information"]["device_playlist_uuid"];
		
		if(tms_lobby.playlist_id==null || tms_lobby.device_id==null)
			return; //this is equivalent to continue
		
		get_playlist(tms_lobby);
	});
}

function get_playlist(tms_lobby) {
	$.post(
		core_api + "playlist/playlist",
		{ username: username, password: password, playlist_ids: JSON.stringify(new Array(tms_lobby.playlist_id)), device_ids: JSON.stringify(new Array(tms_lobby.device_id)) },
		function(data) {
			if($.inArray(tms_lobby.device_id, data["data"]) 
					&& $.inArray(tms_lobby.playlist_id, data["data"][tms_lobby.device_id])
					&& $.inArray("playlist", data["data"][tms_lobby.device_id][tms_lobby.playlist_id]))
				tms_lobby.playlist = data["data"][tms_lobby.device_id][tms_lobby.playlist_id]["playlist"]
				process_playlist(tms_lobby);
		}, "json"
	);
}

function process_playlist(tms_lobby) {
	if(tms_lobby.playlist!=null) {
		tms_lobby.is_3d = tms_lobby.playlist["is_3d"];
		$.each(tms_lobby.playlist["events"], function() {
			if($.inArray("cpl", this)) {
				tms_lobby.cpl_id = this["cpl_id"];
				get_content(tms_lobby);
			}
		});
	}
}

function get_content(tms_lobby) {
	$.post(
		core_api + "content/content",
		{ username: username, password: password, content_ids: JSON.stringify(new Array(tms_lobby.cpl_id)), device_ids: JSON.stringify(new Array(tms_lobby.device_id)) },
		function(data) {
			tms_lobby.content = data["data"];
			process_content(tms_lobby);
		}, "json"
	);
}

function process_content(tms_lobby) {
	$.each(tms_lobby.content, function() {
		if(this["content_kind"] != null && this["content_kind"] == "feature") {
			tms_lobby.audio_language = this["audio_language"];
			tms_lobby.subtitles = this["subtitle_language"];
			tms_lobby.rating = this["rating"];
			get_title(tms_lobby);
			return false; //is equivalent to break
		}
	});
}

function get_title(tms_lobby) {
	$.post(
		core_api + "title/get_title_with_cpl",
		{ username: username, password: password, cpl_uuid: JSON.stringify(tms_lobby.cpl_id) },
		function(data) {
			$.each(data["data"], function() {
				if($.inArray("name", this)) {
					tms_lobby.title = this["name"]
					process_title(tms_lobby);
					return false; //break
				}
			});
		}, "json"
	);
}

function process_title(tms_lobby) {
	var Movie = function() {};
	var movie = new(Movie);
	if(tms_lobby.audio_language != null) {
		movie.audio_language = tms_lobby.audio_language;
	}
	movie.duration_h = tms_lobby.duration_h;
	movie.duration_m = tms_lobby.duration_m;
	movie.start_date = tms_lobby.start_date;
	movie.start_time = tms_lobby.start_time;
	if(tms_lobby.is_3d) {
		movie.is_3d = tms_lobby.is_3d
	}
	if(tms_lobby.rating != null) {
		movie.rating = tms_lobby.rating;
	}
	if(tms_lobby.subtitles != null) {
		movie.subtitles = tms_lobby.subtitles;
	}
	movie.title = tms_lobby.title;
	movies.push(movie);
}

/*function get_screen_name(device_id) {
	$.post(
		core_api + "configuration/screen",
		{ username: username, password: password },
		function(data) {
			$.each(data["data"], function() {
				var parent = this;
				$.each(this["devices"], function() {
					if(this == device_id) {
						process_screen_name(parent["title"]);
					}
				});
			});
		}, "json"
	);
}

function process_screen_name(name) {
	console.log(name);
}

function get_device_info(device_id) {
	$.post(
		core_api + "monitoring/info",
		{ username: username, password: password, device_ids: JSON.stringify(new Array(device_id)) },
		function(data) {
			process_device_info(data["data"][device_id]);
		}, "json"
	);
}

function process_device_info(device) {
	console.log(device);
}*/

function read_tms() {
	$("#loadingAnimation").show("slow");
	var now = new Date();
	var tonight = new Date();
	tonight.setDate(now.getDate()+12);
	tonight.setHours(3);
	get_scheduling(now.format("yyyy-mm-dd HH:mm:ss"), tonight.format("yyyy-mm-dd HH:mm:ss"));
}