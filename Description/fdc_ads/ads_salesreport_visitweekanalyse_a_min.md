- 数据表名称
ads_salesreport_visitweekanalyse_a_min

- 数据表解释

经营分析来访周度分析。

- 各字段说明

| 字段名        | 数据类型                        | 描述                         |
| ------------- | ------------------------------- | ---------------------------- |
| statdate      | timestamp(0)  without time zone | 统计日期                     |
| orgtype       | character varying               | 组织类型                     |
| orgcode       | character  varying              | 组织编码                     |
| orgname       | character  varying              | 组织名称                     |
| channel       | character varying               | 通路                         |
| cycletype     | character varying               | 周期类型 W-周 M-月 Q-季 Y-年 |
| visitornum    | integer                         | 总来访（首访+复访）          |
| newvisitornum | integer                         | 首访                         |
| revisitornum  | integer                         | 复访                         |
| newsubscrnum  | integer                         | 新增认购                     |