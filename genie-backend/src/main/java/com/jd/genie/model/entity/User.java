package com.jd.genie.model.entity;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 用户实体类
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class User {
    
    private Long id;
    private String username;
    private String email;
    private String passwordHash;
    private String fullName;
    
    @Builder.Default
    private UserRole role = UserRole.USER;
    
    @Builder.Default
    private UserStatus status = UserStatus.ACTIVE;
    
    private LocalDateTime lastLogin;
    
    @Builder.Default
    private LocalDateTime createdAt = LocalDateTime.now();
    
    @Builder.Default
    private LocalDateTime updatedAt = LocalDateTime.now();
    
    @Builder.Default
    private Integer apiQuotaDaily = 100;
    
    @Builder.Default
    private Integer apiQuotaUsed = 0;
    
    private String preferences;
    private String avatar;
    
    /**
     * 用户角色枚举
     */
    public enum UserRole {
        ADMIN, USER, GUEST
    }
    
    /**
     * 用户状态枚举
     */
    public enum UserStatus {
        ACTIVE, INACTIVE, SUSPENDED
    }
}