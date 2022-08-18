CREATE TABLE `sign_in` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `uId` varchar(100) NOT NULL COMMENT '工号',
  `name` varchar(100) DEFAULT NULL COMMENT '姓名',
  `time` datetime DEFAULT NULL COMMENT '签到时间',
  `machine` varchar(100) DEFAULT NULL COMMENT '签到卡机',
  `isEffective` varchar(100) DEFAULT NULL COMMENT '是否有效',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COMMENT='用户签到信息';

INSERT INTO `user`.sign_in (uId,name,`time`,machine,isEffective) VALUES
	 ('9527','无情打卡机器','2022-08-04 07:59:40.0','深圳','Y'),
	 ('9527','无情打卡机器','2022-08-04 17:30:20.0','深圳','Y'),
	 ('9527','无情打卡机器','2022-08-05 17:30:20.0','深圳','Y'),
	 ('9527','无情打卡机器','2022-08-05 07:59:40.0','深圳','Y'),
	 ('9527','无情打卡机器','2022-08-08 08:06:01.0','深圳','Y'),
	 ('9527','无情打卡机器','2022-08-08 18:05:44.0','深圳','Y'),
	 ('9527','无情打卡机器','2022-08-09 07:56:46.0','深圳','Y'),
	 ('9527','无情打卡机器','2022-08-11 07:57:00.0','深圳','Y');