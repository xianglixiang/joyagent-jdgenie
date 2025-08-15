package com.jd.genie.config;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

/**
 * 用户上下文信息
 * 存储当前请求的用户信息
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserContext {
    
    private Long userId;
    private String username;
    private String role;
    private boolean authenticated;
    
    /**
     * 创建认证用户上下文
     */
    public static UserContext authenticated(Long userId, String username, String role) {
        return UserContext.builder()
                .userId(userId)
                .username(username)
                .role(role)
                .authenticated(true)
                .build();
    }
    
    /**
     * 创建未认证用户上下文
     */
    public static UserContext unauthenticated() {
        return UserContext.builder()
                .authenticated(false)
                .build();
    }
    
    /**
     * 判断是否为管理员
     */
    public boolean isAdmin() {
        return authenticated && "ADMIN".equals(role);
    }
    
    /**
     * 判断是否为普通用户
     */
    public boolean isUser() {
        return authenticated && "USER".equals(role);
    }
}