package com.ocean.database.service;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.ocean.database.config.DatabaseConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.*;

/**
 * 样本服务
 */
public class SampleService extends BaseService {
    private static final Logger logger = LoggerFactory.getLogger(SampleService.class);
    private final Gson gson = new Gson();
    
    @Override
    public String getAll() throws Exception {
        try (Connection conn = DatabaseConfig.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT * FROM Sample")) {
            
            JsonArray samples = new JsonArray();
            while (rs.next()) {
                JsonObject obj = new JsonObject();
                obj.addProperty("SampleID", rs.getInt("SampleID"));
                obj.addProperty("SampleType", rs.getString("SampleType"));
                obj.addProperty("SamplingTime", rs.getTimestamp("SamplingTime") != null ? 
                    rs.getTimestamp("SamplingTime").toString() : null);
                obj.addProperty("SamplingDepth", rs.getBigDecimal("SamplingDepth"));
                obj.addProperty("LocationDescription", rs.getString("LocationDescription"));
                obj.addProperty("StationID", rs.getInt("StationID"));
                samples.add(obj);
            }
            
            JsonObject response = new JsonObject();
            response.add("data", samples);
            return gson.toJson(response);
        }
    }
    
    @Override
    public String getById(String id) throws Exception {
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement("SELECT * FROM Sample WHERE SampleID = ?")) {
            
            stmt.setInt(1, Integer.parseInt(id));
            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    JsonObject obj = new JsonObject();
                    obj.addProperty("SampleID", rs.getInt("SampleID"));
                    obj.addProperty("SampleType", rs.getString("SampleType"));
                    obj.addProperty("SamplingTime", rs.getTimestamp("SamplingTime") != null ? 
                        rs.getTimestamp("SamplingTime").toString() : null);
                    obj.addProperty("SamplingDepth", rs.getBigDecimal("SamplingDepth"));
                    obj.addProperty("LocationDescription", rs.getString("LocationDescription"));
                    obj.addProperty("StationID", rs.getInt("StationID"));
                    
                    JsonObject response = new JsonObject();
                    response.add("data", obj);
                    return gson.toJson(response);
                }
                throw new Exception("样本不存在");
            }
        }
    }
    
    @Override
    public String create(String jsonBody) throws Exception {
        JsonObject data = gson.fromJson(jsonBody, JsonObject.class);
        
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement(
                 "INSERT INTO Sample (SampleType, SamplingTime, SamplingDepth, LocationDescription, StationID) VALUES (?, ?, ?, ?, ?)",
                 Statement.RETURN_GENERATED_KEYS)) {
            
            stmt.setString(1, data.get("SampleType").getAsString());
            stmt.setString(2, data.has("SamplingTime") ? data.get("SamplingTime").getAsString() : null);
            stmt.setBigDecimal(3, data.has("SamplingDepth") ? data.get("SamplingDepth").getAsBigDecimal() : null);
            stmt.setString(4, data.has("LocationDescription") ? data.get("LocationDescription").getAsString() : null);
            stmt.setInt(5, data.get("StationID").getAsInt());
            
            stmt.executeUpdate();
            ResultSet rs = stmt.getGeneratedKeys();
            
            JsonObject response = new JsonObject();
            if (rs.next()) {
                response.addProperty("SampleID", rs.getInt(1));
            }
            response.addProperty("message", "样本创建成功");
            return gson.toJson(response);
        }
    }
    
    @Override
    public String update(String id, String jsonBody) throws Exception {
        JsonObject data = gson.fromJson(jsonBody, JsonObject.class);
        
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement(
                 "UPDATE Sample SET SampleType=?, SamplingTime=?, SamplingDepth=?, LocationDescription=?, StationID=? WHERE SampleID=?")) {
            
            stmt.setString(1, data.get("SampleType").getAsString());
            stmt.setString(2, data.has("SamplingTime") ? data.get("SamplingTime").getAsString() : null);
            stmt.setBigDecimal(3, data.has("SamplingDepth") ? data.get("SamplingDepth").getAsBigDecimal() : null);
            stmt.setString(4, data.has("LocationDescription") ? data.get("LocationDescription").getAsString() : null);
            stmt.setInt(5, data.get("StationID").getAsInt());
            stmt.setInt(6, Integer.parseInt(id));
            
            int affected = stmt.executeUpdate();
            
            JsonObject response = new JsonObject();
            response.addProperty("message", "样本更新成功");
            response.addProperty("affected", affected);
            return gson.toJson(response);
        }
    }
    
    @Override
    public String delete(String id) throws Exception {
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement("DELETE FROM Sample WHERE SampleID = ?")) {
            
            stmt.setInt(1, Integer.parseInt(id));
            int affected = stmt.executeUpdate();
            
            JsonObject response = new JsonObject();
            response.addProperty("message", "样本删除成功");
            response.addProperty("affected", affected);
            return gson.toJson(response);
        }
    }
}
