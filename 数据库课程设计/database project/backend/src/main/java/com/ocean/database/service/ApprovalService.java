package com.ocean.database.service;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;
import com.ocean.database.config.DatabaseConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.lang.reflect.Type;
import java.sql.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 审批服务 - 处理数据管理的审批流程
 */
public class ApprovalService extends BaseService {
    private static final Logger logger = LoggerFactory.getLogger(ApprovalService.class);
    private final Gson gson = new GsonBuilder().setPrettyPrinting().create();

    /**
     * 提交审批请求
     */
    public String submitApprovalRequest(String requestBody) throws Exception {
        Type type = new TypeToken<Map<String, Object>>(){}.getType();
        Map<String, Object> request = gson.fromJson(requestBody, type);
        
        String table = (String) request.get("table");
        String requestUser = (String) request.get("requestUser");
        Integer requestUserID = ((Number) request.get("requestUserID")).intValue();
        
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> operations = (List<Map<String, Object>>) request.get("operations");
        
        int insertedCount = 0;
        
        String sql = "INSERT INTO ApprovalRequest (RequestUserID, RequestUserName, TargetTable, OperationType, OperationData, Status) " +
                     "VALUES (?, ?, ?, ?, ?, 'Pending')";
        
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            
            for (Map<String, Object> operation : operations) {
                String operationType = (String) operation.get("type");
                @SuppressWarnings("unchecked")
                Map<String, Object> data = (Map<String, Object>) operation.get("data");
                
                pstmt.setInt(1, requestUserID);
                pstmt.setString(2, requestUser);
                pstmt.setString(3, table);
                pstmt.setString(4, operationType.equals("add") ? "Add" : "Delete");
                pstmt.setString(5, gson.toJson(data));
                
                pstmt.executeUpdate();
                insertedCount++;
            }
            
            logger.info("提交审批请求成功: 用户={}, 表={}, 操作数={}", requestUser, table, insertedCount);
            
        } catch (SQLException e) {
            logger.error("提交审批请求失败", e);
            throw new Exception("提交审批请求失败: " + e.getMessage());
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("count", insertedCount);
        result.put("message", "已提交" + insertedCount + "个审批请求");
        
        return gson.toJson(result);
    }

    /**
     * 获取所有待审批的请求（管理员用）
     */
    public String getPendingApprovals() throws Exception {
        List<Map<String, Object>> approvals = new ArrayList<>();
        
        String sql = "SELECT * FROM ApprovalRequest WHERE Status = 'Pending' ORDER BY RequestTime DESC";
        
        try (Connection conn = DatabaseConfig.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            while (rs.next()) {
                Map<String, Object> approval = new HashMap<>();
                approval.put("RequestID", rs.getInt("RequestID"));
                approval.put("RequestUserID", rs.getInt("RequestUserID"));
                approval.put("RequestUserName", rs.getString("RequestUserName"));
                approval.put("TargetTable", rs.getString("TargetTable"));
                approval.put("OperationType", rs.getString("OperationType"));
                approval.put("OperationData", rs.getString("OperationData"));
                approval.put("Status", rs.getString("Status"));
                approval.put("RequestTime", rs.getTimestamp("RequestTime").toString());
                approvals.add(approval);
            }
            
            logger.info("获取待审批请求: {} 个", approvals.size());
            
        } catch (SQLException e) {
            logger.error("获取待审批请求失败", e);
            throw new Exception("获取待审批请求失败: " + e.getMessage());
        }
        
        return gson.toJson(approvals);
    }

