package com.jd.genie.agent.tool.common;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.jd.genie.agent.dto.ragflow.*;
import com.jd.genie.agent.tool.BaseTool;
import com.jd.genie.agent.util.OkHttpUtil;
import com.jd.genie.config.GenieConfig;
import com.jd.genie.agent.agent.AgentContext;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

import java.util.*;

/**
 * RAGFlow知识管理工具
 * 提供数据集、文档和知识检索功能
 */
@Slf4j
public class RAGFlowTool implements BaseTool {

    private GenieConfig genieConfig;
    private AgentContext agentContext;

    public void setAgentContext(AgentContext agentContext) {
        this.agentContext = agentContext;
    }

    public void setGenieConfig(GenieConfig genieConfig) {
        this.genieConfig = genieConfig;
    }

    @Override
    public String getName() {
        return "ragflow_knowledge";
    }

    @Override
    public String getDescription() {
        return "RAGFlow知识管理工具，支持创建和管理知识库数据集、上传和管理文档、智能检索知识内容。" +
                "支持的操作包括：" +
                "1. 创建数据集(create_dataset)" +
                "2. 列出数据集(list_datasets)" +
                "3. 上传文档(upload_document)" +
                "4. 列出文档(list_documents)" +
                "5. 知识检索(search_knowledge)" +
                "6. 删除数据集(delete_dataset)" +
                "7. 删除文档(delete_document)";
    }

    @Override
    public Map<String, Object> toParams() {
        Map<String, Object> properties = new HashMap<>();
        
        Map<String, Object> action = new HashMap<>();
        action.put("type", "string");
        action.put("description", "操作类型");
        action.put("enum", Arrays.asList("create_dataset", "list_datasets", "upload_document", 
                "list_documents", "search_knowledge", "delete_dataset", "delete_document"));
        properties.put("action", action);

        Map<String, Object> name = new HashMap<>();
        name.put("type", "string");
        name.put("description", "名称（创建数据集或上传文档时使用）");
        properties.put("name", name);

        Map<String, Object> description = new HashMap<>();
        description.put("type", "string");
        description.put("description", "描述信息");
        properties.put("description", description);

        Map<String, Object> datasetId = new HashMap<>();
        datasetId.put("type", "string");
        datasetId.put("description", "数据集ID（操作文档时使用）");
        properties.put("dataset_id", datasetId);

        Map<String, Object> query = new HashMap<>();
        query.put("type", "string");
        query.put("description", "检索查询内容");
        properties.put("query", query);

        Map<String, Object> filePath = new HashMap<>();
        filePath.put("type", "string");
        filePath.put("description", "文件路径（上传文档时使用）");
        properties.put("file_path", filePath);

        Map<String, Object> params = new HashMap<>();
        params.put("type", "object");
        params.put("properties", properties);
        params.put("required", Arrays.asList("action"));

        return params;
    }

    @Override
    public Object execute(Object input) {
        try {
            JSONObject inputJson = JSON.parseObject(JSON.toJSONString(input));
            String action = inputJson.getString("action");
            
            if (StringUtils.isEmpty(action)) {
                return buildError("操作类型不能为空");
            }

            switch (action) {
                case "create_dataset":
                    return createDataset(inputJson);
                case "list_datasets":
                    return listDatasets(inputJson);
                case "upload_document":
                    return uploadDocument(inputJson);
                case "list_documents":
                    return listDocuments(inputJson);
                case "search_knowledge":
                    return searchKnowledge(inputJson);
                case "delete_dataset":
                    return deleteDataset(inputJson);
                case "delete_document":
                    return deleteDocument(inputJson);
                default:
                    return buildError("不支持的操作类型: " + action);
            }
        } catch (Exception e) {
            log.error("RAGFlow工具执行失败", e);
            return buildError("执行失败: " + e.getMessage());
        }
    }

