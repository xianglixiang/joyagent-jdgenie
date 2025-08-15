package com.jd.genie.util;

import com.alibaba.fastjson.JSON;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;

/**
 * JWT工具类
 * 简化版本的JWT实现，用于用户认证
 */
@Slf4j
@Component
public class JwtUtil {

    private static final String SECRET_KEY = "genie-jwt-secret-key-2025";
    private static final String ALGORITHM = "HmacSHA256";
    private static final long DEFAULT_EXPIRATION = 24 * 60 * 60; // 24小时（秒）

    /**
     * 生成JWT Token
     *
     * @param userId 用户ID
     * @param username 用户名
     * @param role 用户角色
     * @return JWT Token
     */
    public String generateToken(Long userId, String username, String role) {
        return generateToken(userId, username, role, DEFAULT_EXPIRATION);
    }

    /**
     * 生成JWT Token
     *
     * @param userId 用户ID
     * @param username 用户名
     * @param role 用户角色
     * @param expirationSeconds 过期时间（秒）
     * @return JWT Token
     */
    public String generateToken(Long userId, String username, String role, long expirationSeconds) {
        try {
            // JWT Header
            Map<String, Object> header = new HashMap<>();
            header.put("alg", "HS256");
            header.put("typ", "JWT");

            // JWT Payload
            long nowSeconds = Instant.now().getEpochSecond();
            Map<String, Object> payload = new HashMap<>();
            payload.put("sub", String.valueOf(userId));
            payload.put("username", username);
            payload.put("role", role);
            payload.put("iat", nowSeconds);
            payload.put("exp", nowSeconds + expirationSeconds);

            // Base64编码
            String encodedHeader = encodeBase64Url(JSON.toJSONString(header));
            String encodedPayload = encodeBase64Url(JSON.toJSONString(payload));

            // 生成签名
            String data = encodedHeader + "." + encodedPayload;
            String signature = generateSignature(data);

            return data + "." + signature;
        } catch (Exception e) {
            log.error("生成JWT Token失败", e);
            return null;
        }
    }

    /**
     * 验证JWT Token
     *
     * @param token JWT Token
     * @return 是否有效
     */
    public boolean validateToken(String token) {
        try {
            if (token == null || token.trim().isEmpty()) {
                return false;
            }

            String[] parts = token.split("\\.");
            if (parts.length != 3) {
                return false;
            }

            // 验证签名
            String data = parts[0] + "." + parts[1];
            String expectedSignature = generateSignature(data);
            if (!expectedSignature.equals(parts[2])) {
                return false;
            }

            // 验证过期时间
            Map<String, Object> payload = parsePayload(token);
            if (payload == null) {
                return false;
            }

            // 安全地获取过期时间，处理Integer和Long类型
            Object expObj = payload.get("exp");
            if (expObj == null) {
                return false;
            }
            
            long exp;
            if (expObj instanceof Integer) {
                exp = ((Integer) expObj).longValue();
            } else if (expObj instanceof Long) {
                exp = (Long) expObj;
            } else {
                log.warn("exp字段类型不正确: {}", expObj.getClass().getSimpleName());
                return false;
            }
            
            return exp > Instant.now().getEpochSecond();
        } catch (Exception e) {
            log.error("验证JWT Token失败", e);
            return false;
        }
    }

    /**
     * 从Token中获取用户ID
     *
     * @param token JWT Token
     * @return 用户ID
     */
    public Long getUserIdFromToken(String token) {
        try {
            Map<String, Object> payload = parsePayload(token);
            if (payload != null) {
                String sub = (String) payload.get("sub");
                return sub != null ? Long.valueOf(sub) : null;
            }
        } catch (Exception e) {
            log.error("从Token获取用户ID失败", e);
        }
        return null;
    }

    /**
     * 从Token中获取用户名
     *
     * @param token JWT Token
     * @return 用户名
     */
    public String getUsernameFromToken(String token) {
        try {
            Map<String, Object> payload = parsePayload(token);
            return payload != null ? (String) payload.get("username") : null;
        } catch (Exception e) {
            log.error("从Token获取用户名失败", e);
            return null;
        }
    }

    /**
     * 从Token中获取用户角色
     *
     * @param token JWT Token
     * @return 用户角色
     */
    public String getRoleFromToken(String token) {
        try {
            Map<String, Object> payload = parsePayload(token);
            return payload != null ? (String) payload.get("role") : null;
        } catch (Exception e) {
            log.error("从Token获取用户角色失败", e);
            return null;
        }
    }

    /**
     * 从Token中获取过期时间
     *
     * @param token JWT Token
     * @return 过期时间
     */
    public LocalDateTime getExpirationFromToken(String token) {
        try {
            Map<String, Object> payload = parsePayload(token);
            if (payload != null) {
                // 安全地获取过期时间，处理Integer和Long类型
                Object expObj = payload.get("exp");
                if (expObj != null) {
                    long exp;
                    if (expObj instanceof Integer) {
                        exp = ((Integer) expObj).longValue();
                    } else if (expObj instanceof Long) {
                        exp = (Long) expObj;
                    } else {
                        log.warn("exp字段类型不正确: {}", expObj.getClass().getSimpleName());
                        return null;
                    }
                    return LocalDateTime.ofEpochSecond(exp, 0, ZoneOffset.UTC);
                }
            }
        } catch (Exception e) {
            log.error("从Token获取过期时间失败", e);
        }
        return null;
    }

    /**
     * 解析Token的Payload部分
     */
    private Map<String, Object> parsePayload(String token) {
        try {
            String[] parts = token.split("\\.");
            if (parts.length != 3) {
                return null;
            }

            String payloadJson = decodeBase64Url(parts[1]);
            @SuppressWarnings("unchecked")
            Map<String, Object> result = JSON.parseObject(payloadJson, Map.class);
            return result;
        } catch (Exception e) {
            log.error("解析Token Payload失败", e);
            return null;
        }
    }

    /**
     * 生成HMAC签名
     */
    private String generateSignature(String data) throws Exception {
        Mac mac = Mac.getInstance(ALGORITHM);
        SecretKeySpec secretKeySpec = new SecretKeySpec(SECRET_KEY.getBytes(StandardCharsets.UTF_8), ALGORITHM);
        mac.init(secretKeySpec);
        byte[] signature = mac.doFinal(data.getBytes(StandardCharsets.UTF_8));
        return encodeBase64Url(signature);
    }

    /**
     * Base64 URL安全编码
     */
    private String encodeBase64Url(String data) {
        return encodeBase64Url(data.getBytes(StandardCharsets.UTF_8));
    }

    private String encodeBase64Url(byte[] data) {
        return Base64.getUrlEncoder().withoutPadding().encodeToString(data);
    }

    /**
     * Base64 URL安全解码
     */
    private String decodeBase64Url(String encoded) {
        byte[] decoded = Base64.getUrlDecoder().decode(encoded);
        return new String(decoded, StandardCharsets.UTF_8);
    }
}