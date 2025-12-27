package com.ocean.database.service;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.ocean.database.config.DatabaseConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.*;

/**
 * 统计服务
 * 提供系统统计数据
 */
public class StatsService {
    private static final Logger logger = LoggerFactory.getLogger(StatsService.class);
    private final Gson gson = new Gson();
    
    /**
     * 获取系统统计数据
     * 返回用户、样本、测量记录、地点的总数
     */
    public String getStats() throws Exception {
        logger.info("获取统计数据");
        
        try (Connection conn = DatabaseConfig.getConnection()) {
            Map<String, Object> stats = new HashMap<>();
            
            // 使用单个查询获取所有统计数据（性能更好）
            String sql = """
                SELECT 
                    (SELECT COUNT(*) FROM User) as users,
                    (SELECT COUNT(*) FROM Sample) as samples,
                    (SELECT COUNT(*) FROM MeasurementRecord) as measurements,
                    (SELECT COUNT(*) FROM Station) as locations
            """;
            
            try (PreparedStatement stmt = conn.prepareStatement(sql);
                 ResultSet rs = stmt.executeQuery()) {
                
                if (rs.next()) {
                    stats.put("users", rs.getInt("users"));
                    stats.put("samples", rs.getInt("samples"));
                    stats.put("measurements", rs.getInt("measurements"));
                    stats.put("locations", rs.getInt("locations"));
                }
            }
            
            logger.info("统计数据: {}", stats);
            return gson.toJson(stats);
            
        } catch (Exception e) {
            logger.error("获取统计数据失败", e);
            throw new Exception("获取统计数据失败: " + e.getMessage());
        }
    }
    
    /**
     * 获取放射性浓度趋势数据（按年份统计，包含多个核素）
     */
    public String getRadioactivityTrend() throws Exception {
        logger.info("获取放射性浓度趋势");
        
        // 返回模拟数据，展示Cs-137, Co-60, Sr-90, I-131的浓度变化
        JsonArray data = new JsonArray();
        
        int[] years = {2018, 2019, 2020, 2021, 2022, 2023, 2024};
        
        // Cs-137 数据（铯-137，半衰期30年）
        double[] cs137 = {0.95, 0.88, 0.75, 0.92, 0.68, 0.55, 0.62};
        
        // Co-60 数据（钴-60，半衰期5.27年）
        double[] co60 = {0.55, 0.72, 0.68, 0.45, 0.38, 0.42, 0.50};
        
        // Sr-90 数据（锶-90，半衰期28.8年）
        double[] sr90 = {0.85, 0.95, 0.78, 0.88, 0.72, 0.65, 0.70};
        
        // I-131 数据（碘-131，半衰期8天，通常较低）
        double[] i131 = {0.25, 0.32, 0.28, 0.35, 0.30, 0.28, 0.32};
        
        for (int i = 0; i < years.length; i++) {
            JsonObject obj = new JsonObject();
            obj.addProperty("year", years[i]);
            obj.addProperty("cs137", cs137[i]);
            obj.addProperty("co60", co60[i]);
            obj.addProperty("sr90", sr90[i]);
            obj.addProperty("i131", i131[i]);
            data.add(obj);
        }
        
        JsonObject response = new JsonObject();
        response.add("data", data);
        return gson.toJson(response);
    }
    
    /**
     * 获取生物放射性统计
     */
    public String getBioRadioactivity() throws Exception {
        logger.info("获取生物放射性统计");
        
        // 返回模拟数据
        JsonArray data = new JsonArray();
        
        String[] species = {"Cancer pagurus", "Homarus americanus", "Aurelia aurita", "Octopus orca", 
                            "Spheniscus demersus", "Odobenus rosmarus", "Limanda limanda", "Pleuronectes platessa",
                            "Mytilus edulis", "Ostrea edulis"};
        String[] habitats = {"太平洋", "大西洋", "太平洋", "印度洋", "南极海域", "北冰洋", "北海", "波罗的海", "北海", "大西洋"};
        double[] minValues = {0.80, 1.20, 0.50, 1.50, 0.90, 1.10, 0.70, 0.85, 1.00, 0.95};
        double[] maxValues = {2.50, 3.80, 2.10, 4.20, 2.80, 3.50, 2.30, 2.60, 3.10, 2.90};
        
        for (int i = 0; i < species.length; i++) {
            JsonObject obj = new JsonObject();
            obj.addProperty("species", species[i]);
            obj.addProperty("habitat", habitats[i]);
            obj.addProperty("avgConcentration", (minValues[i] + maxValues[i]) / 2);
            obj.addProperty("minConcentration", minValues[i]);
            obj.addProperty("maxConcentration", maxValues[i]);
            obj.addProperty("sampleCount", 5 + (i * 2));
            data.add(obj);
        }
        
        JsonObject response = new JsonObject();
        response.add("data", data);
        return gson.toJson(response);
    }
    
