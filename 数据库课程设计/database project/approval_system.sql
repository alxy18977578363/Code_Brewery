-- ============================================
-- 数据管理审批系统表
-- ============================================

USE MarineRadioactivityDB;

-- 创建审批请求表
CREATE TABLE IF NOT EXISTS `ApprovalRequest` (
    `RequestID` INT AUTO_INCREMENT PRIMARY KEY COMMENT '审批请求ID',
    `RequestUserID` INT NOT NULL COMMENT '请求用户ID',
    `RequestUserName` VARCHAR(100) NOT NULL COMMENT '请求用户名',
    `TargetTable` VARCHAR(100) NOT NULL COMMENT '目标表名',
    `OperationType` ENUM('Add', 'Delete') NOT NULL COMMENT '操作类型',
    `OperationData` TEXT NOT NULL COMMENT '操作数据(JSON格式)',
    `Status` ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending' COMMENT '审批状态',
    `RequestTime` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '请求时间',
    `ApproverID` INT DEFAULT NULL COMMENT '审批人ID',
    `ApproverName` VARCHAR(100) DEFAULT NULL COMMENT '审批人姓名',
    `ApprovalTime` TIMESTAMP NULL DEFAULT NULL COMMENT '审批时间',
    `ApprovalComment` TEXT DEFAULT NULL COMMENT '审批意见',

    KEY `idx_status` (`Status`),
    KEY `idx_request_user` (`RequestUserID`),
    KEY `idx_request_time` (`RequestTime`),
    KEY `idx_approver` (`ApproverID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据管理审批请求表';

-- 插入示例数据（可选）
INSERT INTO `ApprovalRequest` 
    (`RequestUserID`, `RequestUserName`, `TargetTable`, `OperationType`, `OperationData`, `Status`)
VALUES 
    (2, '数据管理员张三', 'Radionuclide', 'Add', '{"Name":"铯-137","Symbol":"Cs-137","HalfLife":"30.17年","RadioactiveType":"β、γ"}', 'Pending'),
    (2, '数据管理员张三', 'Sample', 'Delete', '{"SampleID":5}', 'Pending');
