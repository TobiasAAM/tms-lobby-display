$(document).ready(function() {
	$('#scheduling').click(function() {
        read_tms();
    });
	read_tms();
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

function convert12to24(timeStr)
{
    var meridian = timeStr.substr(timeStr.length-2).toLowerCase();
    var hours    = timeStr.substring(0, timeStr.indexOf(':'));
    var minutes  = timeStr.substring(timeStr.indexOf(':')+1, timeStr.indexOf(' '));
    if (meridian=='pm')
    {
        hours = (hours=='12') ? '00' : parseInt(hours)+12 ;
    }
    else if(hours.length<2)
    {
        hours = '0' + hours;
    }
    return hours+':'+minutes;
}

function compareDate(a, b) {
	return convert12to24(a.start_time) > convert12to24(b.start_time);
}