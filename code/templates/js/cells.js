<!-- cells.js -->
<script>

function get_faucet_status(status) {
    if (status == 'pending') {
        return "<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='In queue...'><i class='far fa-clock' style='color:white;'></i></span>";		            		
    } else if (status == 'sent') {
        return "<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='Sent!'><i class='fas fa-envelope-open-text' style='color:white;'></i></span>";
    } else {
        return "<span class='p-0' style='border-radius: 50%;' data-toggle='tooltip' data-placement='top' title='In queue...'><i class='far fa-clock' style='color:white;'>"+status+"<i class='far fa-clock' style='color:white;'></i></span>";
    }		
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

function get_qrcode(id, text, title, subtitle) {
    $(id).html('')
    jQuery(id).qrcode({foreground:"#070e28", background:"#b1d1d3", "text":text});
    $('#qrcode-modal-label').html(title)
    $('#qrcode-modal-subtitle').html(subtitle)
}

</script>
