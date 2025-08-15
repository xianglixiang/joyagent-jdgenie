package com.jd.genie.controller;

import com.jd.genie.model.response.ApiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * 测试控制器 - 用于验证基本配置
 */
@Slf4j
@RestController
@RequestMapping("/api/test")
public class TestController {

    @GetMapping("/health")
    public ResponseEntity<ApiResponse<Map<String, Object>>> health() {
        log.info("Health check endpoint called");
        Map<String, Object> data = new HashMap<>();
        data.put("status", "running");
        data.put("timestamp", System.currentTimeMillis());
        return ResponseEntity.ok(ApiResponse.success(data, "Service is running"));
    }

    @PostMapping("/echo")
    public ResponseEntity<ApiResponse<Map<String, Object>>> echo(@RequestBody Map<String, Object> request) {
        log.info("Echo endpoint called with data: {}", request);
        return ResponseEntity.ok(ApiResponse.success(request, "Echo successful"));
    }
}