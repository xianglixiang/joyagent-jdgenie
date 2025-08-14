package com.jd.genie.agent.dto.ragflow;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

/**
 * RAGFlow数据集实体类
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Dataset {
    private String id;
    private String name;
    private String avatar;
    private String description;
    private String embeddingModel;
    private String permission;
    private String chunkMethod;
    private String createTime;
    private String updateTime;
    private Long documentCount;
    private Long chunkCount;
}