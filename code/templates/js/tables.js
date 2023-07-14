<!-- tables.js -->
<script>
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

function update_tabledata(table, endpoint, params)
{
    let new_url = endpoint+params
    table.ajax.url(new_url).load();
}

</script>