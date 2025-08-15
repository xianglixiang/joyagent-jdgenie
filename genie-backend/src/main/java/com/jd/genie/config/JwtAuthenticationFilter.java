package com.jd.genie.config;

import com.jd.genie.util.JwtUtil;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * JWT认证过滤器
 * 拦截请求并验证JWT Token，设置用户上下文
 */
@Slf4j
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    @Autowired
    private JwtUtil jwtUtil;

    @Override
    protected void doFilterInternal(HttpServletRequest request, 
                                    HttpServletResponse response, 
                                    FilterChain filterChain) throws ServletException, IOException {
        
        try {
            // 获取请求路径
            String path = request.getRequestURI();
            log.info("JWT过滤器处理请求: {}", path);
            
            // 跳过不需要认证的路径
            if (isPublicPath(path)) {
                log.info("公开路径，跳过认证: {}", path);
                filterChain.doFilter(request, response);
                return;
            }

            // 从请求头中提取Token
            String token = extractTokenFromRequest(request);
            log.info("提取到Token: {}", token != null ? "存在(长度:" + token.length() + ")" : "不存在");
            
            if (token != null) {
                boolean isValidToken = jwtUtil.validateToken(token);
                log.info("Token验证结果: {}", isValidToken);
                
                if (isValidToken) {
                    // Token有效，设置用户上下文
                    Long userId = jwtUtil.getUserIdFromToken(token);
                    String username = jwtUtil.getUsernameFromToken(token);
                    String role = jwtUtil.getRoleFromToken(token);
                    
                    log.info("从Token解析用户信息: userId={}, username={}, role={}", userId, username, role);
                    
                    if (userId != null && username != null && role != null) {
                        // 设置用户上下文信息
                        UserContext userContext = UserContext.authenticated(userId, username, role);
                        UserContextHolder.setContext(userContext);
                        
                        // 也设置到请求属性中以备其他组件使用
                        request.setAttribute("userId", userId);
                        request.setAttribute("username", username);
                        request.setAttribute("userRole", role);
                        
                        log.info("用户认证成功并设置上下文: userId={}, username={}, role={}", userId, username, role);
                    } else {
                        log.warn("Token解析失败，用户信息为空: userId={}, username={}, role={}", userId, username, role);
                    }
                } else {
                    log.warn("Token验证失败: {}", path);
                }
            } else {
                log.warn("未找到Authorization header: {}", path);
            }
            
            if ((token == null || !jwtUtil.validateToken(token)) && !isOptionalAuthPath(path)) {
                // Token无效且不是可选认证路径，返回401错误
                log.warn("请求未认证或Token无效，返回401: {}", path);
                response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                response.setContentType("application/json;charset=UTF-8");
                response.getWriter().write("{\"success\": false, \"message\": \"未授权访问，请先登录\"}");
                return;
            }
            
        } catch (Exception e) {
            log.error("JWT认证过滤器处理异常", e);
        }
        
        try {
            filterChain.doFilter(request, response);
        } finally {
            // 请求结束后清除用户上下文
            UserContextHolder.clearContext();
        }
    }

    /**
     * 从请求中提取Token
     */
    private String extractTokenFromRequest(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }

    /**
     * 判断是否为公开路径（不需要认证）
     */
    private boolean isPublicPath(String path) {
        String[] publicPaths = {
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/validate",
            "/api/auth/test",
            "/api/test",
            "/api/health",
            "/api/system/info",
            "/api/llm",
            "/error",
            "/favicon.ico"
        };
        
        for (String publicPath : publicPaths) {
            if (path.startsWith(publicPath)) {
                return true;
            }
        }
        
        // 静态资源路径
        if (path.startsWith("/static/") || 
            path.startsWith("/css/") || 
            path.startsWith("/js/") || 
            path.startsWith("/images/") ||
            path.endsWith(".html") ||
            path.endsWith(".css") ||
            path.endsWith(".js") ||
            path.endsWith(".png") ||
            path.endsWith(".jpg") ||
            path.endsWith(".ico")) {
            return true;
        }
        
        return false;
    }

    /**
     * 判断是否为可选认证路径（可以不登录访问，但登录后提供更多功能）
     */
    private boolean isOptionalAuthPath(String path) {
        String[] optionalAuthPaths = {
            "/api/knowledge/tools/validate-config",
            "/api/system/status"
        };
        
        for (String optionalPath : optionalAuthPaths) {
            if (path.startsWith(optionalPath)) {
                return true;
            }
        }
        
        return false;
    }
}