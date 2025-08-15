package com.jd.genie.service.impl;

import com.jd.genie.model.dto.UserDto;
import com.jd.genie.model.entity.User;
import com.jd.genie.model.req.LoginRequest;
import com.jd.genie.model.req.RegisterRequest;
import com.jd.genie.model.response.AuthResponse;
import com.jd.genie.service.UserService;
import com.jd.genie.util.JwtUtil;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 用户服务实现类
 * 使用内存存储，后续可扩展为数据库存储
 */
@Slf4j
@Service
public class UserServiceImpl implements UserService {

    @Autowired
    private JwtUtil jwtUtil;

    // 模拟用户数据存储
    private final Map<Long, User> userStore = new ConcurrentHashMap<>();
    private final Map<String, User> usernameIndex = new ConcurrentHashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(1);

    public UserServiceImpl() {
        // 初始化默认用户
        initDefaultUsers();
    }

    private void initDefaultUsers() {
        // 创建默认管理员用户
        User admin = User.builder()
                .id(idGenerator.getAndIncrement())
                .username("admin")
                .email("admin@example.com")
                .passwordHash(encryptPassword("admin123"))
                .fullName("管理员")
                .role(User.UserRole.ADMIN)
                .status(User.UserStatus.ACTIVE)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();
        
        userStore.put(admin.getId(), admin);
        usernameIndex.put(admin.getUsername(), admin);

        // 创建默认普通用户
        User user = User.builder()
                .id(idGenerator.getAndIncrement())
                .username("user")
                .email("user@example.com")
                .passwordHash(encryptPassword("user123"))
                .fullName("普通用户")
                .role(User.UserRole.USER)
                .status(User.UserStatus.ACTIVE)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();
        
        userStore.put(user.getId(), user);
        usernameIndex.put(user.getUsername(), user);
    }

    @Override
    public AuthResponse register(RegisterRequest request) {
        try {
            // 验证用户名是否已存在
            if (usernameIndex.containsKey(request.getUsername())) {
                return AuthResponse.builder()
                        .message("用户名已存在")
                        .build();
            }

            // 验证密码确认
            if (!request.getPassword().equals(request.getConfirmPassword())) {
                return AuthResponse.builder()
                        .message("两次输入的密码不一致")
                        .build();
            }

            // 创建新用户
            User newUser = User.builder()
                    .id(idGenerator.getAndIncrement())
                    .username(request.getUsername())
                    .email(request.getEmail())
                    .passwordHash(encryptPassword(request.getPassword()))
                    .fullName(request.getFullName())
                    .role(User.UserRole.USER)
                    .status(User.UserStatus.ACTIVE)
                    .createdAt(LocalDateTime.now())
                    .updatedAt(LocalDateTime.now())
                    .build();

            // 保存用户
            userStore.put(newUser.getId(), newUser);
            usernameIndex.put(newUser.getUsername(), newUser);

            // 生成JWT Token
            String token = jwtUtil.generateToken(newUser.getId(), newUser.getUsername(), newUser.getRole().name());

            return AuthResponse.builder()
                    .token(token)
                    .expiresIn(24 * 60 * 60L) // 24小时
                    .user(convertToDto(newUser))
                    .message("注册成功")
                    .build();
        } catch (Exception e) {
            log.error("用户注册失败", e);
            return AuthResponse.builder()
                    .message("注册失败: " + e.getMessage())
                    .build();
        }
    }

    @Override
    public AuthResponse login(LoginRequest request) {
        try {
            // 查找用户
            User user = usernameIndex.get(request.getUsername());
            if (user == null) {
                return AuthResponse.builder()
                        .message("用户名或密码错误")
                        .build();
            }

            // 验证密码
            if (!validatePassword(request.getPassword(), user.getPasswordHash())) {
                return AuthResponse.builder()
                        .message("用户名或密码错误")
                        .build();
            }

            // 检查用户状态
            if (user.getStatus() != User.UserStatus.ACTIVE) {
                return AuthResponse.builder()
                        .message("用户账户已被禁用")
                        .build();
            }

            // 更新最后登录时间
            updateLastLogin(user.getId());

            // 生成JWT Token
            long expirationSeconds = request.getRememberMe() ? 7 * 24 * 60 * 60L : 24 * 60 * 60L; // 记住我7天，否则24小时
            String token = jwtUtil.generateToken(user.getId(), user.getUsername(), user.getRole().name(), expirationSeconds);

            return AuthResponse.builder()
                    .token(token)
                    .expiresIn(expirationSeconds)
                    .user(convertToDto(user))
                    .message("登录成功")
                    .build();
        } catch (Exception e) {
            log.error("用户登录失败", e);
            return AuthResponse.builder()
                    .message("登录失败: " + e.getMessage())
                    .build();
        }
    }

    @Override
    public User findByUsername(String username) {
        return usernameIndex.get(username);
    }

    @Override
    public User findById(Long id) {
        return userStore.get(id);
    }

    @Override
    public User updateUser(Long id, UserDto userDto) {
        User user = userStore.get(id);
        if (user == null) {
            return null;
        }

        // 更新用户信息
        if (userDto.getFullName() != null) {
            user.setFullName(userDto.getFullName());
        }
        if (userDto.getEmail() != null) {
            user.setEmail(userDto.getEmail());
        }
        if (userDto.getAvatar() != null) {
            user.setAvatar(userDto.getAvatar());
        }
        
        user.setUpdatedAt(LocalDateTime.now());
        userStore.put(id, user);
        
        return user;
    }

    @Override
    public void updateLastLogin(Long userId) {
        User user = userStore.get(userId);
        if (user != null) {
            user.setLastLogin(LocalDateTime.now());
            user.setUpdatedAt(LocalDateTime.now());
            userStore.put(userId, user);
        }
    }

    @Override
    public boolean validatePassword(String rawPassword, String hashedPassword) {
        return hashedPassword.equals(encryptPassword(rawPassword));
    }

    @Override
    public String encryptPassword(String rawPassword) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest((rawPassword + "genie-salt").getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    hexString.append('0');
                }
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (Exception e) {
            log.error("密码加密失败", e);
            return rawPassword;
        }
    }

    @Override
    public List<User> getAllUsers() {
        return new ArrayList<>(userStore.values());
    }

    @Override
    public void deleteUser(Long id) {
        User user = userStore.remove(id);
        if (user != null) {
            usernameIndex.remove(user.getUsername());
        }
    }

    @Override
    public UserDto convertToDto(User user) {
        if (user == null) {
            return null;
        }
        
        return UserDto.builder()
                .id(user.getId())
                .username(user.getUsername())
                .email(user.getEmail())
                .fullName(user.getFullName())
                .role(user.getRole().name())
                .status(user.getStatus().name())
                .lastLogin(user.getLastLogin())
                .createdAt(user.getCreatedAt())
                .apiQuotaDaily(user.getApiQuotaDaily())
                .apiQuotaUsed(user.getApiQuotaUsed())
                .avatar(user.getAvatar())
                .build();
    }
}