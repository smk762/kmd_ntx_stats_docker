<!-- helper.js -->
<script>

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

	function titleCase(str) {
        return str.toLowerCase().split(' ').map(function(word) {
          return word.replace(word[0], word[0].toUpperCase());
        }).join(' ');
    }

    function isMiningPool(name) {
        return (name).includes("Mining Pool")
    }

    function remove_node(id) {
        $(id).remove()
    }

    function get_param_join(url) {
        if (url.search("\\?") > -1) return "&"
        return "?"
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

	function floorRound (num, num_dec) {
		var dp = parseInt("1" + "0".repeat(num_dec));
		num = parseFloat(num)
		num = Math.floor(num * dp);
		return num / dp;
	}


	function zero_NaN(num) {
		if (!($.isNumeric(output_amount))) {
			return 0
		}
		else {
			return parseFloat(num)
		}

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

	function isNotary(name) {
		{% autoescape off %}
			return ({{ notaries }}).includes(name)
		{% endautoescape %}
	}

</script>
