package com.ocean.database.handler;

import com.ocean.database.service.*;
import io.netty.buffer.Unpooled;
import io.netty.channel.ChannelFutureListener;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.SimpleChannelInboundHandler;
import io.netty.handler.codec.http.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.charset.StandardCharsets;

/**
 * API路由处理器
 * 根据请求路径分发到对应的Service
 */
public class ApiRouter extends SimpleChannelInboundHandler<FullHttpRequest> {
    private static final Logger logger = LoggerFactory.getLogger(ApiRouter.class);
    
    private final UserService userService = new UserService();
    private final SampleService sampleService = new SampleService();
    private final MeasurementService measurementService = new MeasurementService();
    private final LocationService locationService = new LocationService();
    private final NuclideService nuclideService = new NuclideService();
    private final StatsService statsService = new StatsService();
    private final DataManagementService dataManagementService = new DataManagementService();
    private final ApprovalService approvalService = new ApprovalService();
    
    @Override
    protected void channelRead0(ChannelHandlerContext ctx, FullHttpRequest request) {
        String uri = request.uri();
        HttpMethod method = request.method();
        
        logger.info("收到请求: {} {}", method, uri);
        
        try {
            String response = routeRequest(uri, method, request);
            sendResponse(ctx, request, HttpResponseStatus.OK, response);
        } catch (Exception e) {
            logger.error("处理请求失败: {} {}", method, uri, e);
            String errorJson = String.format("{\"error\": \"%s\"}", e.getMessage());
            sendResponse(ctx, request, HttpResponseStatus.INTERNAL_SERVER_ERROR, errorJson);
        }
    }
    
    /**
     * 路由请求到对应的Service
     */
    private String routeRequest(String uri, HttpMethod method, FullHttpRequest request) throws Exception {
        String body = request.content().toString(StandardCharsets.UTF_8);
        
        // 统计API
        if (uri.equals("/api/stats") && method == HttpMethod.GET) {
            return statsService.getStats();
        }
        if (uri.equals("/api/stats/radioactivity-trend") && method == HttpMethod.GET) {
            return statsService.getRadioactivityTrend();
        }
        if (uri.equals("/api/stats/bio-radioactivity") && method == HttpMethod.GET) {
            return statsService.getBioRadioactivity();
        }
        if (uri.equals("/api/stats/nuclide-distribution") && method == HttpMethod.GET) {
            return statsService.getNuclideDistribution();
        }
        if (uri.equals("/api/stats/recent-events") && method == HttpMethod.GET) {
            return statsService.getRecentEvents();
        }
        if (uri.equals("/api/stats/geographic-distribution") && method == HttpMethod.GET) {
            return statsService.getGeographicDistribution();
        }
        
        // 用户API
        if (uri.startsWith("/api/users")) {
            return handleCrud(uri, method, body, userService, "/api/users");
        }
        
        // 样本API
        if (uri.startsWith("/api/samples")) {
            return handleCrud(uri, method, body, sampleService, "/api/samples");
        }
        
        // 测量记录API
        if (uri.startsWith("/api/measurements")) {
            return handleCrud(uri, method, body, measurementService, "/api/measurements");
        }
        
        // 地点API
        if (uri.startsWith("/api/locations")) {
            return handleCrud(uri, method, body, locationService, "/api/locations");
        }
        
        // 核素API
        if (uri.startsWith("/api/nuclides")) {
            return handleCrud(uri, method, body, nuclideService, "/api/nuclides");
        }
        
        // 数据管理API
        if (uri.startsWith("/api/data-management")) {
            return handleDataManagement(uri, method, body);
        }
        
        // 审批API
        if (uri.startsWith("/api/approval")) {
            return handleApproval(uri, method, body);
        }
        
        // 404
        throw new Exception("API路径不存在: " + uri);
    }
    
    /**
     * 通用CRUD处理
     */
    private String handleCrud(String uri, HttpMethod method, String body, 
                             BaseService service, String basePath) throws Exception {
        // GET /api/xxx - 获取所有
        if (uri.equals(basePath) && method == HttpMethod.GET) {
            return service.getAll();
        }
        
        // GET /api/xxx/:id - 获取单个
        if (uri.startsWith(basePath + "/") && method == HttpMethod.GET) {
            String id = uri.substring(basePath.length() + 1);
            return service.getById(id);
        }
        
        // POST /api/xxx - 创建
        if (uri.equals(basePath) && method == HttpMethod.POST) {
            return service.create(body);
        }
        
        // PUT /api/xxx/:id - 更新
        if (uri.startsWith(basePath + "/") && method == HttpMethod.PUT) {
            String id = uri.substring(basePath.length() + 1);
            return service.update(id, body);
        }
        
        // DELETE /api/xxx/:id - 删除
        if (uri.startsWith(basePath + "/") && method == HttpMethod.DELETE) {
            String id = uri.substring(basePath.length() + 1);
            return service.delete(id);
        }
        
        throw new Exception("不支持的请求方法: " + method);
    }
    
