package com.jd.genie.agent.dto.ragflow;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * RAGFlow文档实体类
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Document {
    private String id;
    private String name;
    private String datasetId;
    private String type;
    private String size;
    private String status;
    private String createTime;
    private String updateTime;
    private Map<String, Object> metaFields;
    private String chunkMethod;
    private Map<String, Object> parserConfig;
    private Long chunkCount;
}