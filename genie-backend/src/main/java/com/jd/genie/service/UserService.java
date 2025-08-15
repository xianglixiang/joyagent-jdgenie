package com.jd.genie.service;

import com.jd.genie.model.dto.UserDto;
import com.jd.genie.model.entity.User;
import com.jd.genie.model.req.LoginRequest;
import com.jd.genie.model.req.RegisterRequest;
import com.jd.genie.model.response.AuthResponse;

import java.util.List;

/**
 * 用户服务接口
 */
public interface UserService {

    /**
     * 用户注册
     */
    AuthResponse register(RegisterRequest request);

    /**
     * 用户登录
     */
    AuthResponse login(LoginRequest request);

    /**
     * 根据用户名查找用户
     */
    User findByUsername(String username);

    /**
     * 根据ID查找用户
     */
    User findById(Long id);

    /**
     * 更新用户信息
     */
    User updateUser(Long id, UserDto userDto);

    /**
     * 更新用户最后登录时间
     */
    void updateLastLogin(Long userId);

    /**
     * 验证密码
     */
    boolean validatePassword(String rawPassword, String hashedPassword);

    /**
     * 加密密码
     */
    String encryptPassword(String rawPassword);

    /**
     * 获取所有用户
     */
    List<User> getAllUsers();

    /**
     * 删除用户
     */
    void deleteUser(Long id);

    /**
     * 转换为DTO
     */
    UserDto convertToDto(User user);
}