package com.ocean.database.service;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.ocean.database.config.DatabaseConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.*;

/**
 * 测量记录服务
 */
public class MeasurementService extends BaseService {
    private static final Logger logger = LoggerFactory.getLogger(MeasurementService.class);
    private final Gson gson = new Gson();
    
    @Override
    public String getAll() throws Exception {
        try (Connection conn = DatabaseConfig.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT * FROM MeasurementRecord")) {
            
            JsonArray measurements = new JsonArray();
            while (rs.next()) {
                JsonObject obj = new JsonObject();
                obj.addProperty("RecordID", rs.getInt("RecordID"));
                obj.addProperty("Activity", rs.getBigDecimal("Activity"));
                obj.addProperty("Uncertainty", rs.getBigDecimal("Uncertainty"));
                obj.addProperty("Unit", rs.getString("Unit"));
                obj.addProperty("MeasurementType", rs.getString("MeasurementType"));
                obj.addProperty("TestingOrganization", rs.getString("TestingOrganization"));
                obj.addProperty("ReportNumber", rs.getString("ReportNumber"));
                obj.addProperty("CompletionTime", rs.getTimestamp("CompletionTime") != null ? 
                    rs.getTimestamp("CompletionTime").toString() : null);
                obj.addProperty("SampleID", rs.getInt("SampleID"));
                obj.addProperty("NuclideID", rs.getInt("NuclideID"));
                measurements.add(obj);
            }
            
            JsonObject response = new JsonObject();
            response.add("data", measurements);
            return gson.toJson(response);
        }
    }
    
    @Override
    public String getById(String id) throws Exception {
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement("SELECT * FROM MeasurementRecord WHERE RecordID = ?")) {
            
            stmt.setInt(1, Integer.parseInt(id));
            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    JsonObject obj = new JsonObject();
                    obj.addProperty("RecordID", rs.getInt("RecordID"));
                    obj.addProperty("Activity", rs.getBigDecimal("Activity"));
                    obj.addProperty("Uncertainty", rs.getBigDecimal("Uncertainty"));
                    obj.addProperty("Unit", rs.getString("Unit"));
                    obj.addProperty("MeasurementType", rs.getString("MeasurementType"));
                    obj.addProperty("TestingOrganization", rs.getString("TestingOrganization"));
                    obj.addProperty("ReportNumber", rs.getString("ReportNumber"));
                    obj.addProperty("CompletionTime", rs.getTimestamp("CompletionTime") != null ? 
                        rs.getTimestamp("CompletionTime").toString() : null);
                    obj.addProperty("SampleID", rs.getInt("SampleID"));
                    obj.addProperty("NuclideID", rs.getInt("NuclideID"));
                    
                    JsonObject response = new JsonObject();
                    response.add("data", obj);
                    return gson.toJson(response);
                }
                throw new Exception("测量记录不存在");
            }
        }
    }
    
    @Override
    public String create(String jsonBody) throws Exception {
        JsonObject data = gson.fromJson(jsonBody, JsonObject.class);
        
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement(
                 "INSERT INTO MeasurementRecord (Activity, Uncertainty, Unit, MeasurementType, TestingOrganization, ReportNumber, CompletionTime, SampleID, NuclideID) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 Statement.RETURN_GENERATED_KEYS)) {
            
            stmt.setBigDecimal(1, data.get("Activity").getAsBigDecimal());
            stmt.setBigDecimal(2, data.has("Uncertainty") ? data.get("Uncertainty").getAsBigDecimal() : null);
            stmt.setString(3, data.has("Unit") ? data.get("Unit").getAsString() : "Bq/kg");
            stmt.setString(4, data.has("MeasurementType") ? data.get("MeasurementType").getAsString() : null);
            stmt.setString(5, data.has("TestingOrganization") ? data.get("TestingOrganization").getAsString() : null);
            stmt.setString(6, data.has("ReportNumber") ? data.get("ReportNumber").getAsString() : null);
            stmt.setString(7, data.has("CompletionTime") ? data.get("CompletionTime").getAsString() : null);
            stmt.setInt(8, data.get("SampleID").getAsInt());
            stmt.setInt(9, data.get("NuclideID").getAsInt());
            
            stmt.executeUpdate();
            ResultSet rs = stmt.getGeneratedKeys();
            
            JsonObject response = new JsonObject();
            if (rs.next()) {
                response.addProperty("RecordID", rs.getInt(1));
            }
            response.addProperty("message", "测量记录创建成功");
            return gson.toJson(response);
        }
    }
    
    @Override
    public String update(String id, String jsonBody) throws Exception {
        JsonObject data = gson.fromJson(jsonBody, JsonObject.class);
        
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement(
                 "UPDATE MeasurementRecord SET Activity=?, Uncertainty=?, Unit=?, MeasurementType=?, TestingOrganization=?, ReportNumber=?, CompletionTime=? WHERE RecordID=?")) {
            
            stmt.setBigDecimal(1, data.get("Activity").getAsBigDecimal());
            stmt.setBigDecimal(2, data.has("Uncertainty") ? data.get("Uncertainty").getAsBigDecimal() : null);
            stmt.setString(3, data.has("Unit") ? data.get("Unit").getAsString() : "Bq/kg");
            stmt.setString(4, data.has("MeasurementType") ? data.get("MeasurementType").getAsString() : null);
            stmt.setString(5, data.has("TestingOrganization") ? data.get("TestingOrganization").getAsString() : null);
            stmt.setString(6, data.has("ReportNumber") ? data.get("ReportNumber").getAsString() : null);
            stmt.setString(7, data.has("CompletionTime") ? data.get("CompletionTime").getAsString() : null);
            stmt.setInt(8, Integer.parseInt(id));
            
            int affected = stmt.executeUpdate();
            
            JsonObject response = new JsonObject();
            response.addProperty("message", "测量记录更新成功");
            response.addProperty("affected", affected);
            return gson.toJson(response);
        }
    }
    
    @Override
    public String delete(String id) throws Exception {
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement("DELETE FROM MeasurementRecord WHERE RecordID = ?")) {
            
            stmt.setInt(1, Integer.parseInt(id));
            int affected = stmt.executeUpdate();
            
            JsonObject response = new JsonObject();
            response.addProperty("message", "测量记录删除成功");
            response.addProperty("affected", affected);
            return gson.toJson(response);
        }
    }
}
