package com.jd.genie.controller;

import com.jd.genie.model.dto.UserDto;
import com.jd.genie.model.entity.User;
import com.jd.genie.model.req.LoginRequest;
import com.jd.genie.model.req.RegisterRequest;
import com.jd.genie.model.response.AuthResponse;
import com.jd.genie.model.response.ApiResponse;
import com.jd.genie.service.UserService;
import com.jd.genie.util.JwtUtil;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 认证控制器
 */
@Slf4j
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @Autowired
    private UserService userService;

    @Autowired
    private JwtUtil jwtUtil;

    /**
     * 测试方法
     */
    @GetMapping("/test")
    public ResponseEntity<ApiResponse<String>> test() {
        return ResponseEntity.ok(ApiResponse.success("Auth controller is working", "测试成功"));
    }

    /**
     * 用户注册
     */
    @PostMapping("/register")
    public ResponseEntity<ApiResponse<AuthResponse>> register(@Valid @RequestBody RegisterRequest request) {
        log.info("用户注册请求: {}", request.getUsername());
        
        try {
            AuthResponse response = userService.register(request);
            
            if (response.getToken() != null) {
                return ResponseEntity.ok(ApiResponse.success(response, "注册成功"));
            } else {
                return ResponseEntity.badRequest().body(ApiResponse.error(response.getMessage() != null ? response.getMessage() : "注册失败"));
            }
        } catch (Exception e) {
            log.error("注册过程中发生错误", e);
            return ResponseEntity.status(500).body(ApiResponse.error("注册失败: " + e.getMessage()));
        }
    }

    /**
     * 用户登录
     */
    @PostMapping("/login")
    public ResponseEntity<ApiResponse<AuthResponse>> login(@Valid @RequestBody LoginRequest request) {
        log.info("用户登录请求: {}", request.getUsername());
        
        try {
            AuthResponse response = userService.login(request);
            
            if (response.getToken() != null) {
                return ResponseEntity.ok(ApiResponse.success(response, "登录成功"));
            } else {
                return ResponseEntity.badRequest().body(ApiResponse.error(response.getMessage() != null ? response.getMessage() : "登录失败"));
            }
        } catch (Exception e) {
            log.error("登录过程中发生错误", e);
            return ResponseEntity.status(500).body(ApiResponse.error("登录失败: " + e.getMessage()));
        }
    }

    /**
     * 获取当前用户信息
     */
    @GetMapping("/me")
    public ResponseEntity<ApiResponse<UserDto>> getCurrentUser(HttpServletRequest request) {
        try {
            String token = extractToken(request);
            if (token == null || !jwtUtil.validateToken(token)) {
                return ResponseEntity.status(401).body(ApiResponse.error("Token无效或已过期"));
            }

            Long userId = jwtUtil.getUserIdFromToken(token);
            User user = userService.findById(userId);
            
            if (user == null) {
                return ResponseEntity.status(404).body(ApiResponse.error("用户不存在"));
            }

            UserDto userDto = userService.convertToDto(user);
            return ResponseEntity.ok(ApiResponse.success(userDto, "获取用户信息成功"));
        } catch (Exception e) {
            log.error("获取当前用户信息失败", e);
            return ResponseEntity.status(500).body(ApiResponse.error("获取用户信息失败"));
        }
    }

    /**
     * 验证Token
     */
    @PostMapping("/validate")
    public ResponseEntity<ApiResponse<Map<String, Object>>> validateToken(HttpServletRequest request) {
        try {
            String token = extractToken(request);
            boolean isValid = token != null && jwtUtil.validateToken(token);
            
            Map<String, Object> data = new HashMap<>();
            data.put("valid", isValid);
            
            if (isValid) {
                data.put("userId", jwtUtil.getUserIdFromToken(token));
                data.put("username", jwtUtil.getUsernameFromToken(token));
                data.put("role", jwtUtil.getRoleFromToken(token));
                data.put("expiration", jwtUtil.getExpirationFromToken(token));
            }
            
            return ResponseEntity.ok(ApiResponse.success(data, "Token验证完成"));
        } catch (Exception e) {
            log.error("验证Token失败", e);
            return ResponseEntity.status(500).body(ApiResponse.error("Token验证失败"));
        }
    }

    /**
     * 用户登出
     */
    @PostMapping("/logout")
    public ResponseEntity<ApiResponse<String>> logout() {
        // 对于JWT，登出通常由客户端处理（删除本地存储的Token）
        // 这里只是提供一个端点确认登出操作
        return ResponseEntity.ok(ApiResponse.success("logout", "登出成功"));
    }

    /**
     * 刷新Token
     */
    @PostMapping("/refresh")
    public ResponseEntity<ApiResponse<AuthResponse>> refreshToken(HttpServletRequest request) {
        try {
            String token = extractToken(request);
            if (token == null || !jwtUtil.validateToken(token)) {
                return ResponseEntity.status(401).body(ApiResponse.error("Token无效或已过期"));
            }

            Long userId = jwtUtil.getUserIdFromToken(token);
            User user = userService.findById(userId);
            
            if (user == null) {
                return ResponseEntity.status(404).body(ApiResponse.error("用户不存在"));
            }

            // 生成新Token
            String newToken = jwtUtil.generateToken(user.getId(), user.getUsername(), user.getRole().name());
            
            AuthResponse authResponse = AuthResponse.builder()
                .token(newToken)
                .expiresIn(24 * 60 * 60L)
                .user(userService.convertToDto(user))
                .message("Token刷新成功")
                .build();
            
            return ResponseEntity.ok(ApiResponse.success(authResponse, "Token刷新成功"));
        } catch (Exception e) {
            log.error("刷新Token失败", e);
            return ResponseEntity.status(500).body(ApiResponse.error("刷新Token失败"));
        }
    }

    /**
     * 获取所有用户（管理员功能）
     */
    @GetMapping("/users")
    public ResponseEntity<ApiResponse<List<UserDto>>> getAllUsers(HttpServletRequest request) {
        try {
            String token = extractToken(request);
            if (token == null || !jwtUtil.validateToken(token)) {
                return ResponseEntity.status(401).body(ApiResponse.error("未授权访问"));
            }

            String role = jwtUtil.getRoleFromToken(token);
            if (!"ADMIN".equals(role)) {
                return ResponseEntity.status(403).body(ApiResponse.error("权限不足"));
            }

            List<User> users = userService.getAllUsers();
            List<UserDto> userDtos = users.stream()
                    .map(userService::convertToDto)
                    .toList();

            return ResponseEntity.ok(ApiResponse.success(userDtos, "获取用户列表成功"));
        } catch (Exception e) {
            log.error("获取用户列表失败", e);
            return ResponseEntity.status(500).body(ApiResponse.error("获取用户列表失败"));
        }
    }

    /**
     * 从请求中提取Token
     */
    private String extractToken(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }
}