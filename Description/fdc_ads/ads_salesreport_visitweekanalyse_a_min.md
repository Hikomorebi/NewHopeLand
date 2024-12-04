- 数据表名称
fdc_ads.ads_salesreport_visitweekanalyse_a_min

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

- 查询须知
1. 其中 orgname 表示组织名称，由城市名和组织名组成，如“成都锦麟府”。若用户提问中涉及城市名或组织名，请提取城市名或组织名作为模糊匹配的筛选条件。如“成都”可以通过 orgname LIKE '%成都%' 进行模糊匹配，“锦麟府”可以通过 orgname LIKE '%锦麟府%' 进行模糊匹配。
2. orgcode 字段主要用于查询时的比较条件，而不用于显示，查询时，避免选择 orgcode 字段。