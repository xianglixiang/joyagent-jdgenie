package com.jd.genie.controller;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.jd.genie.agent.tool.common.RAGFlowTool;
import com.jd.genie.config.GenieConfig;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 知识管理控制器
 * 提供RAGFlow知识库操作的REST API接口
 */
@Slf4j
@RestController
@RequestMapping("/api/knowledge")
public class KnowledgeController {

    @Autowired
    private GenieConfig genieConfig;

    /**
     * 创建数据集
     */
    @PostMapping("/datasets")
    public ResponseEntity<Map<String, Object>> createDataset(@RequestBody Map<String, Object> request) {
        try {
            RAGFlowTool ragflowTool = new RAGFlowTool();
            ragflowTool.setGenieConfig(genieConfig);

            Map<String, Object> params = new HashMap<>();
            params.put("action", "create_dataset");
            params.put("name", request.get("name"));
            params.put("description", request.getOrDefault("description", ""));

            Object result = ragflowTool.execute(params);
            return ResponseEntity.ok((Map<String, Object>) result);
        } catch (Exception e) {
            log.error("创建数据集失败", e);
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("message", "创建数据集失败: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResult);
        }
    }

    /**
     * 获取数据集列表
     */
    @GetMapping("/datasets")
    public ResponseEntity<Map<String, Object>> listDatasets(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int page_size,
            @RequestParam(required = false) String name) {
        try {
            RAGFlowTool ragflowTool = new RAGFlowTool();
            ragflowTool.setGenieConfig(genieConfig);

            Map<String, Object> params = new HashMap<>();
            params.put("action", "list_datasets");
            params.put("page", page);
            params.put("page_size", page_size);
            if (name != null) {
                params.put("name", name);
            }

            Object result = ragflowTool.execute(params);
            return ResponseEntity.ok((Map<String, Object>) result);
        } catch (Exception e) {
            log.error("获取数据集列表失败", e);
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("message", "获取数据集列表失败: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResult);
        }
    }

    /**
     * 删除数据集
     */
    @DeleteMapping("/datasets/{datasetId}")
    public ResponseEntity<Map<String, Object>> deleteDataset(@PathVariable String datasetId) {
        try {
            RAGFlowTool ragflowTool = new RAGFlowTool();
            ragflowTool.setGenieConfig(genieConfig);

            Map<String, Object> params = new HashMap<>();
            params.put("action", "delete_dataset");
            params.put("dataset_id", datasetId);

            Object result = ragflowTool.execute(params);
            return ResponseEntity.ok((Map<String, Object>) result);
        } catch (Exception e) {
            log.error("删除数据集失败", e);
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("message", "删除数据集失败: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResult);
        }
    }

    /**
     * 上传文档
     */
    @PostMapping("/datasets/{datasetId}/documents")
    public ResponseEntity<Map<String, Object>> uploadDocument(
            @PathVariable String datasetId,
            @RequestBody Map<String, Object> request) {
        try {
            RAGFlowTool ragflowTool = new RAGFlowTool();
            ragflowTool.setGenieConfig(genieConfig);

            Map<String, Object> params = new HashMap<>();
            params.put("action", "upload_document");
            params.put("dataset_id", datasetId);
            params.put("file_path", request.get("file_path"));
            params.put("name", request.getOrDefault("name", ""));

            Object result = ragflowTool.execute(params);
            return ResponseEntity.ok((Map<String, Object>) result);
        } catch (Exception e) {
            log.error("上传文档失败", e);
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("message", "上传文档失败: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResult);
        }
    }

    /**
     * 获取文档列表
     */
    @GetMapping("/datasets/{datasetId}/documents")
    public ResponseEntity<Map<String, Object>> listDocuments(
            @PathVariable String datasetId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int page_size,
            @RequestParam(required = false) String keywords) {
        try {
            RAGFlowTool ragflowTool = new RAGFlowTool();
            ragflowTool.setGenieConfig(genieConfig);

            Map<String, Object> params = new HashMap<>();
            params.put("action", "list_documents");
            params.put("dataset_id", datasetId);
            params.put("page", page);
            params.put("page_size", page_size);
            if (keywords != null) {
                params.put("keywords", keywords);
            }

            Object result = ragflowTool.execute(params);
            return ResponseEntity.ok((Map<String, Object>) result);
        } catch (Exception e) {
            log.error("获取文档列表失败", e);
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("message", "获取文档列表失败: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResult);
        }
    }

    /**
     * 删除文档
     */
    @DeleteMapping("/datasets/{datasetId}/documents/{documentId}")
    public ResponseEntity<Map<String, Object>> deleteDocument(
            @PathVariable String datasetId,
            @PathVariable String documentId) {
        try {
            RAGFlowTool ragflowTool = new RAGFlowTool();
            ragflowTool.setGenieConfig(genieConfig);

            Map<String, Object> params = new HashMap<>();
            params.put("action", "delete_document");
            params.put("dataset_id", datasetId);
            params.put("document_id", documentId);

            Object result = ragflowTool.execute(params);
            return ResponseEntity.ok((Map<String, Object>) result);
        } catch (Exception e) {
            log.error("删除文档失败", e);
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("message", "删除文档失败: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResult);
        }
    }

    /**
     * 知识检索
     */
    @PostMapping("/search")
    public ResponseEntity<Map<String, Object>> searchKnowledge(@RequestBody Map<String, Object> request) {
        try {
            RAGFlowTool ragflowTool = new RAGFlowTool();
            ragflowTool.setGenieConfig(genieConfig);

            Map<String, Object> params = new HashMap<>();
            params.put("action", "search_knowledge");
            params.put("query", request.get("query"));
            
            if (request.containsKey("dataset_id")) {
                params.put("dataset_id", request.get("dataset_id"));
            }

            Object result = ragflowTool.execute(params);
            return ResponseEntity.ok((Map<String, Object>) result);
        } catch (Exception e) {
            log.error("知识检索失败", e);
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("message", "知识检索失败: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResult);
        }
    }

    /**
     * 获取RAGFlow配置信息
     */
    @GetMapping("/config")
    public ResponseEntity<Map<String, Object>> getConfig() {
        try {
            Map<String, Object> config = new HashMap<>();
            config.put("ragflow_base_url", genieConfig.getRagflowBaseUrl());
            config.put("ragflow_timeout", genieConfig.getRagflowTimeout());
            config.put("ragflow_retry_attempts", genieConfig.getRagflowRetryAttempts());
            // 不返回API密钥以确保安全
            config.put("ragflow_api_key_configured", !genieConfig.getRagflowApiKey().isEmpty());
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("message", "获取配置成功");
            result.put("data", config);
            
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            log.error("获取RAGFlow配置失败", e);
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("message", "获取RAGFlow配置失败: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResult);
        }
    }

    /**
     * 批量操作接口
     */
    @PostMapping("/batch")
    public ResponseEntity<Map<String, Object>> batchOperations(@RequestBody Map<String, Object> request) {
        try {
            List<Map<String, Object>> operations = (List<Map<String, Object>>) request.get("operations");
            Map<String, Object> results = new HashMap<>();
            
            for (int i = 0; i < operations.size(); i++) {
                Map<String, Object> operation = operations.get(i);
                
                try {
                    RAGFlowTool ragflowTool = new RAGFlowTool();
                    ragflowTool.setGenieConfig(genieConfig);
                    
                    Object result = ragflowTool.execute(operation);
                    results.put("operation_" + i, result);
                } catch (Exception e) {
                    log.error("批量操作第{}项失败", i, e);
                    Map<String, Object> errorResult = new HashMap<>();
                    errorResult.put("success", false);
                    errorResult.put("message", "操作失败: " + e.getMessage());
                    results.put("operation_" + i, errorResult);
                }
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "批量操作完成");
            response.put("data", results);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("批量操作失败", e);
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("message", "批量操作失败: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResult);
        }
    }
}