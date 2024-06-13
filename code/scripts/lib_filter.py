#!/usr/bin/env python3.12


def sorted_list_set(list_obj):
    list_obj = list(set(list_obj))
    list_obj.sort()
    return list_obj


def get_notarised_conditions_filter(sql, **kwargs):
    conditions = []
    group_by_condition = None
    order_by_condition = None
    for k,v in kwargs.items():
        if v:
            if k == "notary":
                conditions.append(f"'{v}' = ANY (notaries)")
            elif k == "include_coins":
                v = str(v)[1:-1]
                conditions.append(f"'coin' IN ({v})")
            elif k == "exclude_coins":
                v = str(v)[1:-1]
                conditions.append(f"'coin' NOT IN ({v})")
            elif k == "exclude_server_unofficial":
                if v:
                    conditions.append(f"server != 'Unofficial'")
            elif k == "group_by":
                group_by_condition = v
            elif k == "order_by":
                order_by_condition = v
            elif k == "lowest_blocktime":
                conditions.append(f"block_time >= '{v}'")
            elif k == "highest_blocktime":
                conditions.append(f"block_time <= '{v}'")
            elif k == "lowest_blockheight":
                conditions.append(f"block_height >= '{v}'")
            elif k == "highest_blockheight":
                conditions.append(f"block_height <= '{v}'")
            elif k == "lowest_ac_blockheight":
                conditions.append(f"ac_ntx_height >= '{v}'")
            elif k == "highest_ac_blockheight":
                conditions.append(f"ac_ntx_height <= '{v}'")
            elif isinstance(k, str):
                if k.startswith("not_"):
                    conditions.append(f"{k.split('_')[1]} != '{v}'")
                else:
                    conditions.append(f"{k} = '{v}'")
            elif isinstance(k, int) or isinstance(k, float):
                conditions.append(f"{k} = {v}")
    if len(conditions) > 0:
        sql += " WHERE " + " AND ".join(conditions)
    if group_by_condition:
        sql += f" GROUP BY {group_by_condition}"
    if order_by_condition:
        sql += f" ORDER BY {order_by_condition}"
    sql += ";"
    return sql


def simple_filter(sql, **kwargs):
    conditions = []
    for k, v in kwargs.items():
        if v:
            if isinstance(k, str):
                conditions.append(f"{k} = '{v}'")
            elif isinstance(k, int) or isinstance(k, float):
                conditions.append(f"{k} = {v}")
    if len(conditions) > 0:
        sql += " WHERE "
        sql += " AND ".join(conditions)    
    sql += ";"
    return sql
