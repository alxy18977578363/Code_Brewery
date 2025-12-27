-- ============================================
-- 放射性物质监测系统数据库
-- 基于关系模式.md设计
-- ============================================

-- 创建数据库
DROP DATABASE IF EXISTS MarineRadioactivityDB;
CREATE DATABASE MarineRadioactivityDB
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE MarineRadioactivityDB;

-- ================================
-- 1. 放射性核素表 (Radionuclide)
-- ================================
CREATE TABLE IF NOT EXISTS `Radionuclide` (
    `NuclideID` INT AUTO_INCREMENT PRIMARY KEY COMMENT '核素ID',
    `Name` VARCHAR(100) NOT NULL COMMENT '名称',
    `Symbol` VARCHAR(20) NOT NULL UNIQUE COMMENT '符号标识',
    `HalfLife` VARCHAR(100) DEFAULT NULL COMMENT '半衰期',
    `RadioactiveType` VARCHAR(50) DEFAULT NULL COMMENT '放射性类型 (如α、β、γ)',

    KEY `idx_symbol` (`Symbol`),
    KEY `idx_name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='放射性核素表';


-- ================================
-- 2. 洋流表 (OceanCurrent)
-- ================================
CREATE TABLE IF NOT EXISTS `OceanCurrent` (
    `CurrentName` VARCHAR(100) PRIMARY KEY COMMENT '洋流名称',
    `Direction` VARCHAR(50) DEFAULT NULL COMMENT '流向',
    `FlowRate` DECIMAL(10,2) DEFAULT NULL COMMENT '流量 (单位：Sv)',
    `Velocity` DECIMAL(10,2) DEFAULT NULL COMMENT '流速 (单位：m/s)',

    KEY `idx_direction` (`Direction`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='洋流表';


-- ================================
-- 3. 放射源表 (RadioactiveSource)
-- ================================
CREATE TABLE IF NOT EXISTS `RadioactiveSource` (
    `SourceID` INT AUTO_INCREMENT PRIMARY KEY COMMENT '放射源ID',
    `SourceOrigin` VARCHAR(200) NOT NULL COMMENT '来源 (如核电站、核试验等)',
    `DiscoveryTime` DATETIME DEFAULT NULL COMMENT '发现时间',
    `OperationStatus` ENUM('Active', 'Inactive', 'Monitoring', 'Decommissioned') DEFAULT 'Monitoring' COMMENT '运行状态',
    `Longitude` DECIMAL(10,6) NOT NULL COMMENT '经度',
    `Latitude` DECIMAL(10,6) NOT NULL COMMENT '纬度',
    `CountryISO` CHAR(3) DEFAULT NULL COMMENT '国家ISO编码',
    `NuclideID` INT NOT NULL COMMENT '核素ID (外键)',

    KEY `idx_coordinates` (`Latitude`, `Longitude`),
    KEY `idx_status` (`OperationStatus`),
    KEY `idx_country` (`CountryISO`),
    KEY `idx_nuclide` (`NuclideID`),
    KEY `idx_discovery_time` (`DiscoveryTime`),

    CONSTRAINT `fk_source_nuclide` FOREIGN KEY (`NuclideID`) REFERENCES `Radionuclide`(`NuclideID`)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='放射源表';


-- ================================
-- 4. 洋流-放射源关系表 (流经关系 m:n)
-- ================================
CREATE TABLE IF NOT EXISTS `CurrentSourceRelation` (
    `RelationID` INT AUTO_INCREMENT PRIMARY KEY COMMENT '关系ID',
    `CurrentName` VARCHAR(100) NOT NULL COMMENT '洋流名称',
    `SourceID` INT NOT NULL COMMENT '放射源ID',
    `ImpactLevel` ENUM('Low', 'Medium', 'High') DEFAULT 'Medium' COMMENT '影响等级',

    UNIQUE KEY `uq_current_source` (`CurrentName`, `SourceID`),
    KEY `idx_current` (`CurrentName`),
    KEY `idx_source` (`SourceID`),

    CONSTRAINT `fk_relation_current` FOREIGN KEY (`CurrentName`) REFERENCES `OceanCurrent`(`CurrentName`)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_relation_source` FOREIGN KEY (`SourceID`) REFERENCES `RadioactiveSource`(`SourceID`)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='洋流-放射源关系表';


-- ================================
-- 5. 监测站点表 (Station)
-- ================================
CREATE TABLE IF NOT EXISTS `Station` (
    `StationID` INT AUTO_INCREMENT PRIMARY KEY COMMENT '站点ID',
    `StationName` VARCHAR(100) NOT NULL COMMENT '站点名称',
    `Longitude` DECIMAL(10,6) NOT NULL COMMENT '经度',
    `Latitude` DECIMAL(10,6) NOT NULL COMMENT '纬度',
    `OceanDepth` DECIMAL(10,2) DEFAULT NULL COMMENT '海洋深度 (单位：米)',
    `RegionDescription` VARCHAR(200) DEFAULT NULL COMMENT '区域描述',
    `StationType` VARCHAR(50) DEFAULT NULL COMMENT '站点类型 (如近岸、深海、河口等)',

    KEY `idx_coordinates` (`Latitude`, `Longitude`),
    KEY `idx_station_name` (`StationName`),
    KEY `idx_station_type` (`StationType`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='监测站点表';


-- ================================
-- 6. 样本表 (Sample)
-- ================================
CREATE TABLE IF NOT EXISTS `Sample` (
    `SampleID` INT AUTO_INCREMENT PRIMARY KEY COMMENT '样本ID',
    `SampleType` ENUM('Biota', 'Seawater', 'Sediment', 'Suspended Matter') NOT NULL COMMENT '样本类型',
    `SamplingTime` DATETIME NOT NULL COMMENT '采样时间',
    `SamplingDepth` DECIMAL(10,2) DEFAULT NULL COMMENT '采样深度 (单位：米)',
    `LocationDescription` VARCHAR(200) DEFAULT NULL COMMENT '位置描述',
    `StationID` INT NOT NULL COMMENT '站点ID (外键)',

    KEY `idx_station` (`StationID`),
    KEY `idx_sample_type` (`SampleType`),
    KEY `idx_sampling_time` (`SamplingTime`),

    CONSTRAINT `fk_sample_station` FOREIGN KEY (`StationID`) REFERENCES `Station`(`StationID`)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='样本表';


-- ================================
-- 7. 检测记录表 (MeasurementRecord)
-- ================================
CREATE TABLE IF NOT EXISTS `MeasurementRecord` (
    `RecordID` INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    `Activity` DECIMAL(18,9) NOT NULL COMMENT '活度值',
    `Uncertainty` DECIMAL(18,9) DEFAULT NULL COMMENT '不确定度',
    `Unit` VARCHAR(30) NOT NULL COMMENT '单位 (如 Bq/L, Bq/kg)',
    `MeasurementType` VARCHAR(50) DEFAULT NULL COMMENT '测量类型 (如γ能谱、液闪)',
    `TestingOrganization` VARCHAR(200) DEFAULT NULL COMMENT '检测机构',
    `ReportNumber` VARCHAR(100) DEFAULT NULL COMMENT '报告编号',
    `CompletionTime` DATETIME DEFAULT NULL COMMENT '完成时间',
    `SampleID` INT NOT NULL COMMENT '样本ID (外键)',
    `NuclideID` INT NOT NULL COMMENT '核素ID (外键)',

    KEY `idx_sample` (`SampleID`),
    KEY `idx_nuclide` (`NuclideID`),
    KEY `idx_completion_time` (`CompletionTime`),
    KEY `idx_report_number` (`ReportNumber`),

    CONSTRAINT `fk_record_sample` FOREIGN KEY (`SampleID`) REFERENCES `Sample`(`SampleID`)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_record_nuclide` FOREIGN KEY (`NuclideID`) REFERENCES `Radionuclide`(`NuclideID`)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='检测记录表';


-- ================================
-- 8. 用户表 (User)
-- ================================
CREATE TABLE IF NOT EXISTS `User` (
    `UserID` INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    `Username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    `Role` ENUM('Admin', 'DataManager', 'Viewer') NOT NULL DEFAULT 'Viewer' COMMENT '角色',
    `Email` VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
    `RegistrationTime` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',

    KEY `idx_role` (`Role`),
    KEY `idx_username` (`Username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';


-- ================================
-- 9. 用户-检测记录关系表 (查看/审核关系 1:n)
-- 可选：如果需要记录用户对记录的操作历史
-- ================================
CREATE TABLE IF NOT EXISTS `UserRecordRelation` (
    `RelationID` INT AUTO_INCREMENT PRIMARY KEY COMMENT '关系ID',
    `UserID` INT NOT NULL COMMENT '用户ID',
    `RecordID` INT NOT NULL COMMENT '记录ID',
    `ActionType` ENUM('View', 'Audit', 'Edit', 'Delete') NOT NULL COMMENT '操作类型',
    `ActionTime` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',

    KEY `idx_user` (`UserID`),
    KEY `idx_record` (`RecordID`),
    KEY `idx_action_time` (`ActionTime`),

    CONSTRAINT `fk_user_relation` FOREIGN KEY (`UserID`) REFERENCES `User`(`UserID`)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_record_relation` FOREIGN KEY (`RecordID`) REFERENCES `MeasurementRecord`(`RecordID`)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户-检测记录关系表';

