package com.ocean.database.service;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.ocean.database.config.DatabaseConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.*;

/**
 * 核素服务
 */
public class NuclideService extends BaseService {
    private static final Logger logger = LoggerFactory.getLogger(NuclideService.class);
    private final Gson gson = new Gson();
    
    @Override
    public String getAll() throws Exception {
        try (Connection conn = DatabaseConfig.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT * FROM Radionuclide")) {
            
            JsonArray nuclides = new JsonArray();
            while (rs.next()) {
                JsonObject obj = new JsonObject();
                obj.addProperty("NuclideID", rs.getInt("NuclideID"));
                obj.addProperty("Name", rs.getString("Name"));
                obj.addProperty("Symbol", rs.getString("Symbol"));
                obj.addProperty("HalfLife", rs.getString("HalfLife"));
                obj.addProperty("RadioactiveType", rs.getString("RadioactiveType"));
                nuclides.add(obj);
            }
            
            JsonObject response = new JsonObject();
            response.add("data", nuclides);
            return gson.toJson(response);
        }
    }
    
    @Override
    public String getById(String id) throws Exception {
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement("SELECT * FROM Radionuclide WHERE NuclideID = ?")) {
            
            stmt.setInt(1, Integer.parseInt(id));
            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    JsonObject obj = new JsonObject();
                    obj.addProperty("NuclideID", rs.getInt("NuclideID"));
                    obj.addProperty("Name", rs.getString("Name"));
                    obj.addProperty("Symbol", rs.getString("Symbol"));
                    obj.addProperty("HalfLife", rs.getString("HalfLife"));
                    obj.addProperty("RadioactiveType", rs.getString("RadioactiveType"));
                    
                    JsonObject response = new JsonObject();
                    response.add("data", obj);
                    return gson.toJson(response);
                }
                throw new Exception("核素不存在");
            }
        }
    }
    
    @Override
    public String create(String jsonBody) throws Exception {
        JsonObject data = gson.fromJson(jsonBody, JsonObject.class);
        
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement(
                 "INSERT INTO Radionuclide (Name, Symbol, HalfLife, RadioactiveType) VALUES (?, ?, ?, ?)",
                 Statement.RETURN_GENERATED_KEYS)) {
            
            stmt.setString(1, data.get("Name").getAsString());
            stmt.setString(2, data.get("Symbol").getAsString());
            stmt.setString(3, data.has("HalfLife") ? data.get("HalfLife").getAsString() : null);
            stmt.setString(4, data.has("RadioactiveType") ? data.get("RadioactiveType").getAsString() : null);
            
            stmt.executeUpdate();
            ResultSet rs = stmt.getGeneratedKeys();
            
            JsonObject response = new JsonObject();
            if (rs.next()) {
                response.addProperty("NuclideID", rs.getInt(1));
            }
            response.addProperty("message", "核素创建成功");
            return gson.toJson(response);
        }
    }
    
    @Override
    public String update(String id, String jsonBody) throws Exception {
        JsonObject data = gson.fromJson(jsonBody, JsonObject.class);
        
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement(
                 "UPDATE Radionuclide SET Name=?, Symbol=?, HalfLife=?, RadioactiveType=? WHERE NuclideID=?")) {
            
            stmt.setString(1, data.get("Name").getAsString());
            stmt.setString(2, data.get("Symbol").getAsString());
            stmt.setString(3, data.has("HalfLife") ? data.get("HalfLife").getAsString() : null);
            stmt.setString(4, data.has("RadioactiveType") ? data.get("RadioactiveType").getAsString() : null);
            stmt.setInt(5, Integer.parseInt(id));
            
            int affected = stmt.executeUpdate();
            
            JsonObject response = new JsonObject();
            response.addProperty("message", "核素更新成功");
            response.addProperty("affected", affected);
            return gson.toJson(response);
        }
    }
    
    @Override
    public String delete(String id) throws Exception {
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement stmt = conn.prepareStatement("DELETE FROM Radionuclide WHERE NuclideID = ?")) {
            
            stmt.setInt(1, Integer.parseInt(id));
            int affected = stmt.executeUpdate();
            
            JsonObject response = new JsonObject();
            response.addProperty("message", "核素删除成功");
            response.addProperty("affected", affected);
            return gson.toJson(response);
        }
    }
}
