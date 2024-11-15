- 数据表名称
fdc_dwd.dwd_trade_roomsmsubscr_a_min

- 数据表解释

房间小订信息表。查询该数据表时，请务必使用 partitiondate 筛选分区时期，若无特别说明，使用 partitiondate = current_date进行筛选。

- 各字段说明

| 字段名              | 数据类型           | 描述               |
| ------------------- | ------------------ | ------------------ |
| roomcode            | character  varying | 房间编码           |
| roomname            | character  varying | 房间名称           |
| roomfullnm          | character  varying | 房间全称           |
| buildcode           | character  varying | 楼栋编码           |
| buildname           | character  varying | 楼栋名称           |
| buildfullnm         | character  varying | 楼栋全称           |
| stagecode           | character  varying | 分期编码           |
| stagename           | character  varying | 分期名称           |
| projcode            | character  varying | 项目编码           |
| projname            | character  varying | 项目名称           |
| formatcode          | character  varying | 业态编码           |
| formatfullnm        | character  varying | 业态全称           |
| formatname          | character  varying | 业态名称           |
| citycode            | character  varying | 城市公司编码       |
| cityname            | character  varying | 城市公司名称       |
| corpcompanycode     | character  varying | 法人公司编码       |
| corpcompanyname     | character  varying | 法人公司名称       |
| smordercode         | character  varying | 认购编码           |
| saleslipcode        | character  varying | 销售单编码         |
| visitcode           | character  varying | 来访编码           |
| custcode            | character  varying | 客户编码           |
| custname            | character  varying | 客户名称           |
| custtype            | character  varying | 客户类型           |
| ordertype           | character  varying | 订单类型           |
| pricingmanner       | character  varying | 计价方式           |
| topaymode           | character  varying | 付款方式           |
| topaymodecate       | character  varying | 付款方式类别       |
| smorderstatus       | character  varying | 认购状态           |
| areastatus          | character  varying | 面积状态           |
| smorderdate         | character  varying | 认购日期           |
| smorderamount       | numeric            | 认购金额           |
| archarea            | numeric            | 建筑面积           |
| tnarea              | numeric            | 套内面积           |
| archuprc            | numeric            | 建筑单价           |
| tnuprc              | numeric            | 套内单价           |
| archbrgnuprc        | numeric            | 建筑成交单价       |
| tnbrgnuprc          | numeric            | 套内成交单价       |
| fitmentpriceiscontr | character  varying | 装修款是否并入合同 |
| decoratestandard    | character  varying | 装修标准           |
| decorateuprc        | numeric            | 装修单价           |
| decoratetotalprice  | numeric            | 装修总价           |
| taxamount           | numeric            | 协议总价(税额)     |
| notaxamount         | numeric            | 协议总价(不含税)   |
| mortgagebank        | character  varying | 按揭银行           |
| mortgageloansum     | numeric            | 按揭贷款额         |
| mortgageyears       | character  varying | 按揭年限           |
| provfundbank        | character  varying | 公积金银行         |
| provfundloansum     | numeric            | 公积金贷款额       |
| provfundyears       | character  varying | 公积金年限         |
| discount            | character  varying | 折扣               |
| discountexplain     | character varying  | 折扣说明           |
| referrer            | character  varying | 推荐人             |
| salesmanoacode      | character  varying | 业务员oa号         |
| salesman            | character  varying | 业务员             |
| closedate           | character  varying | 关闭日期           |
| closereason         | character  varying | 关闭原因           |
| modifydate          | character  varying | 修改日期           |
| custsource          | character  varying | 客户来源           |
| visitdate           | character  varying | 来访日期           |
| smorderexecdate     | character  varying | 认购统计日期       |
| lastsaleguid        | character  varying | 上次协议编码       |
| tradestatus         | character  varying | 交易状态           |
| tradeclosereason    | character  varying | 交易关闭原因       |
| invaliddate         | character  varying | 失效日期           |
| partitiondate       | character  varying | 分区日期           |