    private Object createDataset(JSONObject input) {
        String name = input.getString("name");
        String description = input.getString("description");
        
        if (StringUtils.isEmpty(name)) {
            return buildError("数据集名称不能为空");
        }

        try {
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("name", name);
            requestBody.put("description", description != null ? description : "");
            requestBody.put("embedding_model", "text-embedding-3-small");
            requestBody.put("permission", "me");
            requestBody.put("chunk_method", "manual");

            String response = OkHttpUtil.post(
                    getBaseUrl() + "/api/v1/datasets",
                    JSON.toJSONString(requestBody),
                    getHeaders()
            );

            RAGFlowResponse<?> ragflowResponse = JSON.parseObject(response, RAGFlowResponse.class);
            if (ragflowResponse.isSuccess()) {
                return buildSuccess("数据集创建成功", ragflowResponse.getData());
            } else {
                return buildError("创建数据集失败: " + ragflowResponse.getMessage());
            }
        } catch (Exception e) {
            log.error("创建数据集失败", e);
            return buildError("创建数据集失败: " + e.getMessage());
        }
    }

    private Object listDatasets(JSONObject input) {
        try {
            Integer page = input.getInteger("page");
            Integer pageSize = input.getInteger("page_size");
            
            StringBuilder url = new StringBuilder(getBaseUrl() + "/api/v1/datasets");
            url.append("?page=").append(page != null ? page : 1);
            url.append("&page_size=").append(pageSize != null ? pageSize : 20);

            String response = OkHttpUtil.get(url.toString(), getHeaders());
            
            RAGFlowResponse<?> ragflowResponse = JSON.parseObject(response, RAGFlowResponse.class);
            if (ragflowResponse.isSuccess()) {
                return buildSuccess("获取数据集列表成功", ragflowResponse.getData());
            } else {
                return buildError("获取数据集列表失败: " + ragflowResponse.getMessage());
            }
        } catch (Exception e) {
            log.error("获取数据集列表失败", e);
            return buildError("获取数据集列表失败: " + e.getMessage());
        }
    }

    private Object uploadDocument(JSONObject input) {
        String datasetId = input.getString("dataset_id");
        String filePath = input.getString("file_path");
        String name = input.getString("name");
        
        if (StringUtils.isEmpty(datasetId)) {
            return buildError("数据集ID不能为空");
        }
        if (StringUtils.isEmpty(filePath)) {
            return buildError("文件路径不能为空");
        }

        try {
            // 这里简化实现，实际应该使用multipart/form-data上传文件
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("name", name != null ? name : filePath);
            requestBody.put("file_path", filePath);

            String response = OkHttpUtil.post(
                    getBaseUrl() + "/api/v1/datasets/" + datasetId + "/documents",
                    JSON.toJSONString(requestBody),
                    getHeaders()
            );

            RAGFlowResponse<?> ragflowResponse = JSON.parseObject(response, RAGFlowResponse.class);
            if (ragflowResponse.isSuccess()) {
                return buildSuccess("文档上传成功", ragflowResponse.getData());
            } else {
                return buildError("上传文档失败: " + ragflowResponse.getMessage());
            }
        } catch (Exception e) {
            log.error("上传文档失败", e);
            return buildError("上传文档失败: " + e.getMessage());
        }
    }

    private Object listDocuments(JSONObject input) {
        String datasetId = input.getString("dataset_id");
        
        if (StringUtils.isEmpty(datasetId)) {
            return buildError("数据集ID不能为空");
        }

        try {
            Integer page = input.getInteger("page");
            Integer pageSize = input.getInteger("page_size");
            
            StringBuilder url = new StringBuilder(getBaseUrl() + "/api/v1/datasets/" + datasetId + "/documents");
            url.append("?page=").append(page != null ? page : 1);
            url.append("&page_size=").append(pageSize != null ? pageSize : 20);

            String response = OkHttpUtil.get(url.toString(), getHeaders());
            
            RAGFlowResponse<?> ragflowResponse = JSON.parseObject(response, RAGFlowResponse.class);
            if (ragflowResponse.isSuccess()) {
                return buildSuccess("获取文档列表成功", ragflowResponse.getData());
            } else {
                return buildError("获取文档列表失败: " + ragflowResponse.getMessage());
            }
        } catch (Exception e) {
            log.error("获取文档列表失败", e);
            return buildError("获取文档列表失败: " + e.getMessage());
        }
    }

