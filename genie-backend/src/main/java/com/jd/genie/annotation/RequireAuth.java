package com.jd.genie.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 需要认证注解
 * 用于标记需要用户登录才能访问的方法或类
 */
@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface RequireAuth {
    
    /**
     * 需要的用户角色，默认为任意已认证用户
     */
    String[] roles() default {};
    
    /**
     * 是否允许管理员访问，默认允许
     */
    boolean allowAdmin() default true;
}