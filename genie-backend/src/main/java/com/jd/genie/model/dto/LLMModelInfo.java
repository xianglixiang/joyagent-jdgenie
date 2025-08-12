package com.jd.genie.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * LLM模型信息DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LLMModelInfo {
    /**
     * 模型标识符
     */
    private String modelKey;

    /**
     * 模型显示名称
     */
    private String displayName;

    /**
     * 模型描述
     */
    private String description;

    /**
     * 是否为当前选中模型
     */
    private boolean isCurrent;

    /**
     * 是否可用
     */
    private boolean available;

    /**
     * 最大token数
     */
    private Integer maxTokens;

    /**
     * 模型类型（如：GPT-4, Claude等）
     */
    private String modelType;
}