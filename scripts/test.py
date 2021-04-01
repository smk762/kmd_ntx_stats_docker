#!/usr/bin/env python3
from lib_table_select import get_tenure_chains
from lib_notary import get_dpow_scoring_window

get_tenure_chains("Season_4", "Third_Party")

official_start, official_end, scored_list, unscored_list = get_dpow_scoring_window("Season_4", "GLEEC", "Third_Party")

get_tenure_chains("Season_4", "Main")
official_start, official_end, scored_list, unscored_list = get_dpow_scoring_window("Season_4", "GLEEC", "Main")

get_tenure_chains("Season_4", "Unoffical")
official_start, official_end, scored_list, unscored_list = get_dpow_scoring_window("Season_4", "GLEEC", "Unoffical")