- 数据表名称
fdc_dws.dws_proj_projplansum_a_h

- 数据表解释

项目计划汇总表。查询该数据表时，请务必使用 partitiondate 筛选分区时期，若无特别说明，使用 partitiondate = current_date进行筛选。

- 各字段说明

| 字段名                  | 数据类型                        | 描述                      |
| ----------------------- | ------------------------------- | ------------------------- |
| datadate                | character varying               | 数据日期                  |
| citycode                | character varying               | 城市编码                  |
| cityname                | character varying               | 城市名称                  |
| projcode                | character varying               | 项目编码                  |
| projname                | character varying               | 项目名称                  |
| m1plansignamount        | numeric                         | 1月计划签约金额           |
| m2plansignamount        | numeric                         | 2月计划签约金额           |
| m3plansignamount        | numeric                         | 3月计划签约金额           |
| m4plansignamount        | numeric                         | 4月计划签约金额           |
| m5plansignamount        | numeric                         | 5月计划签约金额           |
| m6plansignamount        | numeric                         | 6月计划签约金额           |
| m7plansignamount        | numeric                         | 7月计划签约金额           |
| m8plansignamount        | numeric                         | 8月计划签约金额           |
| m9plansignamount        | numeric                         | 9月计划签约金额           |
| m10plansignamount       | numeric                         | 10月计划签约金额          |
| m11plansignamount       | numeric                         | 11月计划签约金额          |
| m12plansignamount       | numeric                         | 12月计划签约金额          |
| q1plansignamount        | numeric                         | 1季度计划签约金额         |
| q2plansignamount        | numeric                         | 2季度计划签约金额         |
| q3plansignamount        | numeric                         | 3季度计划签约金额         |
| q4plansignamount        | numeric                         | 4季度计划签约金额         |
| yearplansignamount      | numeric                         | 年计划签约金额            |
| m1planrefundamount      | numeric                         | 1月计划回款金额           |
| m2planrefundamount      | numeric                         | 2月计划回款金额           |
| m3planrefundamount      | numeric                         | 3月计划回款金额           |
| m4planrefundamount      | numeric                         | 4月计划回款金额           |
| m5planrefundamount      | numeric                         | 5月计划回款金额           |
| m6planrefundamount      | numeric                         | 6月计划回款金额           |
| m7planrefundamount      | numeric                         | 7月计划回款金额           |
| m8planrefundamount      | numeric                         | 8月计划回款金额           |
| m9planrefundamount      | numeric                         | 9月计划回款金额           |
| m10planrefundamount     | numeric                         | 10月计划回款金额          |
| m11planrefundamount     | numeric                         | 11月计划回款金额          |
| m12planrefundamount     | numeric                         | 12月计划回款金额          |
| q1planrefund            | numeric                         | 1季度计划回款             |
| q2planrefund            | numeric                         | 2季度计划回款             |
| q3planrefund            | numeric                         | 3季度计划回款             |
| q4planrefund            | numeric                         | 4季度计划回款             |
| yearplanrefund          | numeric                         | 年计划回款                |
| etltime                 | character  varying              | etl时间                   |
| partitiondate           | timestamp(0)  without time zone | 分区日期                  |
| month1plansignarea      | numeric                         | 1月计划签约面积           |
| month1plansignnum       | integer                         | 1月计划签约套数           |
| month2plansignarea      | numeric                         | 2月计划签约面积           |
| month2plansignnum       | integer                         | 2月计划签约套数           |
| month3plansignarea      | numeric                         | 3月计划签约面积           |
| month3plansignnum       | integer                         | 3月计划签约套数           |
| month4plansignarea      | numeric                         | 4月计划签约面积           |
| month4plansignnum       | integer                         | 4月计划签约套数           |
| month5plansignarea      | numeric                         | 5月计划签约面积           |
| month5plansignnum       | integer                         | 5月计划签约套数           |
| month6plansignarea      | numeric                         | 6月计划签约面积           |
| month6plansignnum       | integer                         | 6月计划签约套数           |
| month7plansignarea      | numeric                         | 7月计划签约面积           |
| month7plansignnum       | integer                         | 7月计划签约套数           |
| month8plansignarea      | numeric                         | 8月计划签约面积           |
| month8plansignnum       | integer                         | 8月计划签约套数           |
| month9plansignarea      | numeric                         | 9月计划签约面积           |
| month9plansignnum       | integer                         | 9月计划签约套数           |
| month10plansignarea     | numeric                         | 10月计划签约面积          |
| month10plansignnum      | integer                         | 10月计划签约套数          |
| month11plansignarea     | numeric                         | 11月计划签约面积          |
| month11plansignnum      | integer                         | 11月计划签约套数          |
| month12plansignarea     | numeric                         | 12月计划签约面积          |
| month12plansignnum      | integer                         | 12月计划签约套数          |
| q1plansignarea          | numeric                         | 1季度计划签约面积         |
| q1plansignnum           | integer                         | 1季度计划签约套数         |
| q2plansignarea          | numeric                         | 2季度计划签约面积         |
| q2plansignnum           | integer                         | 2季度计划签约套数         |
| q3plansignarea          | numeric                         | 3季度计划签约面积         |
| q3plansignnum           | integer                         | 3季度计划签约套数         |
| q4plansignarea          | numeric                         | 4季度计划签约面积         |
| q4plansignnum           | integer                         | 4季度计划签约套数         |
| cyplansignarea          | numeric                         | 本年计划签约面积          |
| cyplansignnum           | integer                         | 本年计划签约套数          |
| years                   | character  varying              | 年份                      |
| m1plansignamount_qyh    | numeric                         | 1月计划签约金额_权益后    |
| m2plansignamount_qyh    | numeric                         | 2月计划签约金额_权益后    |
| m3plansignamount_qyh    | numeric                         | 3月计划签约金额_权益后    |
| m4plansignamount_qyh    | numeric                         | 4月计划签约金额_权益后    |
| m5plansignamount_qyh    | numeric                         | 5月计划签约金额_权益后    |
| m6plansignamount_qyh    | numeric                         | 6月计划签约金额_权益后    |
| m7plansignamount_qyh    | numeric                         | 7月计划签约金额_权益后    |
| m8plansignamount_qyh    | numeric                         | 8月计划签约金额_权益后    |
| m9plansignamount_qyh    | numeric                         | 9月计划签约金额_权益后    |
| m10plansignamount_qyh   | numeric                         | 10月计划签约金额_权益后   |
| m11plansignamount_qyh   | numeric                         | 11月计划签约金额_权益后   |
| m12plansignamount_qyh   | numeric                         | 12月计划签约金额_权益后   |
| q1plansignamount_qyh    | numeric                         | 一季度计划签约金额_权益后 |
| q2plansignamount_qyh    | numeric                         | 二季度计划签约金额_权益后 |
| q3plansignamount_qyh    | numeric                         | 三季度计划签约金额_权益后 |
| q4plansignamount_qyh    | numeric                         | 四季度计划签约金额_权益后 |
| yearplansignamount_qyh  | numeric                         | 年度计划签约金额_权益后   |
| m1planrefundamount_qyh  | numeric                         | 1月计划回款金额_权益后    |
| m2planrefundamount_qyh  | numeric                         | 2月计划回款金额_权益后    |
| m3planrefundamount_qyh  | numeric                         | 3月计划回款金额_权益后    |
| m4planrefundamount_qyh  | numeric                         | 4月计划回款金额_权益后    |
| m5planrefundamount_qyh  | numeric                         | 5月计划回款金额_权益后    |
| m6planrefundamount_qyh  | numeric                         | 6月计划回款金额_权益后    |
| m7planrefundamount_qyh  | numeric                         | 7月计划回款金额_权益后    |
| m8planrefundamount_qyh  | numeric                         | 8月计划回款金额_权益后    |
| m9planrefundamount_qyh  | numeric                         | 9月计划回款金额_权益后    |
| m10planrefundamount_qyh | numeric                         | 10月计划回款金额_权益后   |
| m11planrefundamount_qyh | numeric                         | 11月计划回款金额_权益后   |
| m12planrefundamount_qyh | numeric                         | 12月计划回款金额_权益后   |
| q1planrefund_qyh        | numeric                         | 一季度计划回款金额_权益后 |
| q2planrefund_qyh        | numeric                         | 二季度计划回款金额_权益后 |
| q3planrefund_qyh        | numeric                         | 三季度计划回款金额_权益后 |
| q4planrefund_qyh        | numeric                         | 四季度计划回款金额_权益后 |
| yearplanrefund_qyh      | numeric                         | 年度计划回款金额_权益后   |
