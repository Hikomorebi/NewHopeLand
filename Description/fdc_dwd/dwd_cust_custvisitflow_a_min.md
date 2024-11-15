- 数据表名称
fdc_dwd.dwd_cust_custvisitflow_a_min

- 数据表解释
案场客户来访流水表。查询该数据表时，请务必使用 partitiondate 筛选分区时期，若无特别说明，使用 partitiondate = current_date进行筛选。

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
