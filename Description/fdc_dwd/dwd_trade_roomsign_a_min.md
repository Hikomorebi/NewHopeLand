- 数据表名称
fdc_dwd.dwd_trade_roomsign_a_min

- 数据表解释
签约明细表。

- 各字段说明
| 字段名               | 数据类型                        | 描述                             |
| -------------------- | ------------------------------- | -------------------------------- |
| roomcode             | character varying               | 房间编码                         |
| roomname             | character varying               | 房间名称                         |
| roomfullnm           | character varying               | 房间全称                         |
| buildcode            | character varying               | 楼栋编码                         |
| buildname            | character varying               | 楼栋名称                         |
| buildfullnm          | character varying               | 楼栋全称                         |
| stagecode            | character varying               | 分期编码                         |
| stagename            | character varying               | 分期名称                         |
| projcode             | character varying               | 项目编码                         |
| projname             | character varying               | 项目名称                         |
| formatcode           | character varying               | 业态编码                         |
| formatfullnm         | character varying               | 业态全称                         |
| formatname           | character varying               | 业态名称                         |
| citycode             | character varying               | 城市公司编码                     |
| cityname             | character varying               | 城市公司或区域公司名称             |
| corpcompanycode      | character varying               | 法人公司编码                     |
| corpcompanyname      | character varying               | 法人公司名称                     |
| propertyconsultantid | character varying               | 置业顾问编码                     |
| propertyconsultant   | character varying               | 置业顾问名称                     |
| contrcode            | character varying               | 合同编码                         |
| contract             | character varying               | 合同号                           |
| saleslipcode         | character varying               | 销售单编码                       |
| visitcode            | character varying               | 来访编码                         |
| subscrcode           | character varying               | 认购编码                         |
| custcode             | character varying               | 客户编码                         |
| custname             | character varying               | 客户名称                         |
| custtype             | character varying               | 客户类型                         |
| pricingmanner        | character varying               | 计价方式                         |
| topaymode            | character varying               | 付款方式                         |
| topaymodecate        | character varying               | 付款方式类别                     |
| contrputrecnum       | character varying               | 合同备案号                       |
| signdate             | character varying               | 签约日期                         |
| subscrdate           | character varying               | 认购日期                         |
| netsigndate          | character varying               | 网签日期                         |
| putrecdate           | character varying               | 备案日期                         |
| contrstatus          | character varying               | 合同状态                         |
| areastatus           | character varying               | 面积状态                         |
| archarea             | numeric                         | 建筑面积                         |
| tnarea               | numeric                         | 套内面积                         |
| archuprc             | numeric                         | 建筑单价                         |
| tnuprc               | numeric                         | 套内单价                         |
| archbrgnuprc         | numeric                         | 建筑成交单价                     |
| tnbrgnuprc           | numeric                         | 套内成交单价                     |
| contrtotalprice      | character varying               | 合同总价                         |
| decoratetopaymode    | character varying               | 装修付款方式                     |
| fitmentpriceiscontr  | character varying               | 装修款是否并入合同               |
| decoratestandard     | character varying               | 装修标准                         |
| decorateuprc         | numeric                         | 装修单价                         |
| firstdecoraterenosum | numeric                         | 初装修改造费                     |
| decoratetotalprice   | numeric                         | 装修总价                         |
| attafunds            | character varying               | 附属款                           |
| type                 | character varying               | 按揭银行                         |
| mortgageloansum      | numeric                         | 按揭贷款额                       |
| mortgageyears        | character varying               | 按揭年限                         |
| provfundbank         | character varying               | 公积金银行                       |
| provfundloansum      | numeric                         | 公积金贷款额                     |
| provfundyears        | character varying               | 公积金年限                       |
| discount             | character varying               | 折扣                             |
| discountexplain      | character varying               | 折扣说明                         |
| referrer             | character varying               | 推荐人                           |
| salesmanoacode       | character varying               | 业务员oa号                       |
| salesman             | character varying               | 业务员                           |
| closedate            | character varying               | 关闭日期                         |
| closereason          | character varying               | 关闭原因                         |
| modifydate           | character varying               | 修改日期                         |
| custsource           | character varying               | 客户来源                         |
| issffq               | character varying               | 是否首付分期                     |
| signexecdate         | character varying               | 签约统计日期                     |
| actualbctotal        | numeric                         | 实际补差款                       |
| bcshdate             | character varying               | 补差款审核时间                   |
| premprice            | character varying               | 溢价款                           |
| partitiondate        | timestamp(0) without  time zone | 分区日期                         |
| consultantids        | character varying               | 置业顾问ids,可能包含多个置业顾问 |
| standtotal           | numeric                         | 标准总价                         |
| mortgagerecord       | character varying               | 按揭记录                         |
| last_contrcode       | character varying               | 变更前合同编码                   |
| mortgagebank         | character varying               | 按揭银行                         |
| cashback             | numeric                         | 返现                             |

- 查询须知
1. 其中 cityname 代表城市公司或者区域公司的名称，如“西部区域公司”，“华东公司”，“成都公司”。若用户提问中涉及公司名称，请提取城市或区域名作为模糊匹配的筛选条件。如“西部区域公司”可以通过 cityname LIKE '%西部区域%' 进行模糊匹配，“成都公司”可以通过 cityname LIKE '%成都%' 进行匹配。
2. 其中 projname 表示项目名称，由城市名和项目名组成，如“成都锦麟府”,若用户提问中包含城市名或项目名，请提取城市名或项目名作为模糊匹配的筛选条件。如“成都”可以通过 projname LIKE '%成都%' 进行模糊匹配，“锦麟府”可以通过 projname LIKE '%锦麟府%' 进行模糊匹配。
3. 查询该表时，请务必使用 partitiondate = current_date 筛选分区时期。
4. 所有编码字段（如房间编码、楼栋编码）主要用于查询时的比较条件，而不用于显示，查询时，避免选择编码字段。
