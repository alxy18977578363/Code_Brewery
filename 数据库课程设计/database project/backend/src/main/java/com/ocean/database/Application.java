package com.ocean.database;

import com.ocean.database.server.HttpServer;
import com.ocean.database.config.DatabaseConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 应用程序主入口
 * 海洋数据库管理系统后端服务
 */
public class Application {
    private static final Logger logger = LoggerFactory.getLogger(Application.class);
    
    public static void main(String[] args) {
        try {
            logger.info("========================================");
            logger.info("启动海洋数据库管理系统后端服务...");
            logger.info("========================================");
            
            // 初始化数据库配置
            DatabaseConfig.initialize();
            logger.info("数据库连接池初始化成功");
            
            // 启动HTTP服务器
            int port = 3000;
            HttpServer server = new HttpServer(port);
            server.start();
            
            logger.info("========================================");
            logger.info("服务器启动成功! 监听端口: {}", port);
            logger.info("API地址: http://localhost:{}/api", port);
            logger.info("========================================");
            
            // 添加关闭钩子
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                logger.info("正在关闭服务器...");
                server.stop();
                DatabaseConfig.close();
                logger.info("服务器已关闭");
            }));
            
            // 保持主线程运行
            Thread.currentThread().join();
            
        } catch (Exception e) {
            logger.error("启动失败: {}", e.getMessage(), e);
            System.exit(1);
        }
    }
}
