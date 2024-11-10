from auto_select_tables import select_table_based_on_query


# 示例查询
query = "查询广佛锦官半岛在2022年的首访人数是多少，给出具体值 "
selected_table = select_table_based_on_query(query)

print(selected_table)