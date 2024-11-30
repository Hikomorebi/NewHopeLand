- 数据表名称
fdc_dwd.dwd_trade_roomreceivable_a_min

- 数据表解释
应收明细表。

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
| cityname             | character  varying              | 城市公司或区域公司名称 |
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

- 查询须知
1. 其中 cityname 代表城市公司或者区域公司的名称，如“西部区域公司”，“华东公司”，“成都公司”。若用户提问中涉及公司名称，请提取城市或区域名作为模糊匹配的筛选条件。如“西部区域公司”可以通过 cityname LIKE '%西部区域%' 进行模糊匹配，“成都公司”可以通过 cityname LIKE '%成都%' 进行匹配。
2. 其中 projname 表示项目名称，由城市名和项目名组成，如“成都锦麟府”,若用户提问中包含城市名或项目名，请提取城市名或项目名作为模糊匹配的筛选条件。如“成都”可以通过 projname LIKE '%成都%' 进行模糊匹配，“锦麟府”可以通过 projname LIKE '%锦麟府%' 进行模糊匹配。
3. 查询该表时，请务必使用 partitiondate = current_date 筛选分区时期。
4. 所有编码字段（如房间编码、楼栋编码）主要用于查询时的比较条件，而不用于显示，查询时，避免选择编码字段。