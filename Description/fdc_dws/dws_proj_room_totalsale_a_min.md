- 数据表名称
fdc_dws.dws_proj_room_totalsale_a_min

- 数据表解释
房间业绩统计表。

- 各字段说明
| 字段名                  | 数据类型                     | 描述                      |
| ----------------------- | ---------------------------- | ------------------------- |
| datadate                | character  varying           | 统计日期                  |
| bucode                  | character  varying           | 事业部编码                |
| buname                  | character  varying           | 事业部名称                |
| citycode                | character  varying           | 城市编码                  |
| cityname                | character  varying           | 城市公司或区域公司名称       |
| projcode                | character  varying           | 项目编码                  |
| projname                | character  varying           | 项目名称                  |
| buildcode               | character  varying           | 楼栋编码                  |
| buildname               | character  varying           | 楼栋名称                  |
| roomcode                | character  varying           | 房间编码                  |
| roomname                | character  varying           | 房间名称                  |
| cd_smorder_units        | integer                      | 当日小订套数              |
| cd_smorder_units        | integer                      | 当日小订套数              |
| cd_smorder_amt          | numeric                      | 当日小订金额              |
| cd_smorder_amt_qyh      | numeric                      | 当日小订金额_权益后       |
| cw_smorder_units        | integer                      | 当周小订套数              |
| cw_smorder_amt          | numeric                      | 当周小订金额              |
| cw_smorder_amt_qyh      | numeric                      | 当周小订金额_权益后       |
| cm_smorder_units        | integer                      | 当月小订套数              |
| cm_smorder_amt          | numeric                      | 当月小订金额              |
| cm_smorder_amt_qyh      | numeric                      | 当月小订金额_权益后       |
| cq_smorder_units        | integer                      | 当季小订套数              |
| cq_smorder_amt          | numeric                      | 当季小订金额              |
| cq_smorder_amt_qyh      | numeric                      | 当季小订金额_权益后       |
| cy_smorder_units        | integer                      | 当年小订套数              |
| cy_smorder_amt          | numeric                      | 当年小订金额              |
| cy_smorder_amt_qyh      | numeric                      | 当年小订金额_权益后       |
| smorder_units           | integer                      | 累计小订套数              |
| smorder_amt             | numeric                      | 累计小订金额              |
| smorder_amt_qyh         | numeric                      | 累计小订金额_权益后       |
| cd_newsub_units         | integer                      | 当日新认购套数            |
| cd_newsub_area          | numeric                      | 当日新认购面积            |
| cd_newsub_amount        | numeric                      | 当日新认购金额            |
| cd_newsub_amount_qyh    | numeric                      | 当日新认购金额_权益后     |
| cw_newsub_units         | integer                      | 当周新认购套数            |
| cw_newsub_area          | numeric                      | 当周新认购面积            |
| cw_newsub_amount        | numeric                      | 当周新认购金额            |
| cw_newsub_amount_qyh    | numeric                      | 当周新认购金额_权益后     |
| cm_newsub_units         | integer                      | 当月新认购套数            |
| cm_newsub_area          | numeric                      | 当月新认购面积            |
| cm_newsub_amount        | numeric                      | 当月新认购金额            |
| cm_newsub_amount_qyh    | numeric                      | 当月新认购金额_权益后     |
| cq_newsub_units         | integer                      | 当季新认购套数            |
| cq_newsub_area          | numeric                      | 当季新认购面积            |
| cq_newsub_amount        | numeric                      | 当季新认购金额            |
| cq_newsub_amount_qyh    | numeric                      | 当季新认购金额_权益后     |
| cy_newsub_units         | integer                      | 当年新认购套数            |
| cy_newsub_area          | numeric                      | 当年新认购面积            |
| cy_newsub_amount        | numeric                      | 当年新认购金额            |
| cy_newsub_amount_qyh    | numeric                      | 当年新认购金额_权益后     |
| ad_newsub_units         | integer                      | 累计新认购套数            |
| ad_newsub_area          | numeric                      | 累计新认购面积            |
| ad_newsub_amount        | numeric                      | 累计新认购金额            |
| ad_newsub_amount_qyh    | numeric                      | 累计新认购金额_权益后     |
| sub_units               | integer                      | 累计认购套数              |
| sub_area                | numeric                      | 累计认购面积              |
| sub_amt                 | numeric                      | 累计认购金额              |
| sub_amt_qyh             | numeric                      | 累计认购金额_权益后       |
| cd_subunsign_units      | integer                      | 当日认购未签约套数        |
| cd_subunsign_area       | numeric                      | 当日认购未签约面积        |
| cd_subunsign_amount     | numeric                      | 当日认购未签约金额        |
| cd_subunsign_amount_qyh | numeric                      | 当日认购未签约金额_权益后 |
| cw_subunsign_units      | integer                      | 当周认购未签约套数        |
| cw_subunsign_area       | numeric                      | 当周认购未签约面积        |
| cw_subunsign_amount     | numeric                      | 当周认购未签约金额        |
| cw_subunsign_amount_qyh | numeric                      | 当周认购未签约金额_权益后 |
| cm_subunsign_units      | integer                      | 当月认购未签约套数        |
| cm_subunsign_area       | numeric                      | 当月认购未签约面积        |
| cm_subunsign_amount     | numeric                      | 当月认购未签约金额        |
| cm_subunsign_amount_qyh | numeric                      | 当月认购未签约金额_权益后 |
| cq_subunsign_units      | integer                      | 当季认购未签约套数        |
| cq_subunsign_area       | numeric                      | 当季认购未签约面积        |
| cq_subunsign_amount     | numeric                      | 当季认购未签约金额        |
| cq_subunsign_amount_qyh | numeric                      | 当季认购未签约金额_权益后 |
| cy_subunsign_units      | integer                      | 当年认购未签约套数        |
| cy_subunsign_area       | numeric                      | 当年认购未签约面积        |
| cy_subunsign_amount     | numeric                      | 当年认购未签约金额        |
| cy_subunsign_amount_qyh | numeric                      | 当年认购未签约金额_权益后 |
| subunsign_units         | integer                      | 累计认购未签约套数        |
| subunsign_area          | numeric                      | 累计认购未签约面积        |
| subunsign_amt           | numeric                      | 累计认购未签约金额        |
| subunsign_amt_qyh       | numeric                      | 累计认购未签约金额_权益后 |
| cd_newsign_units        | integer                      | 当日新签约套数            |
| cd_newsign_area         | numeric                      | 当日新签约面积            |
| cd_newsign_amount       | numeric                      | 当日新签约金额            |
| cd_newsign_amount_qyh   | numeric                      | 当日新签约金额_权益后     |
| cw_newsign_units        | integer                      | 当周新签约套数            |
| cw_newsign_area         | numeric                      | 当周新签约面积            |
| cw_newsign_amount       | numeric                      | 当周新签约金额            |
| cw_newsign_amount_qyh   | numeric                      | 当周新签约金额_权益后     |
| cm_newsign_units        | integer                      | 当月新签约套数            |
| cm_newsign_area         | numeric                      | 当月新签约面积            |
| cm_newsign_amount       | numeric                      | 当月新签约金额            |
| cm_newsign_amount_qyh   | numeric                      | 当月新签约金额_权益后     |
| cq_newsign_units        | integer                      | 当季新签约套数            |
| cq_newsign_area         | numeric                      | 当季新签约面积            |
| cq_newsign_amount       | numeric                      | 当季新签约金额            |
| cq_newsign_amount_qyh   | numeric                      | 当季新签约金额_权益后     |
| cy_newsign_units        | integer                      | 当年新签约套数            |
| cy_newsign_area         | numeric                      | 当年新签约面积            |
| cy_newsign_amount       | numeric                      | 当年新签约金额            |
| cy_newsign_amount_qyh   | numeric                      | 当年新签约金额_权益后     |
| sign_units              | integer                      | 累计签约套数              |
| sign_area               | numeric                      | 累计签约面积              |
| sign_amt                | numeric                      | 累计签约金额              |
| sign_amt_qyh            | numeric                      | 累计签约金额_权益后       |
| cdsign_cdrcvd           | numeric                      | 当日签约回款              |
| cdsign_cdrcvd_qyh       | numeric                      | 当日签约回款_权益后       |
| pdsign_cdrcvd           | numeric                      | 往日签约回款              |
| pdsign_cdrcvd_qyh       | numeric                      | 往日签约回款_权益后       |
| cwsign_cwrcvd           | numeric                      | 当周签约回款              |
| cwsign_cwrcvd_qyh       | numeric                      | 当周签约回款_权益后       |
| pwsign_cwrcvd           | numeric                      | 往周签约回款              |
| pwsign_cwrcvd_qyh       | numeric                      | 往周签约回款_权益后       |
| cmsign_cmrcvd           | numeric                      | 当月签约回款              |
| cmsign_cmrcvd_qyh       | numeric                      | 当月签约回款_权益后       |
| pmsign_cmrcvd           | numeric                      | 往月签约回款              |
| pmsign_cmrcvd_qyh       | numeric                      | 往月签约回款_权益后       |
| cqsign_cqrcvd           | numeric                      | 当季签约回款              |
| cqsign_cqrcvd_qyh       | numeric                      | 当季签约回款_权益后       |
| pqsign_cqrcvd           | numeric                      | 往季签约回款              |
| pqsign_cqrcvd_qyh       | numeric                      | 往季签约回款_权益后       |
| cysign_cyrcvd           | numeric                      | 当年签约回款              |
| cysign_cyrcvd_qyh       | numeric                      | 当年签约回款_权益后       |
| pysign_cyrcvd           | numeric                      | 往年签约回款              |
| pysign_cyrcvd_qyh       | numeric                      | 往年签约回款_权益后       |
| pmt_rcvd_amt            | numeric                      | 累计回款金额              |
| pmt_rcvd_amt_qyh        | numeric                      | 累计回款金额_权益后       |
| pmt_rcvb_amt            | numeric                      | 累计应收金额              |
| pmt_rcvb_amt_qyh        | numeric                      | 累计应收金额_权益后       |
| sub_ret_units           | integer                      | 认购退房套数              |
| sub_ret_area            | numeric                      | 认购退房面积              |
| sub_ret_amt             | numeric                      | 认购退房金额              |
| sub_ret_amt_qyh         | numeric                      | 认购退房金额_权益后       |
| sub_chg_units           | integer                      | 认购换房套数              |
| sub_chg_area            | numeric                      | 认购换房面积              |
| sub_chg_amt             | numeric                      | 认购换房金额              |
| sub_chg_amt_qyh         | numeric                      | 认购换房金额_权益后       |
| sign_ret_units          | integer                      | 签约退房套数              |
| sign_ret_area           | numeric                      | 签约退房面积              |
| sign_ret_amt            | numeric                      | 签约退房金额              |
| sign_ret_amt_qyh        | numeric                      | 签约退房金额_权益后       |
| sign_chg_units          | integer                      | 签约换房套数              |
| sign_chg_area           | numeric                      | 签约换房面积              |
| sign_chg_amt            | numeric                      | 签约换房金额              |
| sign_chg_amt_qyh        | numeric                      | 签约换房金额_权益后       |
| area_adj_amt            | numeric                      | 补差金额                  |
| area_adj_amt_qyh        | numeric                      | 补差金额_权益后           |
| rename_fee              | numeric                      | 更名手续费                |
| rename_fee_qyh          | numeric                      | 更名手续费_权益后         |
| etltime                 | character varying            | 数据更新时间              |
| partitiondate           | timestamp without  time zone | 分区日期                  |
| tradetype               | character  varying           | 交易类型                  |

- 查询须知
1. 其中 cityname 代表城市公司或者区域公司的名称，如“西部区域公司”，“华东公司”，“成都公司”。若用户提问中涉及公司名称，请提取城市或区域名作为模糊匹配的筛选条件。如“西部区域公司”可以通过 cityname LIKE '%西部区域%' 进行模糊匹配，“成都公司”可以通过 cityname LIKE '%成都%' 进行匹配。
2. 其中 projname 表示项目名称，由城市名和项目名组成，如“成都锦麟府”,若用户提问中包含城市名或项目名，请提取城市名或项目名作为模糊匹配的筛选条件。如“成都”可以通过 projname LIKE '%成都%' 进行模糊匹配，“锦麟府”可以通过 projname LIKE '%锦麟府%' 进行模糊匹配。
3. 查询该表时，请务必使用 partitiondate = current_date 筛选分区时期。
4. 所有编码字段（如房间编码、楼栋编码）主要用于查询时的比较条件，而不用于显示，查询时，避免选择编码字段。