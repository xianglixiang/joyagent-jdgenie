package com.jd.genie.agent.dto.ragflow;

import lombok.Data;

/**
 * RAGFlow API响应基础类
 */
@Data
public class RAGFlowResponse<T> {
    private Integer code;
    private String message;
    private T data;
    private Boolean success;

    public boolean isSuccess() {
        return code != null && code == 200;
    }
}