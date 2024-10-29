#xinxiwang _dictionary：xinxiwang数据库数据字典


## 1.dwd_trade_roomsign_a_min签约明细表

- 基本解释

  ​		该数据表记录了所有所需签约面积，价格，编码全称等。

- 各字段说明

| 字段名                | 描述         | 数据类型                 |
| --------------------- | ------------ | ------------           |
| archarea              | 建筑面积      | numeric(18,4)          |
| contrtotalprice       | 合同总价      | character varying(100) |
| firstdecoraterenosum  | 初装修改造费  | numeric(18,4)           |
| decoratetotalprice    | 装修总价      | numeric(18,4)          |
| partitiondate         | 分区日期      | timestamp(0) without time zone |
| signexecdate          | 签约统计日期  | character varying(50)  |
| closedate             | 关闭日期      | character varying(50)  |
| roomcode              | 房间编码      | character varying(50)  |
| roomname              | 房间名称      | character varying(200) |
| roomfullnm            | 房间全称      | character varying(100) |
| buildcode             | 楼栋编码      | character varying(100) |
| buildname             | 楼栋名称      | character varying(200) |
| buildfullnm           | 楼栋全称      | character varying(100) |
| stagecode             | 分期编码      | character varying(100) |
| stagename             | 分期名称      | character varying(200) |
| projcode              | 项目编码      | character varying(100) |
| projname              | 项目名称      | character varying(500) |
| formatcode            | 业态编码      | character varying(100) |
| formatfullnm          | 业态全称      | character varying(100) |
| formatname            | 业态名称      | character varying(200) |
| fitmentpriceiscontr   | 装修款是否并入合同 | character varying(100) |


## 2.dws_proj_room_totalsale_a_min房间业绩统计表

- 基本解释

  ​		该数据表描述了累计签约套数面积，金额，漏洞房间编码，名称等。

- 各字段说明

| 字段名                   | 描述           | 数据类型                 |
| ------------------------ | -------------- | -----------------------|
| sign_units               | 累计签约套数    | integer                |
| sign_area                | 累计签约面积    | numeric(18,4)          |
| sign_amt                 | 累计签约金额    | numeric(18,4)          |
| sign_amt_qyh             | 累计签约金额_权益后  | numeric(18,4)      |
| datadate                 | 统计日期        | character varying(50)  |
| citycode                 | 城市编码        | character varying(100) |
| cityname                 | 城市名称        | character varying(200) |
| projcode                 | 项目编码        | character varying(100) |
| projname                 | 项目名称        | character varying(200) |
| buildcode                | 楼栋编码        | character varying(100) |
| buildname                | 楼栋名称        | character varying(200) |
| roomcode                 | 房间编码        | character varying(100) |
| roomname                 | 房间名称        | character varying(200) |
| datadate                 | 统计日期        | character varying(50)  |