    /**
     * 处理数据管理API
     */
    private String handleDataManagement(String uri, HttpMethod method, String body) throws Exception {
        // GET /api/data-management/tables - 获取所有表列表
        if (uri.equals("/api/data-management/tables") && method == HttpMethod.GET) {
            return dataManagementService.getAllTables();
        }
        
        // GET /api/data-management/table/:tableName - 获取指定表的数据
        if (uri.startsWith("/api/data-management/table/") && method == HttpMethod.GET) {
            String tableName = uri.substring("/api/data-management/table/".length());
            return dataManagementService.getTableData(tableName);
        }
        
        // GET /api/data-management/schema/:tableName - 获取表结构
        if (uri.startsWith("/api/data-management/schema/") && method == HttpMethod.GET) {
            String tableName = uri.substring("/api/data-management/schema/".length());
            return dataManagementService.getTableSchema(tableName);
        }
        
        // POST /api/data-management/execute - 执行批量操作
        if (uri.equals("/api/data-management/execute") && method == HttpMethod.POST) {
            return dataManagementService.executeBatchOperations(body);
        }
        
        throw new Exception("不支持的数据管理API: " + uri);
    }
    
    /**
     * 处理审批API
     */
    private String handleApproval(String uri, HttpMethod method, String body) throws Exception {
        // POST /api/approval/submit - 提交审批请求
        if (uri.equals("/api/approval/submit") && method == HttpMethod.POST) {
            return approvalService.submitApprovalRequest(body);
        }
        
        // GET /api/approval/pending - 获取待审批列表
        if (uri.equals("/api/approval/pending") && method == HttpMethod.GET) {
            return approvalService.getPendingApprovals();
        }
        
        // POST /api/approval/:id/approve - 批准审批
        if (uri.matches("/api/approval/\\d+/approve") && method == HttpMethod.POST) {
            String[] parts = uri.split("/");
            String requestId = parts[3];
            // 从请求体中解析审批人信息
            com.google.gson.Gson gson = new com.google.gson.Gson();
            java.lang.reflect.Type type = new com.google.gson.reflect.TypeToken<java.util.Map<String, Object>>(){}.getType();
            java.util.Map<String, Object> data = gson.fromJson(body, type);
            String approverName = (String) data.get("approverName");
            int approverId = ((Number) data.get("approverId")).intValue();
            return approvalService.approveRequest(requestId, approverName, approverId);
        }
        
        // POST /api/approval/:id/reject - 拒绝审批
        if (uri.matches("/api/approval/\\d+/reject") && method == HttpMethod.POST) {
            String[] parts = uri.split("/");
            String requestId = parts[3];
            // 从请求体中解析审批人信息和拒绝原因
            com.google.gson.Gson gson = new com.google.gson.Gson();
            java.lang.reflect.Type type = new com.google.gson.reflect.TypeToken<java.util.Map<String, Object>>(){}.getType();
            java.util.Map<String, Object> data = gson.fromJson(body, type);
            String approverName = (String) data.get("approverName");
            int approverId = ((Number) data.get("approverId")).intValue();
            String comment = (String) data.get("comment");
            return approvalService.rejectRequest(requestId, approverName, approverId, comment);
        }
        
        throw new Exception("不支持的审批API: " + uri);
    }
    
    /**
     * 发送HTTP响应
     */
    private void sendResponse(ChannelHandlerContext ctx, FullHttpRequest request, 
                             HttpResponseStatus status, String content) {
        FullHttpResponse response = new DefaultFullHttpResponse(
            HttpVersion.HTTP_1_1,
            status,
            Unpooled.copiedBuffer(content, StandardCharsets.UTF_8)
        );
        
        CorsHandler.addCorsHeaders(response, request);
        response.headers().set(HttpHeaderNames.CONTENT_LENGTH, response.content().readableBytes());
        
        boolean keepAlive = HttpUtil.isKeepAlive(request);
        if (keepAlive) {
            response.headers().set(HttpHeaderNames.CONNECTION, HttpHeaderValues.KEEP_ALIVE);
            ctx.writeAndFlush(response);
        } else {
            ctx.writeAndFlush(response).addListener(ChannelFutureListener.CLOSE);
        }
    }
    
    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
        logger.error("处理请求异常", cause);
        ctx.close();
    }
}
