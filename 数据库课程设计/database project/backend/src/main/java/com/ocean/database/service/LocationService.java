package com.ocean.database.service;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.ocean.database.config.DatabaseConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.*;

/**
 * 地点服务
 */
public class LocationService extends BaseService {
    private static final Logger logger = LoggerFactory.getLogger(LocationService.class);
    private final Gson gson = new Gson();
    
    @Override
    public String getAll() throws Exception {
        try (Connection conn = DatabaseConfig.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT * FROM Station")) {
            
            JsonArray locations = new JsonArray();
            while (rs.next()) {
                JsonObject obj = new JsonObject();
                obj.addProperty("LocationID", rs.getInt("LocationID"));
                obj.addProperty("LocationName", rs.getString("LocationName"));
                obj.addProperty("Latitude", rs.getDouble("Latitude"));
                obj.addProperty("Longitude", rs.getDouble("Longitude"));
                obj.addProperty("Depth", rs.getDouble("Depth"));
                obj.addProperty("WaterBody", rs.getString("WaterBody"));
                obj.addProperty("Region", rs.getString("Region"));
                obj.addProperty("Country", rs.getString("Country"));
                locations.add(obj);
            }
            
            JsonObject response = new JsonObject();
            response.add("data", locations);
            return gson.toJson(response);
        }
    }
    
    @Override
    public String getById(String id) throws Exception {
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement("SELECT * FROM Station WHERE LocationID = ?")) {
            
            stmt.setInt(1, Integer.parseInt(id));
            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    JsonObject obj = new JsonObject();
                    obj.addProperty("LocationID", rs.getInt("LocationID"));
                    obj.addProperty("LocationName", rs.getString("LocationName"));
                    obj.addProperty("Latitude", rs.getDouble("Latitude"));
                    obj.addProperty("Longitude", rs.getDouble("Longitude"));
                    obj.addProperty("Depth", rs.getDouble("Depth"));
                    obj.addProperty("WaterBody", rs.getString("WaterBody"));
                    obj.addProperty("Region", rs.getString("Region"));
                    obj.addProperty("Country", rs.getString("Country"));
                    
                    JsonObject response = new JsonObject();
                    response.add("data", obj);
                    return gson.toJson(response);
                }
                throw new Exception("地点不存在");
            }
        }
    }
    
    @Override
    public String create(String jsonBody) throws Exception {
        JsonObject data = gson.fromJson(jsonBody, JsonObject.class);
        
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement(
                 "INSERT INTO Station (LocationName, Latitude, Longitude, Depth, WaterBody, Region, Country) VALUES (?, ?, ?, ?, ?, ?, ?)",
                 Statement.RETURN_GENERATED_KEYS)) {
            
            stmt.setString(1, data.get("LocationName").getAsString());
            stmt.setDouble(2, data.get("Latitude").getAsDouble());
            stmt.setDouble(3, data.get("Longitude").getAsDouble());
            stmt.setDouble(4, data.has("Depth") ? data.get("Depth").getAsDouble() : 0.0);
            stmt.setString(5, data.has("WaterBody") ? data.get("WaterBody").getAsString() : null);
            stmt.setString(6, data.has("Region") ? data.get("Region").getAsString() : null);
            stmt.setString(7, data.has("Country") ? data.get("Country").getAsString() : null);
            
            stmt.executeUpdate();
            ResultSet rs = stmt.getGeneratedKeys();
            
            JsonObject response = new JsonObject();
            if (rs.next()) {
                response.addProperty("LocationID", rs.getInt(1));
            }
            response.addProperty("message", "地点创建成功");
            return gson.toJson(response);
        }
    }
    
    @Override
    public String update(String id, String jsonBody) throws Exception {
        JsonObject data = gson.fromJson(jsonBody, JsonObject.class);
        
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement(
                 "UPDATE Station SET LocationName=?, Latitude=?, Longitude=?, Depth=?, WaterBody=?, Region=?, Country=? WHERE LocationID=?")) {
            
            stmt.setString(1, data.get("LocationName").getAsString());
            stmt.setDouble(2, data.get("Latitude").getAsDouble());
            stmt.setDouble(3, data.get("Longitude").getAsDouble());
            stmt.setDouble(4, data.has("Depth") ? data.get("Depth").getAsDouble() : 0.0);
            stmt.setString(5, data.has("WaterBody") ? data.get("WaterBody").getAsString() : null);
            stmt.setString(6, data.has("Region") ? data.get("Region").getAsString() : null);
            stmt.setString(7, data.has("Country") ? data.get("Country").getAsString() : null);
            stmt.setInt(8, Integer.parseInt(id));
            
            int affected = stmt.executeUpdate();
            
            JsonObject response = new JsonObject();
            response.addProperty("message", "地点更新成功");
            response.addProperty("affected", affected);
            return gson.toJson(response);
        }
    }
    
    @Override
    public String delete(String id) throws Exception {
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement("DELETE FROM Station WHERE LocationID = ?")) {
            
            stmt.setInt(1, Integer.parseInt(id));
            int affected = stmt.executeUpdate();
            
            JsonObject response = new JsonObject();
            response.addProperty("message", "地点删除成功");
            response.addProperty("affected", affected);
            return gson.toJson(response);
        }
    }
}
