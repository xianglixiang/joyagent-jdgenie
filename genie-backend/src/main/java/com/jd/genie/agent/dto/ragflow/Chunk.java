package com.jd.genie.agent.dto.ragflow;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * RAGFlow文档块实体类
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Chunk {
    private String id;
    private String documentId;
    private String content;
    private List<String> importantKeywords;
    private String createTime;
    private String updateTime;
    private Integer tokenCount;
    private Double similarity;
}