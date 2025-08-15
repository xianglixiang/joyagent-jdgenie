package com.jd.genie.config;

/**
 * 用户上下文持有者
 * 使用ThreadLocal存储当前请求的用户上下文信息
 */
public class UserContextHolder {
    
    private static final ThreadLocal<UserContext> contextHolder = new ThreadLocal<>();
    
    /**
     * 设置当前用户上下文
     */
    public static void setContext(UserContext userContext) {
        contextHolder.set(userContext);
    }
    
    /**
     * 获取当前用户上下文
     */
    public static UserContext getContext() {
        UserContext context = contextHolder.get();
        return context != null ? context : UserContext.unauthenticated();
    }
    
    /**
     * 清除当前用户上下文
     */
    public static void clearContext() {
        contextHolder.remove();
    }
    
    /**
     * 获取当前用户ID
     */
    public static Long getCurrentUserId() {
        UserContext context = getContext();
        return context.isAuthenticated() ? context.getUserId() : null;
    }
    
    /**
     * 获取当前用户名
     */
    public static String getCurrentUsername() {
        UserContext context = getContext();
        return context.isAuthenticated() ? context.getUsername() : null;
    }
    
    /**
     * 获取当前用户角色
     */
    public static String getCurrentUserRole() {
        UserContext context = getContext();
        return context.isAuthenticated() ? context.getRole() : null;
    }
    
    /**
     * 判断当前用户是否已认证
     */
    public static boolean isAuthenticated() {
        return getContext().isAuthenticated();
    }
    
    /**
     * 判断当前用户是否为管理员
     */
    public static boolean isAdmin() {
        return getContext().isAdmin();
    }
    
    /**
     * 判断当前用户是否为普通用户
     */
    public static boolean isUser() {
        return getContext().isUser();
    }
}