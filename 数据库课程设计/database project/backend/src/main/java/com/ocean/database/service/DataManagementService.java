package com.ocean.database.service;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonSerializer;
import com.google.gson.reflect.TypeToken;
import com.ocean.database.config.DatabaseConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.lang.reflect.Type;
import java.sql.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 数据管理服务 - 用于管理员查看和管理所有表（除用户表外）
 */
public class DataManagementService extends BaseService {
    private static final Logger logger = LoggerFactory.getLogger(DataManagementService.class);
    private final Gson gson;
    
    public DataManagementService() {
        // 配置Gson以支持日期时间类型
        this.gson = new GsonBuilder()
            .setPrettyPrinting()
            .registerTypeAdapter(LocalDateTime.class, 
                (JsonSerializer<LocalDateTime>) (src, typeOfSrc, context) -> 
                    context.serialize(src.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))))
            .registerTypeAdapter(java.sql.Timestamp.class,
                (JsonSerializer<Timestamp>) (src, typeOfSrc, context) ->
                    context.serialize(src.toString()))
            .registerTypeAdapter(java.sql.Date.class,
                (JsonSerializer<Date>) (src, typeOfSrc, context) ->
                    context.serialize(src.toString()))
            .create();
    }

    /**
     * 获取所有可管理的表列表
     */
    public String getAllTables() {
        List<Map<String, String>> tables = new ArrayList<>();
        
        // 添加所有非用户表（根据demo.sql）
        tables.add(createTableInfo("Radionuclide", "放射性核素表", "radionuclide"));
        tables.add(createTableInfo("OceanCurrent", "洋流表", "oceancurrent"));
        tables.add(createTableInfo("RadioactiveSource", "放射源表", "radioactivesource"));
        tables.add(createTableInfo("CurrentSourceRelation", "洋流-放射源关系表", "relation"));
        tables.add(createTableInfo("Station", "监测站点表", "station"));
        tables.add(createTableInfo("Sample", "样本表", "sample"));
        tables.add(createTableInfo("MeasurementRecord", "检测记录表", "measurement"));
        tables.add(createTableInfo("UserRecordRelation", "用户记录关系表", "userrecord"));
        
        Map<String, Object> result = new HashMap<>();
        result.put("tables", tables);
        result.put("total", tables.size());
        
        return gson.toJson(result);
    }
    
    private Map<String, String> createTableInfo(String tableName, String displayName, String type) {
        Map<String, String> info = new HashMap<>();
        info.put("table", tableName);
        info.put("name", displayName);
        info.put("type", type);
        return info;
    }

    /**
     * 获取指定表的所有数据
     */
    public String getTableData(String tableName) throws Exception {
        // 安全检查：只允许查询特定的表
        if (!isValidTable(tableName)) {
            throw new Exception("不允许访问该表: " + tableName);
        }

        List<Map<String, Object>> data = new ArrayList<>();
        
        String sql = "SELECT * FROM " + tableName;
        
        try (Connection conn = DatabaseConfig.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            ResultSetMetaData metaData = rs.getMetaData();
            int columnCount = metaData.getColumnCount();
            
            while (rs.next()) {
                Map<String, Object> row = new HashMap<>();
                for (int i = 1; i <= columnCount; i++) {
                    String columnName = metaData.getColumnName(i);
                    Object value = rs.getObject(i);
                    row.put(columnName, value);
                }
                data.add(row);
            }
            
            logger.info("查询表 {} 成功，返回 {} 条记录", tableName, data.size());
            
        } catch (SQLException e) {
            logger.error("查询表 {} 失败", tableName, e);
            throw new Exception("查询表数据失败: " + e.getMessage());
        }
        
        return gson.toJson(data);
    }

    /**
     * 获取表结构信息
     */
    public String getTableSchema(String tableName) throws Exception {
        if (!isValidTable(tableName)) {
            throw new Exception("不允许访问该表: " + tableName);
        }

        List<Map<String, String>> columns = new ArrayList<>();
        
        String sql = "SELECT * FROM " + tableName + " WHERE 1=0";
        
        try (Connection conn = DatabaseConfig.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            ResultSetMetaData metaData = rs.getMetaData();
            int columnCount = metaData.getColumnCount();
            
            for (int i = 1; i <= columnCount; i++) {
                Map<String, String> column = new HashMap<>();
                column.put("name", metaData.getColumnName(i));
                column.put("type", metaData.getColumnTypeName(i));
                column.put("nullable", metaData.isNullable(i) == ResultSetMetaData.columnNullable ? "YES" : "NO");
                columns.add(column);
            }
            
        } catch (SQLException e) {
            logger.error("获取表结构失败: {}", tableName, e);
            throw new Exception("获取表结构失败: " + e.getMessage());
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("table", tableName);
        result.put("columns", columns);
        
        return gson.toJson(result);
    }

    /**
     * 批量执行操作（需要管理员权限）
     */
    public String executeBatchOperations(String requestBody) throws Exception {
        Type type = new TypeToken<Map<String, Object>>(){}.getType();
        Map<String, Object> request = gson.fromJson(requestBody, type);
        
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> operations = (List<Map<String, Object>>) request.get("operations");
        String tableName = (String) request.get("table");
        
        if (!isValidTable(tableName)) {
            throw new Exception("不允许操作该表: " + tableName);
        }

        int successCount = 0;
        int failCount = 0;
        List<String> errors = new ArrayList<>();

        try (Connection conn = DatabaseConfig.getConnection()) {
            conn.setAutoCommit(false);
            
            try {
                for (Map<String, Object> operation : operations) {
                    String operationType = (String) operation.get("type");
                    @SuppressWarnings("unchecked")
                    Map<String, Object> data = (Map<String, Object>) operation.get("data");
                    
                    try {
                        if ("add".equals(operationType)) {
                            insertRecord(conn, tableName, data);
                            successCount++;
                        } else if ("delete".equals(operationType)) {
                            deleteRecord(conn, tableName, data);
                            successCount++;
                        }
                    } catch (Exception e) {
                        failCount++;
                        errors.add(e.getMessage());
                        logger.error("执行操作失败: {}", operation, e);
                    }
                }
                
                conn.commit();
                logger.info("批量操作完成: 成功 {}, 失败 {}", successCount, failCount);
                
            } catch (Exception e) {
                conn.rollback();
                throw new Exception("批量操作失败，已回滚: " + e.getMessage());
            }
            
        } catch (SQLException e) {
            logger.error("数据库操作失败", e);
            throw new Exception("数据库操作失败: " + e.getMessage());
        }

        Map<String, Object> result = new HashMap<>();
        result.put("success", successCount);
        result.put("failed", failCount);
        result.put("errors", errors);
        
        return gson.toJson(result);
    }

    /**
     * 插入记录（公开方法，供ApprovalService调用）
     */
    public void insertRecord(Connection conn, String tableName, Map<String, Object> data) throws SQLException {
        StringBuilder columns = new StringBuilder();
        StringBuilder placeholders = new StringBuilder();
        List<Object> values = new ArrayList<>();
        
        for (Map.Entry<String, Object> entry : data.entrySet()) {
            if (columns.length() > 0) {
                columns.append(", ");
                placeholders.append(", ");
            }
            columns.append(entry.getKey());
            placeholders.append("?");
            values.add(entry.getValue());
        }
        
        String sql = String.format("INSERT INTO %s (%s) VALUES (%s)", 
                                   tableName, columns.toString(), placeholders.toString());
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            for (int i = 0; i < values.size(); i++) {
                pstmt.setObject(i + 1, values.get(i));
            }
            pstmt.executeUpdate();
        }
    }

    /**
     * 删除记录（公开方法，供ApprovalService调用）
     */
    public void deleteRecord(Connection conn, String tableName, Map<String, Object> data) throws SQLException {
        // 根据主键删除
        String primaryKey = getPrimaryKey(tableName);
        Object keyValue = data.get(primaryKey);
        
        if (keyValue == null) {
            throw new SQLException("缺少主键值: " + primaryKey);
        }
        
        String sql = String.format("DELETE FROM %s WHERE %s = ?", tableName, primaryKey);
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setObject(1, keyValue);
            pstmt.executeUpdate();
        }
    }

    /**
     * 获取表的主键字段名
     */
    private String getPrimaryKey(String tableName) {
        switch (tableName) {
            case "Radionuclide":
                return "NuclideID";
            case "OceanCurrent":
                return "CurrentName";
            case "RadioactiveSource":
                return "SourceID";
            case "CurrentSourceRelation":
                return "RelationID";
            case "Station":
                return "StationID";
            case "Sample":
                return "SampleID";
            case "MeasurementRecord":
                return "RecordID";
            case "UserRecordRelation":
                return "RelationID";
            default:
                return "ID";
        }
    }

    /**
     * 验证表名是否在允许列表中（不包括User表）
     */
    private boolean isValidTable(String tableName) {
        return tableName != null && (
            tableName.equalsIgnoreCase("Radionuclide") ||
            tableName.equalsIgnoreCase("OceanCurrent") ||
            tableName.equalsIgnoreCase("RadioactiveSource") ||
            tableName.equalsIgnoreCase("CurrentSourceRelation") ||
            tableName.equalsIgnoreCase("Station") ||
            tableName.equalsIgnoreCase("Sample") ||
            tableName.equalsIgnoreCase("MeasurementRecord") ||
            tableName.equalsIgnoreCase("UserRecordRelation")
        );
    }

    @Override
    public String getAll() throws Exception {
        return getAllTables();
    }

    @Override
    public String getById(String id) throws Exception {
        return getTableData(id);
    }

    @Override
    public String create(String data) throws Exception {
        return executeBatchOperations(data);
    }

    @Override
    public String update(String id, String data) throws Exception {
        throw new Exception("不支持的操作");
    }

    @Override
    public String delete(String id) throws Exception {
        throw new Exception("不支持的操作");
    }
}
