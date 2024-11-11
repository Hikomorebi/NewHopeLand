- 数据表名称
fdc_ads.ads_salesreport_subscranalyse_a_min

- 数据表解释

经营分析认购分析表。

- 各字段说明

| 字段名               | 数据类型                        | 描述                         |
| -------------------- | ------------------------------- | ---------------------------- |
| statdate             | timestamp(0)  without time zone | 统计日期                     |
| orgtype              | character varying               | 组织类型                     |
| orgcode              | character  varying              | 组织编码                     |
| orgname              | character  varying              | 组织名称                     |
| timespancode         | character varying               | 时间范围编码                 |
| subunsign_amount     | numeric                         | 认购未签金额                 |
| subunsign_amount_qyh | numeric                         | 认购未签金额权益后           |
| subunsign_num        | integer                         | 认购未签套数                 |
| subtosign_num        | integer                         | 认购转签约套数               |
| subtosign_period     | numeric                         | 认购转签约平均周期           |
| newvisittosub_num    | integer                         | 首访到认购套数               |
| newvisittosub_period | numeric                         | 首访到认购平均周期           |
| channel              | character varying               | 通路                         |
| cycletype            | character varying               | 周期类型 W-周 M-月 Q-季 Y-年 |
| visitornum           | integer                         | 总来访                       |
| newvisitornum        | integer                         | 首访                         |
| revisitornum         | integer                         | 复访                         |
| newsubscrnum         | integer                         | 新增认购                     |