-- ============================================================
-- RAG 企业内部知识库问答 Agent 系统 数据库初始化脚本
-- 数据库：db_enterprise_ga  字符集：utf8mb4
-- 说明：包含建库、建表 DDL 以及测试数据
-- 默认密码均为 123456，对应 MD5 值：e10adc3949ba59abbe56e057f20f883e
-- ============================================================

-- 创建数据库（若不存在）
CREATE DATABASE IF NOT EXISTS `db_enterprise_ga`
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_general_ci;

USE `db_enterprise_ga`;

-- ------------------------------------------------------------
-- 用户表 t_user
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `t_user`;
CREATE TABLE `t_user` (
    `id`          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '用户主键ID',
    `username`    VARCHAR(50)  NOT NULL COMMENT '登录用户名',
    `password`    CHAR(32)     NOT NULL COMMENT '密码（MD5加密，32位）',
    `real_name`   VARCHAR(50)  DEFAULT NULL COMMENT '真实姓名',
    `role`        VARCHAR(20)  NOT NULL DEFAULT 'user' COMMENT '角色：admin=管理员，user=普通用户',
    `status`      TINYINT      NOT NULL DEFAULT 1 COMMENT '状态：1=启用，0=禁用',
    `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ------------------------------------------------------------
-- 文档表 t_document
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `t_document`;
CREATE TABLE `t_document` (
    `id`          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '文档主键ID',
    `title`       VARCHAR(255) NOT NULL COMMENT '文档标题',
    `filename`    VARCHAR(255) NOT NULL COMMENT '原始文件名',
    `file_path`   VARCHAR(500) NOT NULL COMMENT '服务器存储路径',
    `file_type`   VARCHAR(20)  NOT NULL COMMENT '文件类型：pdf/txt/md/docx',
    `file_size`   BIGINT       NOT NULL DEFAULT 0 COMMENT '文件大小（字节）',
    `chunk_count` INT          NOT NULL DEFAULT 0 COMMENT '切片数量（写入向量库的片段数）',
    `status`      TINYINT      NOT NULL DEFAULT 1 COMMENT '状态：1=已入库，0=处理中/失败',
    `uploader_id` BIGINT       DEFAULT NULL COMMENT '上传人ID',
    `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_uploader` (`uploader_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识库文档表';

-- ------------------------------------------------------------
-- 问答历史表 t_chat_history
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `t_chat_history`;
CREATE TABLE `t_chat_history` (
    `id`          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '问答记录主键ID',
    `user_id`     BIGINT       NOT NULL COMMENT '提问用户ID',
    `session_id`  VARCHAR(64)  DEFAULT NULL COMMENT '会话ID（同一会话多轮问答共享）',
    `question`    TEXT         NOT NULL COMMENT '用户问题',
    `answer`      MEDIUMTEXT   DEFAULT NULL COMMENT 'Agent回答',
    `sources`     TEXT         DEFAULT NULL COMMENT '引用来源（JSON字符串）',
    `use_web`     TINYINT      NOT NULL DEFAULT 0 COMMENT '是否启用联网搜索：1=是，0=否',
    `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_user` (`user_id`),
    KEY `idx_session` (`session_id`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='问答历史记录表';

-- ============================================================
-- 测试数据
-- ============================================================

-- 用户测试数据（密码均为 123456 -> MD5: e10adc3949ba59abbe56e057f20f883e）
INSERT INTO `t_user` (`username`, `password`, `real_name`, `role`, `status`) VALUES
('admin',  'e10adc3949ba59abbe56e057f20f883e', '系统管理员', 'admin', 1),
('user01', 'e10adc3949ba59abbe56e057f20f883e', '张三',       'user',  1),
('user02', 'e10adc3949ba59abbe56e057f20f883e', '李四',       'user',  1),
('user03', 'e10adc3949ba59abbe56e057f20f883e', '王五',       'user',  0);

-- 文档测试数据（仅展示用，实际向量内容以上传后写入 Chroma 为准）
INSERT INTO `t_document` (`title`, `filename`, `file_path`, `file_type`, `file_size`, `chunk_count`, `status`, `uploader_id`) VALUES
('员工入职手册',     'onboarding.pdf',  'uploads/onboarding.pdf',  'pdf',  204800, 12, 1, 1),
('考勤管理制度',     'attendance.docx', 'uploads/attendance.docx', 'docx', 51200,  6,  1, 1),
('报销流程说明',     'expense.md',      'uploads/expense.md',      'md',   10240,  3,  1, 1),
('信息安全规范',     'security.txt',    'uploads/security.txt',    'txt',  8192,   2,  1, 1);

-- 问答历史测试数据（覆盖最近 7 天，供首页折线图统计；按 session_id 分组为多个会话）
INSERT INTO `t_chat_history` (`user_id`, `session_id`, `question`, `answer`, `sources`, `use_web`, `create_time`) VALUES
-- 张三(2) 会话A：入职/制度咨询（3 轮）
(2, 'sess-u2-a', '新员工入职需要准备哪些材料？', '需准备身份证、学历证明、银行卡等材料，详见入职手册。', '[{"title":"员工入职手册"}]', 0, DATE_SUB(NOW(), INTERVAL 6 DAY)),
(2, 'sess-u2-a', '公司的考勤打卡时间是几点？',   '上班 9:00，下班 18:00，详见考勤管理制度。',           '[{"title":"考勤管理制度"}]', 0, DATE_SUB(NOW(), INTERVAL 5 DAY)),
(2, 'sess-u2-a', '年假有多少天？',               '根据工龄不同，年假为5-15天。',                          '[{"title":"员工入职手册"}]', 0, DATE_SUB(NOW(), INTERVAL 3 DAY)),
-- 张三(2) 会话B：报销（1 轮）
(2, 'sess-u2-b', '出差报销标准是多少？',         '住宿费每天不超过400元，详见报销流程说明。',             '[{"title":"报销流程说明"}]', 0, DATE_SUB(NOW(), INTERVAL 1 DAY)),
-- 李四(3) 会话A：报销/调休（2 轮）
(3, 'sess-u3-a', '报销需要哪些发票？',           '需提供正规增值税发票并粘贴在报销单上。',               '[{"title":"报销流程说明"}]', 0, DATE_SUB(NOW(), INTERVAL 5 DAY)),
(3, 'sess-u3-a', '如何申请调休？',               '提前在系统提交调休申请并经主管审批。',                   '[{"title":"考勤管理制度"}]', 0, NOW()),
-- 李四(3) 会话B：安全/联网（2 轮）
(3, 'sess-u3-b', '密码安全有什么要求？',         '密码长度不少于8位，需包含字母和数字。',                 '[{"title":"信息安全规范"}]', 0, DATE_SUB(NOW(), INTERVAL 4 DAY)),
(3, 'sess-u3-b', '最新的人工智能政策是什么？',   '根据联网搜索结果整理的最新政策信息。',                   '[{"title":"网络搜索结果"}]', 1, DATE_SUB(NOW(), INTERVAL 2 DAY));
