package com.jd.genie.model.req;

import lombok.Data;

/**
 * LLM模型切换请求
 */
@Data
public class LLMSwitchRequest {
    /**
     * 目标模型名称
     */
    private String modelName;

    /**
     * 会话ID（可选，用于特定会话切换）
     */
    private String sessionId;
}