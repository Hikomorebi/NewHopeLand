- 数据表名称
fdc_dwd.dwd_cust_custvisitflow_a_min

- 数据表解释
案场客户来访流水表。

- 各字段说明
| 字段名                 | 数据类型                        | 描述              |
| ---------------------- | ------------------------------- | ----------------- |
| datadate               | character  varying              | 数据日期          |
| citycode               | character varying               | 城市编码          |
| cityname               | character varying               | 城市名称          |
| projcode               | character varying               | 项目编码          |
| projname               | character varying               | 项目名称          |
| visitid                | character varying               | 来访id            |
| saleruserid            | character varying               | 销售客户关系表id  |
| agentuserid            | character varying               | 中介报备表id      |
| custname               | character varying               | 客户名称          |
| mobilephone            | character varying               | 手机号            |
| propertyconsultantid   | character varying               | 置业顾问oaAccount |
| agentid                | character varying               | 中介openid        |
| channelid1             | character varying               | 一级渠道id        |
| channelid2             | character varying               | 二级渠道id        |
| channelname            | character varying               | 渠道名称          |
| visitdate              | character varying               | 来访日期          |
| visitorcount           | integer                         | 来访人数          |
| isvisit                | character varying               | 是否来访过        |
| etltime                | character varying               | etl时间           |
| partitiondate          | timestamp(0) without  time zone | 工区日期          |
| chanceid               | character varying               | 销售机会id        |
| tradechannel           | character varying               | 成交途径          |
| propertyconsultantname | character  varying              | 置业顾问          |

- 查询须知
1. 其中 cityname 代表城市公司或者区域公司的名称，如“西部区域公司”，“华东公司”，“成都公司”。若用户提问中涉及公司名称，请提取城市或区域名作为模糊匹配的筛选条件。如“西部区域公司”可以通过 cityname LIKE '%西部区域%' 进行模糊匹配，“成都公司”可以通过 cityname LIKE '%成都%' 进行匹配。
2. 其中 projname 表示项目名称，由城市名和项目名组成，如“成都锦麟府”,若用户提问中包含城市名或项目名，请提取城市名或项目名作为模糊匹配的筛选条件。如“成都”可以通过 projname LIKE '%成都%' 进行模糊匹配，“锦麟府”可以通过 projname LIKE '%锦麟府%' 进行模糊匹配。
3. 查询该表时，请务必使用 partitiondate = current_date 筛选分区时期。
4. citycode 和 projcode 字段主要用于查询时的比较条件，而不用于显示，查询时，避免选择 citycode 和 projcode 字段。