package com.jd.genie.util;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.TypeReference;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Prompt文件加载器
 * 用于从外部Markdown文件加载prompt内容
 */
@Slf4j
@Component
public class PromptLoader {

    /**
     * Prompt缓存，避免重复读取文件
     */
    private final Map<String, String> promptCache = new ConcurrentHashMap<>();

    /**
     * 加载指定路径的prompt文件内容
     *
     * @param promptPath 相对于classpath:prompts/的文件路径，如 "planner/system.md"
     * @return prompt内容
     */
    public String loadPrompt(String promptPath) {
        // 检查缓存
        if (promptCache.containsKey(promptPath)) {
            return promptCache.get(promptPath);
        }

        try {
            String fullPath = "prompts/" + promptPath;
            ClassPathResource resource = new ClassPathResource(fullPath);
            
            if (!resource.exists()) {
                log.warn("Prompt file not found: {}", fullPath);
                return "";
            }

            String content = new String(resource.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
            
            // 缓存内容
            promptCache.put(promptPath, content);
            
            log.debug("Loaded prompt from: {}", fullPath);
            return content;
            
        } catch (IOException e) {
            log.error("Failed to load prompt file: prompts/{}", promptPath, e);
            return "";
        }
    }

    /**
     * 加载并解析JSON格式的prompt配置
     * 用于处理包含多个语言版本的prompt配置
     *
     * @param promptPath prompt文件路径
     * @return Map<String, String> 语言代码 -> prompt内容的映射
     */
    public Map<String, String> loadPromptMap(String promptPath) {
        String content = loadPrompt(promptPath);
        
        if (content.isEmpty()) {
            return new HashMap<>();
        }

        try {
            // 尝试解析为JSON格式的多语言配置
            return JSON.parseObject(content, new TypeReference<Map<String, String>>() {});
        } catch (Exception e) {
            // 如果不是JSON格式，则将整个内容作为default语言
            Map<String, String> result = new HashMap<>();
            result.put("default", content);
            return result;
        }
    }

    /**
     * 清空缓存，用于开发环境下重新加载配置
     */
    public void clearCache() {
        promptCache.clear();
        log.info("Prompt cache cleared");
    }

    /**
     * 获取缓存状态信息
     */
    public Map<String, Object> getCacheInfo() {
        Map<String, Object> info = new HashMap<>();
        info.put("cacheSize", promptCache.size());
        info.put("cachedPrompts", promptCache.keySet());
        return info;
    }
}