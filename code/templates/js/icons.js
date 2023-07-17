
{{ coin_icons|json_script:"coin_icons-data" }}
{{ notary_icons|json_script:"notary_icons-data" }}
{{ dpow_coins|json_script:"dpow_coins-data" }}
{{ notaries|json_script:"notaries-data" }}
<!-- icons.js -->
<script>
	var coin_icons = JSON.parse(document.getElementById('coin_icons-data').textContent);
	var notary_icons = JSON.parse(document.getElementById('notary_icons-data').textContent);
	var dpow_coins = JSON.parse(document.getElementById('dpow_coins-data').textContent);
	var notaries = JSON.parse(document.getElementById('notaries-data').textContent);


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


	function get_detail_link_icon(icon, tooltip, url) {
		return "<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='"+tooltip+"'> \
			<a href='"+url+"'>"+icon+"</i></a>\
		</span>"
	}
	

	function get_epoch_coins(epoch_coins) {
    	let coin_icons = ''
    	for (let coin of epoch_coins) {
    		coin_icons += get_coin_icon_only(coin)
    	}
        return coin_icons;
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
    
        
</script>
