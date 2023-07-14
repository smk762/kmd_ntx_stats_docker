<!-- components.js -->

<script>

function show_region(region) {
    const options = ["AR", "EU", "NA", "SH", "DEV"];
    show_card(region, options)
}

function show_card(card_id, cards_list) {
    cards_list.forEach(function (i) {
        if (i == card_id) {
            $("#"+i).fadeTo(1000, 1)
            $("#"+i+"_btn").addClass('btn-selected')
        }
        else {
            $("#"+i).css('display', 'none')	
            $("#"+i+"_btn").removeClass('btn-selected')
        }
    });
}

function show_season(season) {
    const options = ["Season_4", "Season_5", "Season_6", "Season_7"];
    show_card(season, options)
}

function switch_combos(a,b) {
    val_a = $(a).val()
    val_b = $(b).val()
    $(a).val(val_b)
    $(a).trigger('change')
    $(b).val(val_a)
    $(b).trigger('change')
}

function add_dropdown_options(options, id, selected='') {
    var newOption = new Option('All', 'All', true, true);
    $(id).append(newOption).trigger('change');
    if (selected == 'All') {
        $(id).val(selected)
        $(id).trigger('change')				
    }
    $.each(options, function(i, p) {
        if (selected == p) {
            var newOption = new Option(p, p, true, true);
            $(id).append(newOption).trigger('change');
            $(id).val(selected)
            $(id).trigger('change')
        }
        else {
            var newOption = new Option(p, p, false, false);
            $(id).append(newOption).trigger('change');
        }				    
    });
}

function build_dropdowns(table, json, listtype) {
    let distinct = json.distinct
    let selected = json.selected
    let required = json.required

    for (let cat of Object.keys(distinct)) {
        var options = distinct[cat];
        dropdown = '#'+table+'-'+cat+'-input'
        $(dropdown).empty();
        if (!Object.keys(required).includes(cat)) {
            if (!selected[cat]) {
                $(dropdown).append($('<option></option>').val('All').html('All'));
            }
            else {
                $(dropdown).append($('<option selected></option>').val('All').html('All'));
            }
        }
        if (cat == 'month' && selected[cat]) {
            let months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                          'August', 'September', 'October', 'November', 'December']
            selected[cat] = months[selected[cat]+1]
        }
        $.each(options, function(i, p) {
            let label = format_notary(p)
            if (selected[cat]) {
                if (selected[cat] == p) {
                    $(dropdown).append($('<option selected></option>').val(p).html(label));
                }
                else {
                    $(dropdown).append($('<option></option>').val(p).html(label));
                }
            }
            else if (Object.keys(required).includes(cat)) {
                $(dropdown).append($('<option selected></option>').val(p).html(label));
            }
            else {
                $(dropdown).append($('<option></option>').val(p).html(label));
            }
        });
    }
}

</script>
