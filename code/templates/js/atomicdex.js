<!-- atomicdex.js -->
<script>

function get_bestorders_url() {
    let coin = $('#coin').val() == undefined ? 'KMD' :  $('#coin').val()
    return "/api/table/bestorders/?coin=" + coin
}

function get_orderbook_table_url() {
    let base = $('#base').val() == undefined ? '{{ base }}' :  $('#base').val()
    let rel = $('#rel').val() == undefined ? '{{ rel }}' :  $('#rel').val()
    let url = "/api/table/orderbook/?base="+base+"&rel="+rel
    return url
}


</script>