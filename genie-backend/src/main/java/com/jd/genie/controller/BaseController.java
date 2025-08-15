package com.jd.genie.controller;

import com.jd.genie.config.UserContext;
import com.jd.genie.config.UserContextHolder;
import org.springframework.http.ResponseEntity;

import java.util.HashMap;
import java.util.Map;

/**
 * 基础控制器
 * 提供通用的认证和权限检查方法
 */
public abstract class BaseController {

    /**
     * 获取当前用户上下文
     */
    protected UserContext getCurrentUserContext() {
        return UserContextHolder.getContext();
    }

    /**
     * 获取当前用户ID
     */
    protected Long getCurrentUserId() {
        return UserContextHolder.getCurrentUserId();
    }

    /**
     * 获取当前用户名
     */
    protected String getCurrentUsername() {
        return UserContextHolder.getCurrentUsername();
    }

    /**
     * 获取当前用户角色
     */
    protected String getCurrentUserRole() {
        return UserContextHolder.getCurrentUserRole();
    }

    /**
     * 检查是否已认证
     */
    protected boolean isAuthenticated() {
        return UserContextHolder.isAuthenticated();
    }

    /**
     * 检查是否为管理员
     */
    protected boolean isAdmin() {
        return UserContextHolder.isAdmin();
    }

    /**
     * 检查是否为普通用户
     */
    protected boolean isUser() {
        return UserContextHolder.isUser();
    }

    /**
     * 要求用户已认证，否则返回401错误
     */
    protected ResponseEntity<Map<String, Object>> requireAuthentication() {
        if (!isAuthenticated()) {
            return createUnauthorizedResponse("请先登录");
        }
        return null;
    }

    /**
     * 要求用户为管理员，否则返回403错误
     */
    protected ResponseEntity<Map<String, Object>> requireAdmin() {
        ResponseEntity<Map<String, Object>> authCheck = requireAuthentication();
        if (authCheck != null) {
            return authCheck;
        }
        
        if (!isAdmin()) {
            return createForbiddenResponse("需要管理员权限");
        }
        return null;
    }

    /**
     * 要求用户拥有指定角色之一，否则返回403错误
     */
    protected ResponseEntity<Map<String, Object>> requireRole(String... roles) {
        ResponseEntity<Map<String, Object>> authCheck = requireAuthentication();
        if (authCheck != null) {
            return authCheck;
        }
        
        String currentRole = getCurrentUserRole();
        
        // 管理员默认可以访问所有资源
        if ("ADMIN".equals(currentRole)) {
            return null;
        }
        
        for (String role : roles) {
            if (role.equals(currentRole)) {
                return null;
            }
        }
        
        return createForbiddenResponse("权限不足");
    }

    /**
     * 检查是否为资源所有者或管理员
     */
    protected ResponseEntity<Map<String, Object>> requireOwnerOrAdmin(Long resourceUserId) {
        ResponseEntity<Map<String, Object>> authCheck = requireAuthentication();
        if (authCheck != null) {
            return authCheck;
        }
        
        Long currentUserId = getCurrentUserId();
        if (!isAdmin() && !currentUserId.equals(resourceUserId)) {
            return createForbiddenResponse("只能访问自己的资源");
        }
        
        return null;
    }

    /**
     * 创建成功响应
     */
    protected ResponseEntity<Map<String, Object>> createSuccessResponse(Object data) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("data", data);
        return ResponseEntity.ok(response);
    }

    /**
     * 创建成功响应（带消息）
     */
    protected ResponseEntity<Map<String, Object>> createSuccessResponse(Object data, String message) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("data", data);
        response.put("message", message);
        return ResponseEntity.ok(response);
    }

    /**
     * 创建错误响应
     */
    protected ResponseEntity<Map<String, Object>> createErrorResponse(String message) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", false);
        response.put("message", message);
        return ResponseEntity.badRequest().body(response);
    }

    /**
     * 创建401未授权响应
     */
    protected ResponseEntity<Map<String, Object>> createUnauthorizedResponse(String message) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", false);
        response.put("message", message);
        return ResponseEntity.status(401).body(response);
    }

    /**
     * 创建403禁止访问响应
     */
    protected ResponseEntity<Map<String, Object>> createForbiddenResponse(String message) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", false);
        response.put("message", message);
        return ResponseEntity.status(403).body(response);
    }

    /**
     * 创建404未找到响应
     */
    protected ResponseEntity<Map<String, Object>> createNotFoundResponse(String message) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", false);
        response.put("message", message);
        return ResponseEntity.status(404).body(response);
    }

    /**
     * 创建500服务器错误响应
     */
    protected ResponseEntity<Map<String, Object>> createServerErrorResponse(String message) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", false);
        response.put("message", message);
        return ResponseEntity.status(500).body(response);
    }
}