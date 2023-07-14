
<script>

    function get_link(url, text) {
        return "<a href='"+url+"'>"+text+"</a>"
    }

	function get_faucet_txid(coin, txid) {
		if (txid == 'n/a') {
        	return "<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='Awaiting drip...'><i class='fas fa-hourglass-half' style='color:white'></i></i></span>";
    	} else {
        	return get_txid_url(coin, txid);
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

    function get_richlist_url(address) {
        return "<a href='https://dexstats.info/richlistlookup.php?address="
            + address + "&bootstrap-data-table-1_length=-1'>"
            + address + "</a>"
    }

    function get_address_url(coin, address, label, max_length=34) {
        let explorer = get_explorer(coin)
        if (!label) {
            label = address
        }
        if (label.length > max_length) {
            label = address.substring(0, max_length-3) + "..."
        }
        // TODO: Using the explorer suffix data from coins_config.json would expland coverage here.
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


    function get_opret_link(opret) {
        let op_return = (opret.split(" ").length > 1) ? opret.split(" ")[1] : opret
        let icon = "<i class='fas fa-arrow-right'></i>"
        let tooltip = "Decode OP_RETURN: "+op_return
        let url = "{% url 'decode_op_return_view' %}?OP_RETURN="+op_return+"&season={{ season }}"
        return get_detail_link_icon(icon, tooltip, url)
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

    function get_notary_url(season, notary) {
        notary_txt = format_notary(notary)
        return "<a href=\"{% url 'notary_profile_index_view' %}"+notary+"/?season="+season+"\">"+notary_txt+"</a>"
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

</script>