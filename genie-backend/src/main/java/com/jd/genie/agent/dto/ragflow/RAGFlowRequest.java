package com.jd.genie.agent.dto.ragflow;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * RAGFlow API请求参数类
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RAGFlowRequest {
    private String action;
    private String datasetId;
    private String documentId;
    private String chunkId;
    private String name;
    private String description;
    private String content;
    private String query;
    private Map<String, Object> parameters;
    private Integer page;
    private Integer pageSize;
}