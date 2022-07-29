
{{ explorers|json_script:"explorers-data" }}
{{ coin_icons|json_script:"coin_icons-data" }}
{{ notary_icons|json_script:"notary_icons-data" }}
{{ dpow_coins|json_script:"dpow_coins-data" }}
{{ notaries|json_script:"notaries-data" }}
<script>
	// TODO: explorers and coin_icons are data heavy.
	// Should not load these unless needed, and use params to constrain when only dpow related required.
	var explorers = JSON.parse(document.getElementById('explorers-data').textContent);
	var coin_icons = JSON.parse(document.getElementById('coin_icons-data').textContent);
	var dpow_coins = JSON.parse(document.getElementById('dpow_coins-data').textContent);
	var notaries = JSON.parse(document.getElementById('notaries-data').textContent);

	function pad(num, size) {
	    num = num.toString();
	    while (num.length < size) num = "0" + num;
	    return num;
	}

	function pad_decimal(num, size) {
		split = num.toString().split(".")
	    dec = split[1] ? split[1] : 0
	    num = split[0] + "." + dec
	    size = split[0].length + size + 1
	    while (num.length < size) num = num + "0";
	    return num;
	}

	function remove_node(id) {
		$(id).remove()
	}

	function addAddress_Row(id) {
		num_rows = $(id).children().length;
		out_row = 'address_row_'+num_rows
		out_id = 'output_amount_'+num_rows
		$(id).append('<div class="row" id="'+out_row+'"> \
							<div class="input-group mb-3 col-9"> \
							    <div class="input-group-prepend prepend-label-left p-0" > \
							        <span class="input-group-text " style="color:white; border: solid grey 1px !important; line-height: 1em;"> \
							      	    To {{ coin }} Address \
							        	<i onclick="remove_node(\'#'+out_row+'\')" class="fas fa-times-circle pl-2 m-0" style="font-size: 0.8em;"></i> \
							        </span> \
							    </div> \
							    <input type="text" class="form-control m-auto" id="address_id" name="to_address" style="border: solid grey 1px !important; font-size: 1em; line-height: 0.7em; text-align: center; min-width: 34em"> \
							</div> \
							<div class="input-group mb-3 col-3"> \
							    <div class="input-group-prepend prepend-label-left p-0" > \
							        <span class="input-group-text" style="color:white; border: solid grey 1px !important; line-height: 1em;"> \
							      	    Amount \
							        </span> \
							    </div> \
							    <input type="text" onchange="sanitize_outputs()" class="form-control m-0 " id="'+out_id+'" name="output_amount" value="0" style="border: solid grey 1px !important; font-size: 1em; line-height: 0.7em; text-align: center;" value=""> \
							    <div class="input-group-append p-0  "> \
									<button class="append-btn" type="button" onclick="spendMax(\'#'+out_id+'\')" style="line-height: 1em; border: solid grey 1px !important;"> \
									    Max \
									</button> \
							    </div> \
							</div> \
						</div>');
	}

	function iconify_version(gui) {
    	gui = gui.replace(/-beta/ig, '')
    	gui = gui.replace(/0.5.5/ig, '')
    	gui = gui.replace(/0.5.4/ig, '')
    	gui = gui.replace(/pyMakerbot/ig, '<i class="fa-brands fa-python"></i>')
    	gui = gui.replace(/WASMTEST/ig, '<i class="fa-brands fa-weebly"></i>')

    	gui = gui.replace(/MM2CLI/ig, '<i class="fa-brands fa-steam-square"></i>')
    	gui = gui.replace(/mpm/ig, '<i class="fa-brands fa-mandalorian"></i> ')
    	gui = gui.replace(/SwapCase Desktop/ig, '<i class="fa-solid fa-circle-question"></i>')
    	gui = gui.replace(/ColliderDEX Desktop/ig, '<i class="fa-solid fa-circle-question"></i>')
    	gui = gui.replace(/SwapCase/ig, '<i class="fa-solid fa-circle-question"></i>')
    	gui = gui.replace(/ColliderDEX/ig, '<i class="fa-solid fa-circle-question"></i>')
    	gui = gui.replace(/Android/ig, '<i class="fa-brands fa-android"></i>')
    	gui = gui.replace(/iOS/ig, '<i class="fa-brands fa-apple"></i>')
    	gui = gui.replace(/Darwin/ig, '<i class="fa-brands fa-apple"></i>')
    	gui = gui.replace(/Windows/ig, '<i class="fa-brands fa-windows"></i>')
    	gui = gui.replace(/Linux/ig, '<i class="fa-brands fa-linux"></i>')
    	gui = gui.replace(/AtomicDEX/ig, get_coin_icon_only('DEX', '', 18, 'm-0'))
    	gui = gui.replace(/DogeDEX/ig, get_coin_icon_only('DOGE', '', 18, 'm-0'))
    	gui = gui.replace(/SmartDEX/ig, get_coin_icon_only('SMTF', '', 18, 'm-0'))
    	gui = gui.replace(/GleecDEX/ig, get_coin_icon_only('GLEEC', '', 18, 'm-0'))
    	gui = gui.replace(/FiroDEX/ig, get_coin_icon_only('FIRO', '', 18, 'm-0'))
    	gui = gui.replace(/ShibaDEX/ig, get_coin_icon_only('SHIB-BEP20', '', 18, 'm-0'))
    	gui = gui.replace(/BitcoinZ Dex/ig, get_coin_icon_only('BTCZ', '', 18, 'm-0'))
    	gui = gui.replace(/BitcoinZ/ig, get_coin_icon_only('BTCZ', '', 18, 'm-0'))
    	gui = gui.replace(/Unknown/ig, '?')
    	gui = gui.replace(/None/ig, '?')
    	return gui
	}

	function show_region(region) {
		const options = ["AR", "EU", "NA", "SH", "DEV"];
		show_card(region, options)
	}

	function get_api_button(id, width, url, text) {
		return '{% include "components/buttons/api_link_button.html" with btn_id="'+id+'" width_pct="'+width+'" btn_url="'+url+'" btn_text="'+text+'" %}'
	}

	function show_card(card_id, cards_list) {
		cards_list.forEach(function (i) {
			if (i == card_id) {
				$("#"+i).fadeTo(1000, 1)
				$("#"+i+"_btn").addClass('btn-selected')
			}
			else {
				$("#"+i).css('display', 'none')	
				$("#"+i+"_btn").removeClass('btn-selected')
			}
		});
	}

	function show_season(season) {
		const options = ["Season_4", "Season_5", "Season_6"];
		show_card(season, options)
	}

    function update_tabledata(table, endpoint, params)
    {
    	let new_url = endpoint+params
		table.ajax.url(new_url).load();
	}

	function get_param_join(url) {
    	if (url.search("\\?") > -1) return "&"
		return "?"
	}

	function get_coin_icons_from_list(coins_list, base_url='', active_coin='') {
		url = ''
    	let coin_icons = ''
    	let param_join = get_param_join(url)
    	for (let coin of coins_list) {
			if (base_url != '') {
				url = base_url + param_join + 'coin=' + coin
			}
			if (coin == active_coin) {
				coin_icons += get_coin_icon_only(coin, url, size=48, "m-2")
			}
			coin_icons += get_coin_icon_only(coin, url, size=24, "m-1 mute_on_hover")
    	}
        return coin_icons
	}

	function titleCase(str) {
	  return str.toLowerCase().split(' ').map(function(word) {
	    return word.replace(word[0], word[0].toUpperCase());
	  }).join(' ');
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

	function get_time_since(ts, until=false, format='text', precalc=false) {
		timestamp = parseInt(ts)
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

	function get_notaries_symbol(notaries, txid) {
		let tooltip_html = ""
		for (let notary of notaries) {
			tooltip_html += notary+"\n"
		}
		return "<a href='{% url 'notarisedViewSet-list' %}?txid="+txid+"'><span class='' style='font-size: 0.7em' data-bs-toggle='tooltip'\
					data-bs-placement='top' title=' "+tooltip_html+"'>\
		<i class='fa fa-users' style='font-size:1.5em;'></i>\
		</span></a>";
	}

	function get_coin_icon(coin, url) {
		if (coin == "TKL") coin = "TOKEL"
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


	function get_coin_icon_only(coin, url='', size=18, img_class="m-1") {
		if (dpow_coins.includes(coin)) {
			if (url == '') {
				url = "/coin_profile/" + coin
			}
		}
    	if (coin_icons.hasOwnProperty(coin)) {
        	return "<span class='' style='' data-toggle='tooltip' data-placement='top' title='"+coin+"'><a href='"+url+"'><img height='"+size+"px' class='"+img_class+"' src='"+coin_icons[coin]+"' /></a></span>";
        }
        else {
        	return "<span class='' style='' data-toggle='tooltip' data-placement='top' title='"+coin+"'><a href='"+url+"'><img height='"+size+"px' class='"+img_class+"' src='/static/img/notary/icon/blank.png' /></a></span>"
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

	function get_richlist_url(address) {
		return "<a href='https://dexstats.info/richlistlookup.php?address="
			+ address + "&bootstrap-data-table-1_length=-1'>"
			+ address + "</a>"
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


	function make_graph(graphtype, url, id) {
	    $.ajax({ 
			method: "GET", 
			url: '//{{ request.get_host }}/api/graph_json/balances/?coin={{ coin }}', 
			success: function(data) { 
				//document.getElementById('graph_title').innerHTML = data.chartLabel;
				if (graphtype == 'line') {
					drawLineGraph(data, 'myChartline');
				}
				else if (graphtype == 'bar') {
					drawBarGraph(data, 'myChartBar');
				}
			}, 
			error: function(error_data) { 
				console.log(error_data); 
			} 
	    }) 
	}

	function switch_combos(a,b) {
		val_a = $(a).val()
		val_b = $(b).val()
		$(a).val(val_b)
    	$(a).trigger('change')
		$(b).val(val_a)
    	$(b).trigger('change')
	}
	
    function add_dropdown_options(options, id, selected='') {
		var newOption = new Option('All', 'All', true, true);
		$(id).append(newOption).trigger('change');
		if (selected == 'All') {
    		$(id).val(selected)
    		$(id).trigger('change')				
		}
		$.each(options, function(i, p) {
			if (selected == p) {
				var newOption = new Option(p, p, true, true);
				$(id).append(newOption).trigger('change');
	    		$(id).val(selected)
	    		$(id).trigger('change')
	    	}
		    else {
				var newOption = new Option(p, p, false, false);
				$(id).append(newOption).trigger('change');
		    }				    
		});
	}

	function build_dropdowns(table, json, listtype) {
    	let distinct = json.distinct
    	let selected = json.selected
    	let required = json.required

        for (let cat of Object.keys(distinct)) {
			var options = distinct[cat];
			dropdown = '#'+table+'-'+cat+'-input'
			$(dropdown).empty();
			if (!Object.keys(required).includes(cat)) {
				if (!selected[cat]) {
					$(dropdown).append($('<option></option>').val('All').html('All'));
				}
				else {
					$(dropdown).append($('<option selected></option>').val('All').html('All'));
				}
			}
			if (cat == 'month' && selected[cat]) {
				let months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
							  'August', 'September', 'October', 'November', 'December']
				selected[cat] = months[selected[cat]+1]
			}
			$.each(options, function(i, p) {
				let label = format_notary(p)
				if (selected[cat]) {
					if (selected[cat] == p) {
			    		$(dropdown).append($('<option selected></option>').val(p).html(label));
			    	}
				    else {
				    	$(dropdown).append($('<option></option>').val(p).html(label));
				    }
			    }
			    else if (Object.keys(required).includes(cat)) {
			    	$(dropdown).append($('<option selected></option>').val(p).html(label));
			    }
			    else {
			    	$(dropdown).append($('<option></option>').val(p).html(label));
			    }
			});
		}
	}

	function get_richlist_celldata(addresses) {
		let linked_addresses = []
		$.each(addresses, function(i, p) {
			linked_addresses.push(
				get_richlist_url(addresses[i])
			)
		})
		return linked_addresses.join("<br />")
	}

	function get_region_scoreboard_table(season, region, url, title='') {

		const dom = '<"row mx-0 p-0 my-2 "<"row '+region+'_notarisations-tbl-title col-md-6 p-0 m-0"><"col-sm-12 col-md-6"f>>tr<"row mx-0 p-0 my-2 d-flex justify-content-between"<"'+region+'_notarisations-api-link">ip>'
	    table = $('#'+region+'_notarisations').DataTable({
	    	"paging": false,
	        "orderClasses": false,
			order: [[ 0, 'asc' ]],
	    	"columns": [
		        { "data": "rank" },
		        { "data": "notary" },
		        { "data": "master" },
		        { "data": "main" },
		        { "data": "third_party" },	
		        { "data": "seed" },	
		        { "data": "mining" },
		        { "data": "score" }
		    ],
			"columnDefs": [
				{ className: "text-left text-nowrap", "targets": [ 1 ] },
				{ className: "text-right text-nowrap", "targets": [ 2,3,4,5,6,7 ] },
				{
		            "targets": 1,
		            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
		            	$(nTd).html(get_notary_url(season, oData.notary));
			        }
		        },
				{
		            "targets": 7,
		            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
			            $(nTd).html((Math.round(oData.score*100, 2)/100).toFixed(2));
			        }
		        }
			],
			dom: dom,
			fnInitComplete: function(){
	            $('.'+region+'_notarisations-tbl-title').html('<h5 class="text-left">'+title+'</h5>');
	            if (url != '') {
	    	        let api_btn = '{% include "components/buttons/api_link_button.html" with btn_id="'+region+'_notarisations" width_pct="100" btn_url="'+url+'" btn_text="Source Data" %}'
		            $('.'+region+'_notarisations-api-link').html(api_btn);
		        }
			}
	    });

	    // TODO: review highlights here
	    var max = table.column(6).data()[0]
	    table.rows().every( function (index) {
	    	var row = table.row(index);
		    var d = row.data();
		    if (d.score > max/3) {
		    	row.nodes().to$().addClass( 'kmd_secondary_purple' );
		    }
		});
	    highlight_notaries(table)
		return table
	}

	function get_className(header) {
		switch(header) {

			case 'Ntx Count %':
			case 'Ntx Score %':
			case 'Ntx Score':
			case 'Biggest Block':
			case 'Score':
			case 'Total Count':
			case 'Ntx Count':
		    case 'Since':
			case 'Since Updated':
		    case 'Updated':
			case 'Last Block':
			case 'Block Height':
			case 'Ntx Height':
			case 'SC Height':
		    case 'Balance':
			case 'USD Value':
			case 'Category':
			case 'Fees':
			case 'Inputs':
			case 'Input Index':
			case 'Sent':
			case 'Outputs':
			case 'Output Index':
			case 'Received':
			case 'Rewards':
			case 'KMD Value':
			case 'KMD Mined':
			case 'Blocks Mined':
			case 'Time Since':
			    return "text-right text-nowrap"

			case 'Mined By':
			case 'Notary':
			case 'Coin':
			case 'Season':
			case 'Server':
			case 'Epoch':
		    case 'Name':
			    return "text-left text-nowrap"

		    // Function derived cells //
		    
			case 'Epoch Coins':
			    return "fixed-width-28"

			case 'Ntx Txid':
			case 'Notaries':
			case 'OP Return':
			    return "text-center text-nowrap fw-14pct"

		    default:
		    	return "text-center text-nowrap"
		}
	}
	
	function isNotary(name) {
		{% autoescape off %}
			return ({{ notaries }}).includes(name)
		{% endautoescape %}
	}
	
	function isMiningPool(name) {
		return (name).includes("Mining Pool")
	}

	function get_miningpool_url(name) {
		switch(name) {
			case "k1pool (Mining Pool)":
				url = "https://k1pool.com/pool/kmd"
				break

			case "ZPool (Mining Pool)":
				url = "https://zpool.ca/coins"
				break

			case "LuckPool (Mining Pool)":
				url = "https://luckpool.net/"
				break

			case "Mining-Dutch (Mining Pool)":
				url = "https://www.mining-dutch.nl/"
				break

			case "MiningFool (Mining Pool)":
				url = "https://kmd.miningfool.com/"
				break

			case "ZergPool (Mining Pool)":
				url = "https://zergpool.com/site/block?coin=KMD"
				break

			case "CoolMine (Mining Pool)":
				url = "https://coolmine.top/?coin=4"
				break

			case "Luxor (Mining Pool)":
				url = "https://mining.luxor.tech/"
				break

			case "ProHashing (Mining Pool)":
				url = "https://prohashing.com/"
				break

			case "SoloPool (Mining Pool)":
				url = "https://kmd.solopool.org/"
				break

		    default:
		    	return name

		}
   		return "<a class='' href='"+url+"'>\
   			<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='Go to "+url+"'>"+name+"</span></a>";
	}

	function get_columnDefs(columns) {
		
		columnDefs = []
		let i = 0
	    for (let [key,header] of Object.entries(columns)) {
	    	visible = header == "" ? false : true
			columnDefs.push({
	            "targets": i,
	            "data": key,
	            "visible": visible,
	            "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {

			    	switch(header) {

						case 'KMD to LTC':
						case 'Main to KMD':
						case '3P to KMD':
							val = "<a href='/table/notarised/?hide_filters=1&date="+oData.notarised_date+"&notary="+oData.notary+"'>"+parseInt(oData[key])+"</a>"
					    	break

						case 'Season Count':
						case 'Season Score':
							text = header =='Season Count' ? parseInt(oData[key]) : parseFloat(oData[key]).toFixed(3)
							if (oData.server) {
								val = "<a href='/table/notarised_coin_daily/?hide_filters=1&season="+oData.season+"&server="+oData.server+"'>"+text+"</a>"
							}
							else if (oData.notary) {
								val = "<a href='/table/notarised_count_daily/?hide_filters=1&season="+oData.season+"&notary="+oData.notary+"'>"+text+"</a>"
							}
							else if (oData.coin) {
								val = "<a href='/table/notarised_coin_daily/?hide_filters=1&season="+oData.season+"&coin="+oData.coin+"'>"+text+"</a>"
							}
							else {
								 val = text
							}
					    	break

						case 'Ntx Count %':
						case 'Ntx Score %':
						    val = parseFloat(oData[key]).toFixed(3) + "%"
					    	break

						case 'Ntx Count':
						case 'Ntx Score':
							text = header =='Ntx Count' ? parseInt(oData[key]) : parseFloat(oData[key]).toFixed(8)
							if (oData.notary) {
								val = "<a href='/table/notarised/?hide_filters=1&coin="+oData.coin+"&date="+oData.notarised_date+"'>"+text+"</a>"
							}
							else if (oData.coin) {
								val = "<a href='/table/notarised/?hide_filters=1&coin="+oData.coin+"&date="+oData.notarised_date+"'>"+text+"</a>"
							}
							else {
								 val = text
							}
					    	break
					    
						case 'Address':
						case 'Address / Pubkey':
					    case 'Name':
					    case 'Balance':
					    	coin = oData.coin
					    		? oData.coin : "KMD"

					    	if (oData.output_addresses) {
					    		val = get_richlist_celldata(oData.output_addresses)
					    	}
					    	else {
					    		text = oData.balance && header != "Address"
							    	? parseFloat(oData.balance).toFixed(4) : oData.name
							    	? oData.name : oData.address
						    	val = get_address_url(coin, oData.address, text)
						    	val = oData.pubkey 
							    	? val+"<br /><span style='font-size:0.8em; font-style: italic;'>"+oData.pubkey+"</span>" : val
					    	}
					    	break

						case 'Blocks Mined':
						case 'Sum Mined':
							text = header =='Sum Mined' ? parseFloat(oData[key]).toFixed(8) : parseInt(oData[key])
							val = oData.last_mined_block
							? "<a href='/table/mined/?hide_filters=1&season="+oData.season+"&name="+oData.name+"'>"+text+"</a>" : oData.mined_date && oData.notary
							? "<a href='/table/mined/?date="+oData.mined_date+"&name="+oData.notary+"'>"+text+"</a>" : text
					    	break

						case 'Mined By':
						case 'Notary':
							let name = oData.name ? oData.name : oData.notary ? oData.notary : ""
							val = isNotary(name)
								? get_notary_url(oData.season, name) : isMiningPool(name)
								? get_miningpool_url(name) : oData.address && oData.coin 
			            		? get_address_url(oData.coin, oData.address, name) : oData.address && oData.name 
			            		? get_address_url("KMD", oData.address, name) : oData.input_sats
			            		? get_address_url("LTC", oData.address, name) : get_notary_url(oData.season, name)
					    	break

						case 'Last Block':
						case 'Block Height':
						case 'Ntx Height':
						case 'SC Height':
						    coin = header == 'SC Height'
						    	? oData.coin : oData.output_sats
						    	? "LTC" : "KMD"
					    	val = get_block_url(coin, oData[key])
					    	break

						case 'Ntx Txid':
						case 'Biggest Block':
						    val = oData.max_value_txid
						    	? get_txid_url("KMD", oData.max_value_txid, parseFloat(oData[key]).toFixed(8)) : oData.kmd_ntx_txid
						    	? get_txid_url("KMD", oData[key]) : parseFloat(oData[key]).toFixed(8)
					    	break

						case 'USD Value':
					    	val = oData.value
					    		? oData.value : oData.rewards_value
					    		? oData.rewards_value : oData.sum_value_mined
					    		? oData.sum_value_mined : 1
							val = "$USD " + (oData.usd_price * val).toFixed(2)
					    	break

						
						case 'Sent':
						case 'Fees':
							val = get_txid_url("LTC", oData['txid'], oData[key]/100000000)
							break

						case 'Rewards':
						case 'Received':
						case 'KMD Mined':
						case 'KMD Value':
						    val = ["KMD Mined", "Rewards"].includes(header)
						    	? parseFloat(oData[key]) : parseInt(oData[key])
					    	val = isNaN(val)
					    		? val
					    		: val >= 0 && ["KMD Mined", "Rewards"].includes(header)
					    		? "<a href='https://komodod.com/t/"+oData.txid+"'>"+(val).toFixed(8)+"</a>"
					 		   		: val >= 0 && ["Sent", "Received", "Fees", "KMD Value"].includes(header)
					    		? "<a href='https://komodod.com/t/"+oData.txid+"'>"+(val/10000000).toFixed(8)+"</a>"
					    		: "-"
					    	break

						case 'Inputs':
						case 'Input Index':
						case 'Outputs':
						case 'Output Index':
			    			val = parseInt(oData[key])
			    			val = val < 0 ? "-" : val
					    	break

					    case 'Time Since':
					    case 'Since Updated':
					    	val = get_time_since(oData[key])
					    	break

						case 'Time UTC':
						    val = oData[key].split("T")[1].replace("Z", "")
					    	break

						case 'Total Count':
						    val = parseInt(oData[key])
					    	break

						case 'OP Return':
					    	val = get_opret_link(oData[key])
					    	break

			    		case 'Season':
					    	val = get_season_styled(oData[key])
					    	break

						case 'Server':
					    	val = get_server_styled(oData[key])
					    	break

						case 'Epoch': 
					    	val = get_epoch_styled(oData[key])
					    	break

						case 'Epoch Coins':
					    	val = get_epoch_coins(oData[key])
					    	break

						case 'Coin':
					    	val = get_coin_icon(oData[key])
					    	break

						case 'Notaries':
					    	val = get_notaries_symbol(oData.notaries, oData.txid)
					    	break

					    default:
			    			val = oData[key]
					    	break
			        }
					$(nTd).html(val)
    			},
    			"className": get_className(header)
		    })
    		i++;			
	    }

	    return columnDefs
	}

	function get_opret_link(opret) {
		let op_return = (opret.split(" ").length > 1) ? opret.split(" ")[1] : opret
		let icon = "<i class='fas fa-arrow-right'></i>"
		let tooltip = "Decode OP_RETURN: "+op_return
		let url = "{% url 'decode_op_return_view' %}?OP_RETURN="+op_return+"&season={{ season }}"
		return get_detail_link_icon(icon, tooltip, url)
	}

	function refresh_table(table, endpoint, filters, required) {
	    let params = get_params(table, filters, required)
	    let url = endpoint+params
		window.tables[table+"_table"].ajax.url(url).load();
        let api_btn = '{% include "components/buttons/api_link_button.html" with btn_id="{{ table }}" width_pct="100" btn_url="'+url+'" btn_text="Source Data" %}'
        $('.{{ table }}-api-link').html(api_btn);
	}

	function get_params(table, param_list, required, selected, no_filter) {
		let params = {}
		if (selected) {
			for (let x of Object.keys(selected)) {
				if (!["All", undefined, null, ""].includes(selected[x])) params[x] = selected[x]
			}
		}
		if (!no_filter) {
			
			for (let x of param_list) {
				if (!Object.keys(params).includes(x)) {
					val = $("#"+table+"-"+x+"-input").val()
					if (!["All", undefined, null, ""].includes(val)) params[x] = val
				}
			}
			
			for (let x of Object.keys(required)) {
				if (!Object.keys(params).includes(x)) {
					if (!["All", undefined, null, ""].includes(required[x])) params[x] = required[x]
				}
			}
		}
		param_list = []
		for (let x of Object.keys(params)) {
			param_list.push(x+"="+params[x])
		}
		
		return "?" + param_list.join("&")
	}

	function reset_inputs(table, param_list, required) {
		for (let x of param_list) {
			if (Object.keys(required).includes(x)) {
				$("#"+table+"-"+x+"-input").val(required[x])
			}
			else if ($("#"+table+"-"+x+"-input").val() != "All") {
				$("#"+table+"-"+x+"-input").val("All")
			}
		}
		$("#"+table+"-"+param_list[0]+"-input").trigger('change');
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

	function titlecase(string) {
	  return string.charAt(0).toUpperCase() + string.slice(1);
	}

	function format_notary(notary) {
		if (notary) {
			x = notary.split("_")
			if (x.length > 1) {
				return titlecase(x.slice(0,-1).join("_")) + " " + x.slice(-1)
			}
			return titlecase(notary)
		}
		return notary
	}

	function get_notary_url(season, notary) {
		notary_txt = format_notary(notary)
		return "<a href=\"{% url 'notary_profile_index_view' %}"+notary+"/?season="+season+"\">"+notary_txt+"</a>"
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

	function get_rewards_tables() {
		let address = $('#address').val()
		let url = "/api/source/rewards_tx/?address={"+address+"}"
 		rewards_history_table.ajax.url(url).load();
	}

    // Custom DataTables search filter input styling
    function update_dt_search(id) {
        filter_div = `{% include "components/form/dt_search.html" %}`
        //<div class="col-6 input-group-prepend px-0 ml-auto"><span class="input-group-text col-4">Search: </span><input type="search" class="col-8 ml-0 mr-3 form-control form-control-sm" placeholder="" aria-controls="'+id+'"></div>'
        $("#"+id+"_filter").html(filter_div)
        $("#"+id+"_filter").addClass('ml-auto')
        $("#"+id+"_filter").on("keyup", 'input', function() {
            $("#"+id).DataTable().search(this.value.trim(), false, false).draw();
        });
    }

    function update_dt_length(id) {

        custom_select = '<div class="col-6 input-group-prepend px-0 mr-auto"><span class="input-group-text col-4">Show </span><select id="tbl_select" name="'+id+'_length" aria-controls="'+id+'" class="custom-select custom-select-sm form-control form-control-sm"><option value="10">10</option><option value="25" selected>25</option><option value="50">50</option><option value="100">100</option></select><span class="input-group-text std-append col-4"> Rows</span></div>'
        $("#"+id+"_length").html(custom_select)
        $("#"+id).DataTable().page.len(50).draw();
        $("#tbl_select").on("change", function() {
            $("#"+id).DataTable().page.len(parseInt(this.value)).draw();
        });
    }

    function tables_refresh_rate(seconds, countdown, tables) {
        let timer_increment = seconds
        setInterval( function () {
            timer_increment -= 1
            $(countdown).html(timer_increment)
            if (timer_increment == 0) {
            	for (let table of tables) {
					table.ajax.reload();
				}
				timer_increment = seconds
             }
        }, 1000 );
    }
    		function floorRound (num, num_dec) {
		    var dp = parseInt("1" + "0".repeat(num_dec));
		    num = parseFloat(num)
			num = Math.floor(num * dp);
		    return num / dp;
		}

		function get_fees(coin='KMD', size=80, sat_per_byte=10) {
			return 0.0001
		}

		function get_unallocated(address_rows) {
			sum_selected = floorRound(parseFloat($("#sum_selected").html()), 5)
			sum_outputs = get_sum_outputs(address_rows)
			fees = get_fees()
			unallocated = sum_selected - sum_outputs - fees
			return unallocated
		}

		function spendMax(id) {
			unallocated = get_unallocated($(id).parent())
			output_amount = parseFloat($(id).val())
			$(id).val(floorRound(output_amount+unallocated,5))
			sanitize_outputs()
		}

		function get_sum_outputs(address_rows) {
			num_rows = $(address_rows).children().length;
			sum_outputs = 0
			for (var i = 0; i < num_rows; i++) {
				output_amount = $("#output_amount_"+i).val()
				if (!($.isNumeric(output_amount))) {
					output_amount = 0
					$("#output_amount_"+i).val(0)
				}
				sum_outputs += parseFloat(output_amount)
			}
			return floorRound(sum_outputs,5)
		}

    	function zero_NaN(num) {
			if (!($.isNumeric(output_amount))) {
				return 0
			}
			else {
				return parseFloat(num)
			}

    	}

		function sanitize_outputs(address_rows='#output_addresses') {
			sum_selected = floorRound(parseFloat($("#sum_selected").html()),5)
			sum_outputs = get_sum_outputs(address_rows)
			fee_val = sum_selected - sum_outputs
			$("#fee_val").html(floorRound(fee_val,5))
			$("#total_val").html(sum_outputs+fee_val)
			/* if fees > 0.001 , red text warning, disable submit */
			/* if remaining < 0 , red text warning, disable submit */		
		}
</script>
