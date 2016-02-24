#优化时间 2015-01-11 降低CPU 80%
ALTER TABLE fcpay.FC_WITHDRAW_LOAN_APPLY_REF ADD KEY FC__WITH_APPLY_ID_key (FC_WITH_APPLY_ID);
ALTER TABLE fcpay.FC_WITHDRAW_APPLY ADD KEY USER_NAME_BUSINESS_ID_APPLY_TIME (USER_NAME,BUSINESS_ID,APPLY_TIME);


#优化时间 2015-01-12 Reid 提供
--客户申请表
ALTER TABLE fcpay.FC_WITHDRAW_APPLY ADD INDEX FC_WA_INDEX1(BUSINESS_ID,USER_NAME,APPLY_TIME,RISK_STATUS,STATUS);
--充值帐变表
ALTER TABLE fcpay.FC_RISK_PREPAID_ACCOUNT_CHANGE_INFO ADD INDEX FC_RPACI_INDEX2(BUSINESS_ID,ACCOUNT_CHANGE_TIME,CUSTOMER_NAME);
--游戏流水明细表
ALTER TABLE fcpay.FC_RISK_GAME_FLOW_DETAIL ADD INDEX FC_RGFD_INDEX3(BUSINESS_ID,GAME_CHANGE_TIME,CHANGE_TYPE,GAME_TYPE,CUSTOMER_NAME);
--游戏中奖信息表
ALTER TABLE fcpay.FC_RISK_GAME_WINNING_INFO ADD INDEX FC_RGWI_INDEX4(BUSINESS_ID,BET_TIME,GAME_RULE,CUSTOMER_NAME);
--会员总账信息表
ALTER TABLE fcpay.FC_RISK_CUSTOMER_ACCOUNT_INFO ADD INDEX FC_RUAI_INDEX5(CUSTOMER_NAME);

ALTER TABLE fcpay.FC_WITHDRAW_LOAN_APPLY_REF ADD INDEX FC_WDLAR_INDEX7(LOAN_RECORD_ID,fcpay.FC_WITH_APPLY_ID);

ALTER TABLE fcpay.FC_WITHDRAW_LOAN_DETAIL ADD INDEX FC_WDLD_INDEX8(LOAN_RECORD_ID,STATUS);

ALTER TABLE fcpay.FC_WITHDRAW_TRANSIT_RECORD ADD INDEX FC_WDTD_INDEX9(fcpay.FC_WITH_APPLY_ID,TRANSIT_STATUS);

ALTER TABLE fcpay.FC_WITHDRAW_TRANSIT_DETAIL ADD INDEX FC_WDTD_INDEX10(TRANSIT_RECORD_ID,STATUS);

ALTER TABLE fcpay.FC_WEB_GAME_TRADE ADD INDEX FC_WGT_INDEX11(TRAD_TYPE,TRAD_MSG_STATUS,TRAD_MSG_PLATFROM);

--静态表，无insert 
ALTER TABLE fcpay.FC_SHIFT_ACTIVE_ACCOUNT ADD INDEX FC_SAA_INDEX12(STATUS,IS_TRANSFERING,TRANSIT_UPDATED_TIME);

--静态表，无insert
ALTER TABLE fcpay.FC_INNERC_ACCOUNT ADD INDEX FC_IA_INDEX13(ACCOUNT_NO,ACCOUNT_AUTO_TYPE,ACCOUNT_STATUS,PAYMENT_TYPE,ACCOUNT_TIER,BUSINESS_ID);


#优化时间 2015-01-11
Alter table fcpay.FC_RISK_PREPAID_ACCOUNT_CHANGE_INFO add KEY CN_TIME_TYPE_KEY(CUSTOMER_NAME,ACCOUNT_CHANGE_TIME,ACCOUNT_CHANGE_TYPE);
alter table fcpay.FC_WITHDRAW_APPLY add key APPLY_TIME_KEY(APPLY_TIME);

#优化时间 2015-01-15
ALTER TABLE fcpay.FC_WITHDRAW_APPLY ADD KEY MULTI_KEY1(USER_NAME,APPLY_TIME,RISK_STATUS);
ALTER TABLE fcpay.FC_WITHDRAW_APPLY ADD KEY MULTI_KEY2(USER_NAME,APPLY_TIME,STATUS);
ALTER TABLE fcpay.FC_WITHDRAW_APPLY ADD KEY MULTI_KEY3(STATUS,USER_NAME,APPLY_TIME);
ALTER TABLE fcpay.FC_WITHDRAW_APPLY ADD KEY MULTI_KEY4(BUSINESS_ID,RISK_STATUS,APPLY_TIME);
ALTER table fcpay.FC_WITHDRAW_APPLY ADD KEY APPLY_TIME_KEY(APPLY_TIME);

#优化时间 2015-01-16
ALTER TABLE npe.tasks add key multikey1(interstate,obtainer,taskname,obtaintime);
ALTER TABLE npe.tasks add key multikey2(procinstid,taskdefid);
ALTER TABLE npe.tasks add key multikey3(nodetype,taskname,interstate);
ALTER TABLE npe.tasks add key multikey4(nodetype,taskcenter,interstate);
ALTER TABLE npe.oplogs add key createtime_key(createtime);
ALTER TABLE fcpay.FC_CRM_MEMBER add key multikey(CUSTOMER_NAME,BUSINESS_ID);
ALTER TABLE fcpay.FC_RISK_GAME_WINNING_INFO add KEY multikey1 (`CUSTOMER_NAME`,`BUSINESS_ID`,`BET_TIME`,`GAME_RULE`,`GAME_DRAW_TIME`);

#优化时间 2015-01-20
ALTER TABLE fcpay.FC_RISK_SORT_RULE ADD INDEX FC_RSR_INDEX6(RULE_TYPE,RULE_FLAG);