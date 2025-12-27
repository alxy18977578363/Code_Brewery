-- Create ApprovalRequest Table
USE MarineRadioactivityDB;

DROP TABLE IF EXISTS `ApprovalRequest`;

CREATE TABLE `ApprovalRequest` (
    `RequestID` INT AUTO_INCREMENT PRIMARY KEY,
    `RequestUserID` INT NOT NULL,
    `RequestUserName` VARCHAR(100) NOT NULL,
    `TargetTable` VARCHAR(100) NOT NULL,
    `OperationType` ENUM('Add', 'Delete') NOT NULL,
    `OperationData` TEXT NOT NULL,
    `Status` ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    `RequestTime` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `ApproverID` INT DEFAULT NULL,
    `ApproverName` VARCHAR(100) DEFAULT NULL,
    `ApprovalTime` TIMESTAMP NULL DEFAULT NULL,
    `ApprovalComment` TEXT DEFAULT NULL,
    KEY `idx_status` (`Status`),
    KEY `idx_request_user` (`RequestUserID`),
    KEY `idx_request_time` (`RequestTime`),
    KEY `idx_approver` (`ApproverID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SELECT 'ApprovalRequest table created successfully!' AS Result;
