- 数据表名称
fdc.view_proj_equity_his

- 数据表解释
项目权益汇总表。

- 各字段说明
| 字段名      | 数据类型          | 描述     |
| ----------- | ----------------- | -------- |
| projcode    | character varying | 项目编码 |
| projname    | character varying | 项目名称 |
| equityratio | numeric           | 权益比例 |
| validdate   | character varying | 生效日期 |
| invaliddate | character varying | 失效日期 |

- 查询须知
1. 其中 projname 表示项目名称，由城市名和项目名组成，如“成都锦麟府”,若用户提问中包含城市名或项目名，请提取城市名或项目名作为模糊匹配的筛选条件。如“成都”可以通过 projname LIKE '%成都%' 进行模糊匹配，“锦麟府”可以通过 projname LIKE '%锦麟府%' 进行模糊匹配。
2. projcode 字段主要用于查询时的比较条件，而不用于显示，查询时，避免选择 projcode 字段。