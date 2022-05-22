
{{ explorers|json_script:"explorers-data" }}
{{ coin_icons|json_script:"coin_icons-data" }}
{{ notary_icons|json_script:"notary_icons-data" }}
{{ dpow_coins|json_script:"dpow_coins-data" }}
{{ notaries|json_script:"notaries-data" }}
<script>
	var explorers = JSON.parse(document.getElementById('explorers-data').textContent);
	var coin_icons = JSON.parse(document.getElementById('coin_icons-data').textContent);
	var dpow_coins = JSON.parse(document.getElementById('dpow_coins-data').textContent);
	var notaries = JSON.parse(document.getElementById('notaries-data').textContent);

	function pad(num, size) {
	    num = num.toString();
	    while (num.length < size) num = "0" + num;
	    return num;
	}

	function show_region(region) {
		const options = ["#AR", "#EU", "#NA", "#SH", "#DEV"];
		options.forEach(function (i) {
			if (i == region) {
				$(i).fadeTo(1000, 1)
				$(i+"_btn").addClass('btn-selected')
			}
			else {
				$(i).css('display', 'none')	
				$(i+"_btn").removeClass('btn-selected')
			}
		});
	}

	function show_timespan(timespan) {
		const options = ["#season", "#month", "#week", "#last_24hrs"];
		options.forEach(function (i) {
			if (i == timespan) {
				$(i).fadeTo(1000, 1)
				$(i+"_btn").addClass('btn-selected')
			}
			else {
				$(i).css('display', 'none')	
				$(i+"_btn").removeClass('btn-selected')
			}
		});
	}

	function get_time_since(timestamp, until=false, format='text') {

		var time_now = Date.now() / 1000;
		until ? totalSeconds = timestamp - time_now : totalSeconds = time_now - timestamp
		
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
	    		timesince = minutes + " mins, " + seconds + " sec";
	    	}
	    	else {
	    		timesince = minutes + " min, " + seconds + " sec";
	    	}
	    } else if (days == 0) {
	    	if (hours > 1) {
	    		timesince = hours + " hrs, " + minutes + " min";
	    	}
	    	else {
	    		timesince = hours + " hr, " + minutes + " min";
	    	}
	    } else {
	    	if (days > 1) {
	    		timesince = days + " days, " + hours + " hrs";
	    	}
	    	else {
	    		timesince = days + " day, " + hours + " hrs";
	    	}
	    }
	    return timesince
	}

	function get_notaries_symbol(season, notaries, txid) {
		let tooltip_html = ""
		for (let notary of notaries) {
			tooltip_html += notary+"\n"
		}
		return "<a href='{% url 'notarisedViewSet-list' %}?txid="+txid+"'><span class='badge p-0' style='border-radius: 50%;' data-bs-toggle='tooltip'\
					data-bs-placement='top' title=' "+tooltip_html+"'>\
		<i class='fa fa-users' style='font-size:1.5em;'></i>\
		</span></a>";
	}

	function get_coin_icon(coin, url) {
		if (dpow_coins.includes(coin)) {
			url = "/coin_profile/" + coin
		}
		if (!url) url = '#'

    	if (coin_icons.hasOwnProperty(coin)) {
        	return "<a href='"+url+"'><img height='16px' class='mr-2' src='"+coin_icons[coin]+"' />"+coin+"</a>";
        }
        else {
        	return "<a href='"+url+"'><img height='16px' class='mr-2' src='/static/img/notary/icon/blank.png' />"+coin+"</a>";
        }		
	}


	function get_coin_icon_only(coin, url) {
		if (dpow_coins.includes(coin)) {
			url = "/coin_profile/" + coin
		}
    	if (coin_icons.hasOwnProperty(coin)) {
        	return "<span class='' style='' data-toggle='tooltip' data-placement='top' title='"+coin+"'><a href='"+url+"'><img height='18px' class='m-1' src='"+coin_icons[coin]+"' /></a></span>";
        }
        else {
        	return "<span class='' style='' data-toggle='tooltip' data-placement='top' title='"+coin+"'><a href='"+url+"'><img height='18px' class='m-1' src='/static/img/notary/icon/blank.png' /></a></span>"
        }		
	}

	function get_epoch_coins(epoch_coins) {
    	let coin_icons = ''
    	for (let coin of epoch_coins) {
    		coin_icons += get_coin_icon_only(coin)
    	}
        return coin_icons;
	}

	function get_explorer(coin) {
		if (!(explorers.hasOwnProperty(coin))) {
			return false
		}
		else {
			for (let x of explorers[coin]) {
				if (explorers.length == 1) {
					return x
				}
				if (x.search("dexstats") > -1) {
					return x
				}
			}
			return explorers[coin][0]
		}	
	}

	function get_address_url(coin, address, label) {
		let explorer = get_explorer(coin)
		if (!label) {
			label = address
		}
    	if (explorer) {
	    	if (explorer.search("cryptoid") > -1) {
	    		return "<a class='' href='"+explorer+'address.dws?'+address+".htm'>\
	    			<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='View "+address+" on block explorer'>"+label+"</span></a>";	
	    	}
	    	else {
	    		return "<a class='' href='"+explorer+'address/'+address+"'>\
	    			<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='View "+address+" on block explorer'>"+label+"</span></a>";	
	    	}
	    }
	    else {
    		return "<span>"+label+"</span>";	
    	}
	}

	function get_block_url(coin, blockheight, extra_class) {
		let explorer = get_explorer(coin)
    	if (explorer) {
	    	if ((explorer.search("dexstats") > -1) || (explorer.search("explorer.aryacoin.io") > -1)) {
	    		return "<a class='' href='"+explorer+'block-index/'+blockheight+"'>\
	    			<span class='p-0 "+extra_class+"' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='View "+blockheight+" on block explorer'>"+blockheight+"</span></a>";	
	    	}
	    	else if (explorer.search("kmdexplorer") > -1) {
	    		return "<a class='' href='"+explorer+'block-index/'+blockheight+"'>\
	    			<span class='p-0 "+extra_class+"' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='View "+blockheight+" on block explorer'>"+blockheight+"</span></a>";	
	    	}
	    	else if (explorer.search("kmd.sh") > -1) {
	    		return "<a class='' href='"+explorer+'block-index/'+blockheight+"'>\
	    			<span class='p-0 "+extra_class+"' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='View "+blockheight+" on block explorer'>"+blockheight+"</span></a>";	
	    	}
	    	else if (explorer.search("komodod") > -1) {
	    		return "<a class='' href='"+explorer+'b/'+blockheight+"'>\
	    			<span class='p-0 "+extra_class+"' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='View "+blockheight+" on block explorer'>"+blockheight+"</span></a>";	
	    	}
	    	else if (explorer.search("cryptoid") > -1) {
	    		return "<a class='' href='"+explorer+'block.dws?'+blockheight+".htm'>\
	    			<span class='p-0 "+extra_class+"' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='View "+blockheight+" on block explorer'>"+blockheight+"</span></a>";	
	    	}
	    	else {
		    	return "<span>"+blockheight+"</span>";
		    }
		}
    	return "<span>"+blockheight+"</span>";
	}

	function get_txid_url(coin, txid, label) {
		if (!label) {
			label = "<i class='fa fa-search'>"
		}
		let explorer = get_explorer(coin)
    	if (explorer) {
	    	if ((explorer.search("dexstats") > -1) || (explorer.search("explorer.aryacoin.io") > -1)) {
	    		return "<a class='' href='"+explorer+'tx/'+txid+"'>\
	    			<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='View "+txid+" on block explorer'>"+label+"</span></a>";
	    	}
	    	else if (explorer.search("komodod") > -1) {
	    		return "<a class='' href='"+explorer+'t/'+txid+"'>\
	    			<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='View "+txid+" on block explorer'>"+label+"</span></a>";
	    	}
	    	else if ((explorer.search("kmdexplorer") > -1) || (explorer.search("chips.cash") > -1) || (explorer.search("kmd.sh") > -1)) {
	    		return "<a class='' href='"+explorer+'tx/'+txid+"'>\
	    			<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='View "+txid+" on block explorer'>"+label+"</span></a>";
	    	}
	    	else if (explorer.search("cryptoid") > -1) {
	    		return "<a class='' href='"+explorer+'tx.dws?'+txid+".htm'>\
	    			<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='View "+txid+" on block explorer'>"+label+"</span></a>";
	    	}
	    	else {
				if (label != "<i class='fa fa-search'>") {
					label = "<i class='fa fa-search' style='color:darkgrey;'>"
				}
	    		return "<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title=''>"+label+"</span>";	
	    	}
	    }
    	else {
			if (label == "<i class='fa fa-search'>") {
				label = "<i class='fa fa-search' style='color:grey;'>"
			}
    		return "<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title=''>"+label+"</span>";
    	}
	}

	function get_faucet_status(status) {
    	if (status == 'pending') {
        	return "<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='In queue...'><i class='far fa-clock' style='color:white;'></i></span>";		            		
    	} else if (status == 'sent') {
        	return "<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='Sent!'><i class='fas fa-envelope-open-text' style='color:white;'></i></span>";
    	} else {
        	return "<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='In queue...'><i class='far fa-clock' style='color:white;'>"+status+"<i class='far fa-clock' style='color:white;'></i></span>";
    	}		
	}

	function get_faucet_txid(coin, txid) {
    	if (address == 'GalacticFederationPrison') {
        	return "<a href='https://www.galacticfederation.org.uk/'><span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='Galactic Federation Prison'><i class='fab fa-galactic-senate'></i></span></a>";
    	} else if (txid == 'n/a') {
        	return "<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='Awaiting drip...'><i class='fas fa-hourglass-half' style='color:white'></i></i></span>";
    	} else {
        	return get_txid_url(coin, txid);
        }
	}

	function get_notary_url(season, notary) {
		return "<a href=\"{% url 'notary_profile_index_view' %}"+notary+"/?season="+season+"\">"+notary+"</a>"
	}

	function get_season_styled(season) {
    	if (season == "Season_5") {
    		color = "#1e5ead";
    	}
    	else if (season == "Season_5_Testnet") {
    		color = "#622C7B";
    	}
    	else if (season == "Season_4") {
    		color = "#000";
    	}
    	else if (season == "Season_3") {
    		color = "#8A510D";
    	}
    	else if (season == "Season_2") {
    		color = "#622C7B";
    	}
    	else if (season == "Season_1") {
    		color = "#802F5A";
    	}
    	else {
    		color = "#000";	
    	}
        return season.replace(/_/g, " ")
	}

	function get_server_styled(server) {
    	if (server == "Main") {
    		color = "#115621";
    		server = "Main"
    	}
    	else if (server == "Third_Party") {
    		color = "#2b53ad";
    		server = "3P"
    	}
    	else if (server == "Testnet") {
    		color = "#622C7B";
    		server = "Testnet"
    	}
    	else {
    		server = server
    		color = "#000";	
    	}
    	return server
	}

	function get_epoch_styled(epoch) {
    	if (epoch != "Unofficial") {
        	return "<span class='' data-toggle='tooltip' data-placement='top' title='"+epoch+"'>"+epoch.replace('Epoch_','')+"</span>";
        }
        else {	
        	return "<span data-toggle='tooltip' data-placement='top' title='"+epoch+"'><i class='bi bi-exclamation-triangle-fill'></i>";
        }
	}

	function get_detail_link_icon(icon, tooltip, url) {
		return "<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='"+tooltip+"'> \
			<a href='"+url+"'>"+icon+"</i></a>\
		</span>"
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

	function get_score_per_ntx(server, num_coins) {
	    if (server == "Main") {
	        server_score = 0.8698
	    }
	    else if ((server == "Third_Party") || (server == "3P")) {
	        server_score = 0.0977
	    }
	    else if (server == "KMD") {
	        server_score = 0.0325
	    }
	    else if (server == "Testnet") {
	        server_score = 0.0977
	    }
	    else {
	        server_score = 0
	    }

	    tooltip = server_score+" / "+num_coins
	    score = (server_score/parseInt(num_coins)).toFixed(8)
	    return "<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='"+tooltip+"'>\
	    		"+score+"</span>"
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

	function highlight_notaries(table) {
        table.rows().every( function (index) {
	    	var row = table.row(index);
		    var d = row.data();
		    if (d.rank <= 3) {
		    	console.log(d.notary)
		    	row
		    	.nodes()
			    .to$()    // Convert to a jQuery object
				.addClass( 'top_3_row' );
		    }
		});
        table.rows().every( function (index) {
	    	var row = table.row(index);
		    var d = row.data();
		    if ((d.rank == 4) || (d.rank == 5)) {
		    	console.log(d.notary)
		    	row
		    	.nodes()
			    .to$()    // Convert to a jQuery object
				.addClass( 'top_5_row' );
		    }
		});
        var max_AR = table.column(6).data()[0]
	    table.rows().every( function (index) {
	    	var row = table.row(index);
		    var d = row.data();
		    if (d.score < max_AR/3) {
		    	row
		    	.nodes()
			    .to$()    // Convert to a jQuery object
				.addClass( 'danger_row' );
		    }
		});
	}

	function get_social_icon(category, url) {
		let icon = ''
		switch(category) {
			case 'twitter':
				icon = "fab fa-twitter"
				break;
			case 'reddit':
				icon = "fab fa-reddit-square"
				break;
			case 'email':
				icon = "far fa-envelope"
				url = "mailto:"+url
				break;
			case 'linkedin':
				icon = "fab fa-linkedin"
				break;
			case 'explorers':
				if (url.length == 0) url = ''
				icon = "fa-solid fa-binoculars"
				break;
			case 'mining_pools':
				if (url.length == 0) url = ''
				icon = "fa-solid fa-person-digging"
				break;
			case 'youtube':
				icon = "fab fa-youtube"
				break;
			case 'discord':
				icon = "fab fa-discord"
				break;
			case 'telegram':
				icon = "fab fa-telegram-plane"
				break;
			case 'github':
				icon = "fab fa-github"
				break;
			case 'website':
				icon = "fas fa-desktop"
				break;
			case 'keybase':
				icon = "fab fa-keybase"
				if (url.find("keybase") > -1) {
					url = "http://keybase.io/"+url
				}				
				break;
		}
    	if (url) {
    		resp = ''
    		if (['explorers', 'mining_pools'].indexOf(category) > -1) {
    			for (let x of url) {
    				resp += '<a href="'+x+'"><i class="'+icon+' mr-2 social-icon"></i></a>'
    			}
    			return resp
    		}
    		return '<a href="'+url+'"><i class="'+icon+' mr-2 social-icon"></i></a>'
    	}
		else {
			return '<i class="'+icon+' mr-2 social-icon-disabled"></i>'
		}
	}
	
	function get_link(url, text) {
		return "<a href='"+url+"'>"+text+"</a>"
	}


	function getVal(item) {
	    return item[this];
	}

	function getSum(total, num) {
	    return total + num;
	}

	function getAverage(data, key, dp=3) {
		let totals = data.map(getVal, key)
		let sum = totals.reduce(getSum, 0)
		return Math.round(sum / totals.length * dp) / dp
	}

function get_qrcode(id, text, title, subtitle) {
	$(id).html('')
	jQuery(id).qrcode({foreground:"#070e28", background:"#b1d1d3", "text":text});
	$('#qrcode-modal-label').html(title)
	$('#qrcode-modal-subtitle').html(subtitle)
}

</script>
