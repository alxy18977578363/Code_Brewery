package com.ocean.database.handler;

import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.SimpleChannelInboundHandler;
import io.netty.handler.codec.http.*;
import io.netty.buffer.Unpooled;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.charset.StandardCharsets;

/**
 * CORS跨域处理器
 */
public class CorsHandler extends SimpleChannelInboundHandler<FullHttpRequest> {
    private static final Logger logger = LoggerFactory.getLogger(CorsHandler.class);
    
    @Override
    protected void channelRead0(ChannelHandlerContext ctx, FullHttpRequest request) {
        // OPTIONS预检请求直接返回
        if (request.method() == HttpMethod.OPTIONS) {
            FullHttpResponse response = new DefaultFullHttpResponse(
                HttpVersion.HTTP_1_1,
                HttpResponseStatus.OK,
                Unpooled.EMPTY_BUFFER
            );
            
            addCorsHeaders(response, request);
            ctx.writeAndFlush(response);
            return;
        }
        
        // 其他请求继续传递
        ctx.fireChannelRead(request.retain());
    }
    
    /**
     * 添加CORS响应头
     */
    public static void addCorsHeaders(FullHttpResponse response, FullHttpRequest request) {
        HttpHeaders headers = response.headers();
        headers.set(HttpHeaderNames.ACCESS_CONTROL_ALLOW_ORIGIN, "*");
        headers.set(HttpHeaderNames.ACCESS_CONTROL_ALLOW_METHODS, "GET, POST, PUT, DELETE, OPTIONS");
        headers.set(HttpHeaderNames.ACCESS_CONTROL_ALLOW_HEADERS, "Content-Type, Authorization");
        headers.set(HttpHeaderNames.ACCESS_CONTROL_MAX_AGE, "3600");
        headers.set(HttpHeaderNames.CONTENT_TYPE, "application/json; charset=UTF-8");
    }
}
