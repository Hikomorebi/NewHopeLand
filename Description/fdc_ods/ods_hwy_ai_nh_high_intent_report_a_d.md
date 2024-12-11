- 数据表名称
fdc_ods.ods_hwy_ai_nh_high_intent_report_a_d

- 数据表解释
高意向报告表，用于记录意向客户相关数据。

- 各字段说明
| 字段名                  | 数据类型                     | 描述                        |
| ----------------------- | ---------------------------- | --------------------------- |
| id                      | varchar                      | 主键                        |
| phone                   | varchar                      | 销售人员手机号                    |
| name                    | varchar                      | 销售人员姓名                    |
| role_id                 | varchar                      | 角色ID                      |
| role_name               | varchar                      | 角色名称                    |
| project_id              | varchar                      | 项目ID                      |
| project_name            | varchar                      | 项目名称                    |
| report_type             | varchar                      | 报告类型:新访、复访、高意向 |
| customer_name           | varchar                      | 客户名称                    |
| customer_phone          | varchar                      | 客户手机号                  |
| intention_degree        | varchar                      | 意向度                      |
| intention_level         | varchar                      | 意向等级                    |
| transaction_stuck_point | longtext                     | 成交卡点                    |
| follow_up_suggestions   | longtext                     | 跟进建议                    |
| report_date             | datetime                     | 报告日期                    |
| ext_json                | longtext                     | 扩展信息                    |
| delete_flag             | varchar                      | 删除标志                    |
| create_time             | datetime                     | 创建时间                    |
| create_user             | varchar                      | 创建用户                    |
| update_time             | datetime                     | 修改时间                    |
| update_user             | varchar                      | 修改用户                    |
| partitiondate           | timestamp without  time zone | 分区日期                    |

- 查询须知
1. 意向等级分为A、B、C、D、E，其中A、B为高意向等级，若问题涉及高意向客户，请通过 intention_level LIKE '%A%' or intention_level LIKE '%B%' 查询。
2. 注意name代表销售人员姓名，customer_name代表客户姓名