    private Object searchKnowledge(JSONObject input) {
        String query = input.getString("query");
        String datasetId = input.getString("dataset_id");
        
        if (StringUtils.isEmpty(query)) {
            return buildError("检索查询不能为空");
        }

        try {
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("query", query);
            if (!StringUtils.isEmpty(datasetId)) {
                requestBody.put("dataset_ids", Arrays.asList(datasetId));
            }
            requestBody.put("top_k", 10);
            requestBody.put("similarity_threshold", 0.1);

            String response = OkHttpUtil.post(
                    getBaseUrl() + "/api/v1/search",
                    JSON.toJSONString(requestBody),
                    getHeaders()
            );

            RAGFlowResponse<?> ragflowResponse = JSON.parseObject(response, RAGFlowResponse.class);
            if (ragflowResponse.isSuccess()) {
                return buildSuccess("知识检索成功", ragflowResponse.getData());
            } else {
                return buildError("知识检索失败: " + ragflowResponse.getMessage());
            }
        } catch (Exception e) {
            log.error("知识检索失败", e);
            return buildError("知识检索失败: " + e.getMessage());
        }
    }

    private Object deleteDataset(JSONObject input) {
        String datasetId = input.getString("dataset_id");
        
        if (StringUtils.isEmpty(datasetId)) {
            return buildError("数据集ID不能为空");
        }

        try {
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("ids", Arrays.asList(datasetId));

            String response = OkHttpUtil.delete(
                    getBaseUrl() + "/api/v1/datasets",
                    JSON.toJSONString(requestBody),
                    getHeaders()
            );

            RAGFlowResponse<?> ragflowResponse = JSON.parseObject(response, RAGFlowResponse.class);
            if (ragflowResponse.isSuccess()) {
                return buildSuccess("数据集删除成功", null);
            } else {
                return buildError("删除数据集失败: " + ragflowResponse.getMessage());
            }
        } catch (Exception e) {
            log.error("删除数据集失败", e);
            return buildError("删除数据集失败: " + e.getMessage());
        }
    }

    private Object deleteDocument(JSONObject input) {
        String datasetId = input.getString("dataset_id");
        String documentId = input.getString("document_id");
        
        if (StringUtils.isEmpty(datasetId)) {
            return buildError("数据集ID不能为空");
        }
        if (StringUtils.isEmpty(documentId)) {
            return buildError("文档ID不能为空");
        }

        try {
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("ids", Arrays.asList(documentId));

            String response = OkHttpUtil.delete(
                    getBaseUrl() + "/api/v1/datasets/" + datasetId + "/documents",
                    JSON.toJSONString(requestBody),
                    getHeaders()
            );

            RAGFlowResponse<?> ragflowResponse = JSON.parseObject(response, RAGFlowResponse.class);
            if (ragflowResponse.isSuccess()) {
                return buildSuccess("文档删除成功", null);
            } else {
                return buildError("删除文档失败: " + ragflowResponse.getMessage());
            }
        } catch (Exception e) {
            log.error("删除文档失败", e);
            return buildError("删除文档失败: " + e.getMessage());
        }
    }

    private String getBaseUrl() {
        return genieConfig.getRagflowBaseUrl();
    }

    private Map<String, String> getHeaders() {
        Map<String, String> headers = new HashMap<>();
        headers.put("Content-Type", "application/json");
        headers.put("Authorization", "Bearer " + genieConfig.getRagflowApiKey());
        return headers;
    }

    private Map<String, Object> buildSuccess(String message, Object data) {
        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("message", message);
        result.put("data", data);
        return result;
    }

    private Map<String, Object> buildError(String message) {
        Map<String, Object> result = new HashMap<>();
        result.put("success", false);
        result.put("message", message);
        return result;
    }
}