{{ mm2_coins|json_script:"mm2_coins-data" }}
<!-- mm2_coins.js -->
<script>
	var mm2_coins = JSON.parse(document.getElementById('mm2_coins-data').textContent);
</script>
