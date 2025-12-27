package com.ocean.database.config;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.Properties;

/**
 * 数据库配置和连接池管理
 */
public class DatabaseConfig {
    private static final Logger logger = LoggerFactory.getLogger(DatabaseConfig.class);
    private static HikariDataSource dataSource;
    
    // 默认配置
    private static String DB_URL = "jdbc:mysql://localhost:3306/ocean_database?useSSL=false&serverTimezone=UTC&allowPublicKeyRetrieval=true";
    private static String DB_USER = "root";
    private static String DB_PASSWORD = "root";
    
    /**
     * 初始化数据库连接池
     */
    public static void initialize() {
        // 尝试从配置文件加载
        loadConfig();
        
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(DB_URL);
        config.setUsername(DB_USER);
        config.setPassword(DB_PASSWORD);
        
        // 连接池配置
        config.setMaximumPoolSize(10);
        config.setMinimumIdle(2);
        config.setConnectionTimeout(30000);
        config.setIdleTimeout(600000);
        config.setMaxLifetime(1800000);
        
        // 性能优化
        config.addDataSourceProperty("cachePrepStmts", "true");
        config.addDataSourceProperty("prepStmtCacheSize", "250");
        config.addDataSourceProperty("prepStmtCacheSqlLimit", "2048");
        
        dataSource = new HikariDataSource(config);
        logger.info("数据库连接池创建成功: {}", DB_URL);
    }
    
    /**
     * 从配置文件加载数据库配置
     */
    private static void loadConfig() {
        Properties props = new Properties();
        try (InputStream input = new FileInputStream("config/database.properties")) {
            props.load(input);
            DB_URL = props.getProperty("db.url", DB_URL);
            DB_USER = props.getProperty("db.user", DB_USER);
            DB_PASSWORD = props.getProperty("db.password", DB_PASSWORD);
            logger.info("已从配置文件加载数据库配置");
        } catch (IOException e) {
            logger.warn("未找到配置文件,使用默认配置: {}", e.getMessage());
        }
    }
    
    /**
     * 获取数据库连接
     */
    public static Connection getConnection() throws SQLException {
        if (dataSource == null) {
            throw new SQLException("数据库连接池未初始化");
        }
        return dataSource.getConnection();
    }
    
    /**
     * 关闭连接池
     */
    public static void close() {
        if (dataSource != null && !dataSource.isClosed()) {
            dataSource.close();
            logger.info("数据库连接池已关闭");
        }
    }
}