    /**
     * 审批请求（同意）
     */
    public String approveRequest(String requestId, String approverName, int approverId) throws Exception {
        int id = Integer.parseInt(requestId);
        
        // 获取审批请求详情
        Map<String, Object> request = getApprovalRequestById(id);
        
        if (request == null) {
            throw new Exception("审批请求不存在");
        }
        
        String status = (String) request.get("Status");
        if (!"Pending".equals(status)) {
            throw new Exception("该请求已被处理");
        }
        
        // 执行操作
        String targetTable = (String) request.get("TargetTable");
        String operationType = (String) request.get("OperationType");
        String operationData = (String) request.get("OperationData");
        
        try (Connection conn = DatabaseConfig.getConnection()) {
            conn.setAutoCommit(false);
            
            try {
                // 执行数据操作
                executeApprovedOperation(conn, targetTable, operationType, operationData);
                
                // 更新审批状态
                String updateSql = "UPDATE ApprovalRequest SET Status = 'Approved', ApproverID = ?, " +
                                  "ApproverName = ?, ApprovalTime = NOW() WHERE RequestID = ?";
                try (PreparedStatement pstmt = conn.prepareStatement(updateSql)) {
                    pstmt.setInt(1, approverId);
                    pstmt.setString(2, approverName);
                    pstmt.setInt(3, id);
                    pstmt.executeUpdate();
                }
                
                conn.commit();
                logger.info("审批通过: RequestID={}, 审批人={}", id, approverName);
                
            } catch (Exception e) {
                conn.rollback();
                logger.error("执行审批操作失败: RequestID={}", id, e);
                throw new Exception("审批执行失败: " + e.getMessage());
            }
        } catch (SQLException e) {
            logger.error("数据库连接失败", e);
            throw new Exception("数据库连接失败: " + e.getMessage());
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("message", "审批通过，操作已执行");
        
        return gson.toJson(result);
    }

    /**
     * 拒绝审批请求
     */
    public String rejectRequest(String requestId, String approverName, int approverId, String comment) throws Exception {
        int id = Integer.parseInt(requestId);
        
        String sql = "UPDATE ApprovalRequest SET Status = 'Rejected', ApproverID = ?, " +
                     "ApproverName = ?, ApprovalTime = NOW(), ApprovalComment = ? WHERE RequestID = ? AND Status = 'Pending'";
        
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setInt(1, approverId);
            pstmt.setString(2, approverName);
            pstmt.setString(3, comment);
            pstmt.setInt(4, id);
            
            int affected = pstmt.executeUpdate();
            
            if (affected == 0) {
                throw new Exception("审批请求不存在或已被处理");
            }
            
            logger.info("审批拒绝: RequestID={}, 审批人={}, 原因={}", id, approverName, comment);
            
        } catch (SQLException e) {
            logger.error("拒绝审批失败", e);
            throw new Exception("拒绝审批失败: " + e.getMessage());
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("message", "已拒绝该审批请求");
        
        return gson.toJson(result);
    }

    /**
     * 获取审批请求详情
     */
    private Map<String, Object> getApprovalRequestById(int requestId) throws SQLException {
        String sql = "SELECT * FROM ApprovalRequest WHERE RequestID = ?";
        
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setInt(1, requestId);
            
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    Map<String, Object> request = new HashMap<>();
                    request.put("RequestID", rs.getInt("RequestID"));
                    request.put("RequestUserID", rs.getInt("RequestUserID"));
                    request.put("RequestUserName", rs.getString("RequestUserName"));
                    request.put("TargetTable", rs.getString("TargetTable"));
                    request.put("OperationType", rs.getString("OperationType"));
                    request.put("OperationData", rs.getString("OperationData"));
                    request.put("Status", rs.getString("Status"));
                    return request;
                }
            }
        }
        
        return null;
    }

    /**
     * 执行已批准的操作
     */
    private void executeApprovedOperation(Connection conn, String targetTable, String operationType, 
                                         String operationData) throws Exception {
        Type type = new TypeToken<Map<String, Object>>(){}.getType();
        Map<String, Object> data = gson.fromJson(operationData, type);
        
        DataManagementService dataService = new DataManagementService();
        
        try {
            if ("Add".equals(operationType)) {
                dataService.insertRecord(conn, targetTable, data);
            } else if ("Delete".equals(operationType)) {
                dataService.deleteRecord(conn, targetTable, data);
            } else {
                throw new Exception("未知的操作类型: " + operationType);
            }
        } catch (SQLException e) {
            // 处理外键约束等SQL异常
            String errorMsg = e.getMessage();
            if (errorMsg.contains("foreign key constraint")) {
                throw new Exception("无法删除：该记录被其他数据引用。请先删除相关联的记录。");
            } else if (errorMsg.contains("Duplicate entry")) {
                throw new Exception("无法添加：记录已存在或主键重复。");
            } else {
                throw new Exception("数据库操作失败: " + errorMsg);
            }
        }
    }

    @Override
    public String getAll() throws Exception {
        return getPendingApprovals();
    }

    @Override
    public String getById(String id) throws Exception {
        throw new Exception("不支持的操作");
    }

    @Override
    public String create(String data) throws Exception {
        return submitApprovalRequest(data);
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
