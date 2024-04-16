<!-- chrono.js -->
<script>
function get_time_since(ts, until=false, format='text', precalc=false) {
    timestamp = parseInt(ts)
    if (ts == 0 ) {
        return "Never"
    }
    if (isNaN(timestamp)) return ts

    if (!precalc) {
        var time_now = Date.now() / 1000;
        until ? totalSeconds = timestamp - time_now : totalSeconds = time_now - timestamp
    }
    else {
        totalSeconds = timestamp
    }
    
    if (totalSeconds < 0) return 0

    days = Math.floor(totalSeconds / 86400);

    totalSeconds %= 86400;
    hours = Math.floor(totalSeconds / 3600);

    totalSeconds %= 3600;
    minutes = Math.floor(totalSeconds / 60);

    totalSeconds %= 60;
    seconds = Math.floor(totalSeconds);

    if (format == 'numeric') {
        response = pad(hours, 2) + ":" + pad(minutes, 2) + ":" + pad(seconds, 2)
        if (days != 0) {
            response = days + " days, " + response
        }
        return response
    }

    if (days > 400) return "Never"
    if ((days == 0) && (hours == 0) && (minutes == 0)) {
        timesince = seconds + " sec";
    } else if (days == 0 & hours == 0) {
        if (minutes > 1) {
            timesince = minutes + " mins, " + pad(seconds,2) + " sec";
        }
        else {
            timesince = minutes + " min, " + pad(seconds,2) + " sec";
        }
    } else if (days == 0) {
        if (hours > 1) {
            timesince = hours + " hrs, " + pad(minutes,2) + " min";
        }
        else {
            timesince = hours + " hr, " + pad(minutes,2) + " min";
        }
    } else {
        if (days > 1) {
            timesince = days + " days, " + pad(hours,2) + " hrs";
        }
        else {
            timesince = days + " day, " + pad(hours,2) + " hrs";
        }
    }
    return timesince
}

function getOffset() {
    var d = new Date();
    return d.getTimezoneOffset()*60*1000;
}

function local_date_str(date_str) {
    var d = Date.parse(date_str);
    var offset = getOffset()
    var x = new Date(d-offset)
    var ds = x.toLocaleDateString();
    var ts = x.toLocaleTimeString();
    return ds+" "+ts;
}

function show_timespan(timespan) {
    const options = ["#season", "#month", "#week", "#last_24hrs"];
    options.forEach(function (i) {
        if (i == timespan) {
            $(i).fadeTo(1000, 1)
            $(i+"_btn").addClass('btn-selected')
            if (i == '#month') {
                $("#month_selection").show()
                $("#date_selection").hide()
                $("#month_title").show()
                $("#date_title").hide()
            }
            if (i == '#last_24hrs') {
                $("#month_selection").hide()
                $("#date_selection").show()
                $("#month_title").hide()
                $("#date_title").show()
            }
        }
        else {
            $(i).css('display', 'none')	
            $(i+"_btn").removeClass('btn-selected')
        }
    });
}

function update_timespan(e, from_id, to_id) {
    now = parseInt(Date.now()/1000)
    $('#'+to_id).val(now)
    gap = $("#"+e.id).val()
    switch(gap) {
        case 'day':
            when = now - 60*60*24
            break;
        case 'week':
            when = now - 60*60*24*7			    
            break;
        case 'fortnight':
            when = now - 60*60*24*14			    
            break;
        case 'month':
            when = now - 60*60*24*30			    
            break;
        case 'year':
            when = now - 60*60*24*365			    
            break;
        default:
            when = now - 60*60*24
    }
    $('#'+from_id).val(when)
}

</script>
