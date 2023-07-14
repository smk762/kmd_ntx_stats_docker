<!-- styles.js -->
<script>
function get_className(header) {
    switch(header) {

        case 'Ntx Count %':
        case 'Ntx Score %':
        case 'Ntx Score':
        case 'Biggest Block':
        case 'Score':
        case 'Total Count':
        case 'Ntx Count':
        case 'Since':
        case 'Since Updated':
        case 'Updated':
        case 'Last Block':
        case 'Block Height':
        case 'Ntx Height':
        case 'SC Height':
        case 'Balance':
        case 'USD Value':
        case 'Category':
        case 'Fees':
        case 'Inputs':
        case 'Input Index':
        case 'Sent':
        case 'Outputs':
        case 'Output Index':
        case 'Received':
        case 'Rewards':
        case 'KMD Value':
        case 'KMD Mined':
        case 'Blocks Mined':
        case 'Time Since':
            return "text-right text-nowrap"

        case 'Mined By':
        case 'Notary':
        case 'Coin':
        case 'Season':
        case 'Server':
        case 'Epoch':
        case 'Name':
            return "text-left text-nowrap"

        // Function derived cells //
        
        case 'Epoch Coins':
            return "fixed-width-28"

        case 'Ntx Txid':
        case 'Notaries':
        case 'OP Return':
            return "text-center text-nowrap fw-14pct"

        default:
            return "text-center text-nowrap"
    }
}


function titlecase(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }

  function format_notary(notary) {
      if (notary) {
          x = notary.split("_")
          if (x.length > 1) {
              return titlecase(x.slice(0,-1).join("_")) + " " + x.slice(-1)
          }
          return titlecase(notary)
      }
      return notary
  }


  function get_season_styled(season) {
      if (season == "Season_5") {
          color = "#1e5ead";
      }
      else if (season == "Season_5_Testnet") {
          color = "#622C7B";
      }
      else if (season == "Season_4") {
          color = "#000";
      }
      else if (season == "Season_3") {
          color = "#8A510D";
      }
      else if (season == "Season_2") {
          color = "#622C7B";
      }
      else if (season == "Season_1") {
          color = "#802F5A";
      }
      else {
          color = "#000";	
      }
      return season.replace(/_/g, " ")
  }

  function get_server_styled(server) {
      if (server == "Main") {
          color = "#115621";
          server = "Main"
      }
      else if (server == "Third_Party") {
          color = "#2b53ad";
          server = "3P"
      }
      else if (server == "Testnet") {
          color = "#622C7B";
          server = "Testnet"
      }
      else {
          server = server
          color = "#000";	
      }
      return server
  }

  function get_epoch_styled(epoch) {
      if (epoch != "Unofficial") {
          return "<span class='' data-toggle='tooltip' data-placement='top' title='"+epoch+"'>"+epoch.replace('Epoch_','')+"</span>";
      }
      else {	
          return "<span data-toggle='tooltip' data-placement='top' title='"+epoch+"'><i class='bi bi-exclamation-triangle-fill'></i>";
      }
  }

</script>