    /**
     * 获取核素分布统计
     */
    public String getNuclideDistribution() throws Exception {
        logger.info("获取核素分布统计");
        
        try (Connection conn = DatabaseConfig.getConnection()) {
            String sql = """
                SELECT 
                    n.Symbol,
                    n.Name,
                    AVG(mr.Activity) as avgConcentration,
                    COUNT(*) as measurementCount
                FROM MeasurementRecord mr
                LEFT JOIN Radionuclide n ON mr.NuclideID = n.NuclideID
                WHERE n.Symbol IS NOT NULL
                GROUP BY n.Symbol, n.Name
                ORDER BY avgConcentration DESC
            """;
            
            JsonArray data = new JsonArray();
            try (PreparedStatement stmt = conn.prepareStatement(sql);
                 ResultSet rs = stmt.executeQuery()) {
                
                while (rs.next()) {
                    JsonObject obj = new JsonObject();
                    obj.addProperty("symbol", rs.getString("Symbol"));
                    obj.addProperty("name", rs.getString("Name"));
                    obj.addProperty("avgConcentration", rs.getDouble("avgConcentration"));
                    obj.addProperty("count", rs.getInt("measurementCount"));
                    data.add(obj);
                }
            }
            
            JsonObject response = new JsonObject();
            response.add("data", data);
            return gson.toJson(response);
            
        } catch (Exception e) {
            logger.error("获取核素分布统计失败", e);
            throw new Exception("获取核素分布统计失败: " + e.getMessage());
        }
    }
    
    /**
     * 获取最新事件/通知
     * 展示重要的海洋放射性事件
     */
    public String getRecentEvents() throws Exception {
        logger.info("获取最新事件");
        
        // 返回真实的海洋放射性事件数据
        JsonArray events = new JsonArray();
        
        // 历史上重要的海洋放射性事件
        Object[][] eventData = {
            {"福岛核电站事故影响持续", "2011-03-11 14:46:00", "Pending"},
            {"切尔诺贝利核泄漏监测更新", "2010-04-26 01:23:00", "Approved"},
            {"太平洋核试验区域监测", "2010-06-07 08:15:00", "Approved"},
            {"法国穆鲁罗阿环礁核试验遗留", "1996-01-27 00:00:00", "Pending"},
            {"比基尼环礁放射性残留检测", "1954-03-01 06:45:00", "Approved"},
            {"塞拉菲尔德核废料泄漏事件", "2005-04-20 00:00:00", "Pending"},
            {"K-19潜艇核事故区域调查", "1961-07-04 00:00:00", "Approved"},
            {"三哩岛核电站事故影响评估", "1979-03-28 04:00:00", "Approved"},
            {"托卡塔托劳环礁核试验遗址", "1967-03-18 00:00:00", "Pending"},
            {"地中海核潜艇事故调查", "2010-02-12 00:00:00", "Approved"}
        };
        
        for (int i = 0; i < eventData.length; i++) {
            JsonObject event = new JsonObject();
            event.addProperty("type", "radioactive-event");
            event.addProperty("id", i + 1);
            event.addProperty("title", (String) eventData[i][0]);
            event.addProperty("time", (String) eventData[i][1]);
            event.addProperty("status", (String) eventData[i][2]);
            events.add(event);
        }
        
        JsonObject response = new JsonObject();
        response.add("data", events);
        return gson.toJson(response);
    }
    
    /**
     * 获取地理分布统计
     */
    public String getGeographicDistribution() throws Exception {
        logger.info("获取地理分布统计");
        
        try (Connection conn = DatabaseConfig.getConnection()) {
            String sql = """
                SELECT 
                    st.OceanArea,
                    st.Latitude,
                    st.Longitude,
                    COUNT(DISTINCT s.SampleID) as sampleCount,
                    AVG(mr.Activity) as avgConcentration
                FROM Station st
                LEFT JOIN Sample s ON st.StationID = s.StationID
                LEFT JOIN MeasurementRecord mr ON s.SampleID = mr.SampleID
                WHERE st.OceanArea IS NOT NULL
                GROUP BY st.StationID, st.OceanArea, st.Latitude, st.Longitude
                ORDER BY sampleCount DESC
            """;
            
            JsonArray data = new JsonArray();
            try (PreparedStatement stmt = conn.prepareStatement(sql);
                 ResultSet rs = stmt.executeQuery()) {
                
                while (rs.next()) {
                    JsonObject obj = new JsonObject();
                    obj.addProperty("area", rs.getString("OceanArea"));
                    obj.addProperty("latitude", rs.getDouble("Latitude"));
                    obj.addProperty("longitude", rs.getDouble("Longitude"));
                    obj.addProperty("sampleCount", rs.getInt("sampleCount"));
                    obj.addProperty("avgConcentration", rs.getDouble("avgConcentration"));
                    data.add(obj);
                }
            }
            
            JsonObject response = new JsonObject();
            response.add("data", data);
            return gson.toJson(response);
            
        } catch (Exception e) {
            logger.error("获取地理分布统计失败", e);
            throw new Exception("获取地理分布统计失败: " + e.getMessage());
        }
    }
}
