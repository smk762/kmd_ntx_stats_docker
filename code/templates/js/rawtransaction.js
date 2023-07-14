<!-- rawtransaction.js -->
<script>
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

function sanitize_outputs(address_rows='#output_addresses') {
    sum_selected = floorRound(parseFloat($("#sum_selected").html()),5)
    sum_outputs = get_sum_outputs(address_rows)
    fee_val = sum_selected - sum_outputs
    $("#fee_val").html(floorRound(fee_val,5))
    $("#total_val").html(sum_outputs+fee_val)
    /* if fees > 0.001 , red text warning, disable submit */
    /* if remaining < 0 , red text warning, disable submit */		
}

function get_fees(coin='KMD', size=80, sat_per_byte=10) {
    return 0.0001
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

</script>