- 数据表名称
fdc_dwd.dwd_trade_roomreceivable_a_min

- 数据表解释

应收明细表。查询该数据表时，请务必使用 partitiondate 筛选分区时期，若无特别说明，使用 partitiondate = current_date进行筛选。

- 各字段说明

| 字段名               | 数据类型                        | 描述             |
| -------------------- | :------------------------------ | ---------------- |
| roomcode             | character  varying              | 房间编码         |
| roomname             | character  varying              | 房间名称         |
| roomfullnm           | character  varying              | 房间全称         |
| buildcode            | character  varying              | 楼栋编码         |
| buildname            | character  varying              | 楼栋名称         |
| buildfullnm          | character  varying              | 楼栋全称         |
| stagecode            | character  varying              | 分期编码         |
| stagename            | character  varying              | 分期名称         |
| projcode             | character  varying              | 项目编码         |
| projname             | character  varying              | 项目名称         |
| formatcode           | character  varying              | 业态编码         |
| formatfullnm         | character  varying              | 业态全称         |
| formatname           | character  varying              | 业态名称         |
| citycode             | character  varying              | 城市公司编码     |
| cityname             | character  varying              | 城市公司名称     |
| corpcompanycode      | character  varying              | 法人公司编码     |
| corpcompanyname      | character  varying              | 法人公司名称     |
| receivablecode       | character  varying              | 应收款编码       |
| saleslipcode         | character  varying              | 销售单编码       |
| subscrcode           | character  varying              | 认购编码         |
| contrcode            | character  varying              | 合同编码         |
| recvbldebtdate       | character varying               | 应收日期         |
| fundtype             | character varying               | 款项类型         |
| fundname             | character  varying              | 款项名称         |
| fundstatus           | character varying               | 款项状态         |
| recvbldebtamounttax  | numeric                         | 应收金额(含税)   |
| recvbldebtamountectx | numeric                         | 应收金额(不含税) |
| recvbldebtbalance    | numeric                         | 应收余额         |
| dsamount             | numeric                         | 多收金额         |
| partitiondate        | timestamp(0) without  time zone | 分区日期         |
| contrrecvbldebtdate  | character varying               | 合同应收日期     |

