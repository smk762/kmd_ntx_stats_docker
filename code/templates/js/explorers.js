{{ explorers|json_script:"explorers-data" }}
<!-- explorers.js -->
<script>
	var explorers = JSON.parse(document.getElementById('explorers-data').textContent);
</script>
