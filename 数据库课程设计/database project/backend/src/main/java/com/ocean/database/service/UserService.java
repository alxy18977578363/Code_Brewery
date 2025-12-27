package com.ocean.database.service;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.ocean.database.config.DatabaseConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

/**
 * 用户服务
 */
public class UserService extends BaseService {
    private static final Logger logger = LoggerFactory.getLogger(UserService.class);
    private final Gson gson = new Gson();
    
    @Override
    public String getAll() throws Exception {
        logger.info("获取所有用户");
        
        try (Connection conn = DatabaseConfig.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT * FROM User")) {
            
            JsonArray users = new JsonArray();
            while (rs.next()) {
                users.add(resultSetToJson(rs));
            }
            
            JsonObject response = new JsonObject();
            response.add("data", users);
            return gson.toJson(response);
            
        } catch (Exception e) {
            logger.error("获取用户列表失败", e);
            throw new Exception("获取用户列表失败: " + e.getMessage());
        }
    }
    
    @Override
    public String getById(String id) throws Exception {
        logger.info("获取用户: {}", id);
        
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement("SELECT * FROM User WHERE UserID = ?")) {
            
            stmt.setInt(1, Integer.parseInt(id));
            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    JsonObject response = new JsonObject();
                    response.add("data", resultSetToJson(rs));
                    return gson.toJson(response);
                } else {
                    throw new Exception("用户不存在: " + id);
                }
            }
            
        } catch (Exception e) {
            logger.error("获取用户失败", e);
            throw new Exception("获取用户失败: " + e.getMessage());
        }
    }
    
    @Override
    public String create(String jsonBody) throws Exception {
        logger.info("创建用户: {}", jsonBody);
        JsonObject data = gson.fromJson(jsonBody, JsonObject.class);
        
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement(
                 "INSERT INTO User (Username, Email, Role) VALUES (?, ?, ?)",
                 Statement.RETURN_GENERATED_KEYS)) {
            
            stmt.setString(1, data.get("Username").getAsString());
            stmt.setString(2, data.has("Email") ? data.get("Email").getAsString() : null);
            stmt.setString(3, data.has("Role") ? data.get("Role").getAsString() : "Viewer");
            
            int affected = stmt.executeUpdate();
            ResultSet rs = stmt.getGeneratedKeys();
            
            JsonObject response = new JsonObject();
            if (rs.next()) {
                response.addProperty("UserID", rs.getInt(1));
            }
            response.addProperty("message", "用户创建成功");
            return gson.toJson(response);
            
        } catch (Exception e) {
            logger.error("创建用户失败", e);
            throw new Exception("创建用户失败: " + e.getMessage());
        }
    }
    
    @Override
    public String update(String id, String jsonBody) throws Exception {
        logger.info("更新用户 {}: {}", id, jsonBody);
        JsonObject data = gson.fromJson(jsonBody, JsonObject.class);
        
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement(
                 "UPDATE User SET Username=?, Email=?, Role=? WHERE UserID=?")) {
            
            stmt.setString(1, data.get("Username").getAsString());
            stmt.setString(2, data.has("Email") ? data.get("Email").getAsString() : null);
            stmt.setString(3, data.has("Role") ? data.get("Role").getAsString() : "Viewer");
            stmt.setInt(4, Integer.parseInt(id));
            
            int affected = stmt.executeUpdate();
            
            JsonObject response = new JsonObject();
            response.addProperty("message", "用户更新成功");
            response.addProperty("affected", affected);
            return gson.toJson(response);
            
        } catch (Exception e) {
            logger.error("更新用户失败", e);
            throw new Exception("更新用户失败: " + e.getMessage());
        }
    }
    
    @Override
    public String delete(String id) throws Exception {
        logger.info("删除用户: {}", id);
        
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement("DELETE FROM User WHERE UserID = ?")) {
            
            stmt.setInt(1, Integer.parseInt(id));
            int affected = stmt.executeUpdate();
            
            JsonObject response = new JsonObject();
            response.addProperty("message", "用户删除成功");
            response.addProperty("affected", affected);
            return gson.toJson(response);
            
        } catch (Exception e) {
            logger.error("删除用户失败", e);
            throw new Exception("删除用户失败: " + e.getMessage());
        }
    }
    
    private JsonObject resultSetToJson(ResultSet rs) throws SQLException {
        JsonObject obj = new JsonObject();
        obj.addProperty("UserID", rs.getInt("UserID"));
        obj.addProperty("Username", rs.getString("Username"));
        obj.addProperty("Email", rs.getString("Email"));
        obj.addProperty("Role", rs.getString("Role"));
        obj.addProperty("RegistrationTime", rs.getTimestamp("RegistrationTime") != null ? 
            rs.getTimestamp("RegistrationTime").toString() : null);
        return obj;
    }
}
