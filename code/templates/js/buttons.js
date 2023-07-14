<!-- buttons.js -->
<script>
function get_api_button(id, width, url, text) {
    return '{% include "components/buttons/api_link_button.html" with btn_id="'+id+'" width_pct="'+width+'" btn_url="'+url+'" btn_text="'+text+'" %}'
}
</script>
