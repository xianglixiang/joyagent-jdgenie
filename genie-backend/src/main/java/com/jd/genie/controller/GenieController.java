package com.jd.genie.controller;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.jd.genie.agent.agent.AgentContext;
import com.jd.genie.agent.printer.Printer;
import com.jd.genie.agent.printer.SSEPrinter;
import com.jd.genie.agent.tool.ToolCollection;
import com.jd.genie.agent.tool.common.CodeInterpreterTool;
import com.jd.genie.agent.tool.common.DeepSearchTool;
import com.jd.genie.agent.tool.common.FileTool;
import com.jd.genie.agent.tool.common.ReportTool;
import com.jd.genie.agent.tool.mcp.McpTool;
import com.jd.genie.agent.util.DateUtil;
import com.jd.genie.agent.util.ThreadUtil;
import com.jd.genie.config.GenieConfig;
import com.jd.genie.model.req.AgentRequest;
import com.jd.genie.model.req.GptQueryReq;
import com.jd.genie.model.req.LLMSwitchRequest;
import com.jd.genie.model.dto.LLMModelInfo;
import com.jd.genie.service.AgentHandlerService;
import com.jd.genie.service.IGptProcessService;
import com.jd.genie.service.impl.AgentHandlerFactory;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.UnsupportedEncodingException;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;

@Slf4j
@RestController
@RequestMapping("/")
public class GenieController {
    private final ScheduledExecutorService executor = Executors.newScheduledThreadPool(5);
    private static final long HEARTBEAT_INTERVAL = 10_000L; // 10秒心跳间隔
    @Autowired
    protected GenieConfig genieConfig;
    @Autowired
    private AgentHandlerFactory agentHandlerFactory;
    @Autowired
    private IGptProcessService gptProcessService;

    /**
     * 开启SSE心跳
     * @param emitter
     * @param requestId
     * @return
     */
    private ScheduledFuture<?> startHeartbeat(SseEmitter emitter, String requestId) {
        return executor.scheduleAtFixedRate(() -> {
            try {
                // 发送心跳消息
                log.info("{} send heartbeat", requestId);
                emitter.send("heartbeat");
            } catch (Exception e) {
                // 发送心跳失败，关闭连接
                log.error("{} heartbeat failed, closing connection", requestId, e);
                emitter.completeWithError(e);
            }
        }, HEARTBEAT_INTERVAL, HEARTBEAT_INTERVAL, TimeUnit.MILLISECONDS);
    }

    /**
     * 注册SSE事件
     * @param emitter
     * @param requestId
     * @param heartbeatFuture
     */
    private void registerSSEMonitor(SseEmitter emitter, String requestId, ScheduledFuture<?> heartbeatFuture) {
        // 监听SSE异常事件
        emitter.onCompletion(() -> {
            log.info("{} SSE connection completed normally", requestId);
            heartbeatFuture.cancel(true);
        });

        // 监听连接超时事件
        emitter.onTimeout(() -> {
            log.info("{} SSE connection timed out", requestId);
            heartbeatFuture.cancel(true);
            emitter.complete();
        });

        // 监听连接错误事件
        emitter.onError((ex) -> {
            log.info("{} SSE connection error: ", requestId, ex);
            heartbeatFuture.cancel(true);
            emitter.completeWithError(ex);
        });
    }

    /**
     * 执行智能体调度
     * @param request
     * @return
     * @throws UnsupportedEncodingException
     */
    @PostMapping("/AutoAgent")
    public SseEmitter AutoAgent(@RequestBody AgentRequest request) throws UnsupportedEncodingException {

        log.info("{} auto agent request: {}", request.getRequestId(), JSON.toJSONString(request));

        Long AUTO_AGENT_SSE_TIMEOUT = 60 * 60 * 1000L;

        SseEmitter emitter = new SseEmitter(AUTO_AGENT_SSE_TIMEOUT);
        // SSE心跳
        ScheduledFuture<?> heartbeatFuture = startHeartbeat(emitter, request.getRequestId());
        // 监听SSE事件
        registerSSEMonitor(emitter, request.getRequestId(), heartbeatFuture);
        // 拼接输出类型
        request.setQuery(handleOutputStyle(request));
        // 执行调度引擎
        ThreadUtil.execute(() -> {
            try {
                Printer printer = new SSEPrinter(emitter, request, request.getAgentType());
                AgentContext agentContext = AgentContext.builder()
                        .requestId(request.getRequestId())
                        .sessionId(request.getRequestId())
                        .printer(printer)
                        .query(request.getQuery())
                        .task("")
                        .dateInfo(DateUtil.CurrentDateInfo())
                        .productFiles(new ArrayList<>())
                        .taskProductFiles(new ArrayList<>())
                        .sopPrompt(request.getSopPrompt())
                        .basePrompt(request.getBasePrompt())
                        .agentType(request.getAgentType())
                        .isStream(Objects.nonNull(request.getIsStream()) ? request.getIsStream() : false)
                        .build();

                // 构建工具列表
                agentContext.setToolCollection(buildToolCollection(agentContext, request));
                // 根据数据类型获取对应的处理器
                AgentHandlerService handler = agentHandlerFactory.getHandler(agentContext, request);
                // 执行处理逻辑
                handler.handle(agentContext, request);
                // 关闭连接
                emitter.complete();

            } catch (Exception e) {
                log.error("{} auto agent error", request.getRequestId(), e);
            }
        });

        return emitter;
    }


    /**
     * html模式： query+以 html展示
     * docs模式：query+以 markdown展示
     * table 模式: query+以 excel 展示
     */
    private String handleOutputStyle(AgentRequest request) {
        String query = request.getQuery();
        Map<String, String> outputStyleMap = genieConfig.getOutputStylePrompts();
        if (!StringUtils.isEmpty(request.getOutputStyle())) {
            query += outputStyleMap.computeIfAbsent(request.getOutputStyle(), k -> "");
        }
        return query;
    }


    /**
     * 构建工具列表
     *
     * @param agentContext
     * @param request
     * @return
     */
    private ToolCollection buildToolCollection(AgentContext agentContext, AgentRequest request) {

        ToolCollection toolCollection = new ToolCollection();
        toolCollection.setAgentContext(agentContext);
        // file
        FileTool fileTool = new FileTool();
        fileTool.setAgentContext(agentContext);
        toolCollection.addTool(fileTool);

        // default tool
        List<String> agentToolList = Arrays.asList(genieConfig.getMultiAgentToolListMap()
                .getOrDefault("default", "search,code,report").split(","));
        if (!agentToolList.isEmpty()) {
            if (agentToolList.contains("code")) {
                CodeInterpreterTool codeTool = new CodeInterpreterTool();
                codeTool.setAgentContext(agentContext);
                toolCollection.addTool(codeTool);
            }
            if (agentToolList.contains("report")) {
                ReportTool htmlTool = new ReportTool();
                htmlTool.setAgentContext(agentContext);
                toolCollection.addTool(htmlTool);
            }
            if (agentToolList.contains("search")) {
                DeepSearchTool deepSearchTool = new DeepSearchTool();
                deepSearchTool.setAgentContext(agentContext);
                toolCollection.addTool(deepSearchTool);
            }
        }

        // mcp tool
        try {
            McpTool mcpTool = new McpTool();
            mcpTool.setAgentContext(agentContext);
            for (String mcpServer : genieConfig.getMcpServerUrlArr()) {
                String listToolResult = mcpTool.listTool(mcpServer);
                if (listToolResult.isEmpty()) {
                    log.error("{} mcp server {} invalid", agentContext.getRequestId(), mcpServer);
                    continue;
                }

                JSONObject resp = JSON.parseObject(listToolResult);
                if (resp.getIntValue("code") != 200) {
                    log.error("{} mcp serve {} code: {}, message: {}", agentContext.getRequestId(), mcpServer,
                            resp.getIntValue("code"), resp.getString("message"));
                    continue;
                }
                JSONArray data = resp.getJSONArray("data");
                if (data.isEmpty()) {
                    log.error("{} mcp serve {} code: {}, message: {}", agentContext.getRequestId(), mcpServer,
                            resp.getIntValue("code"), resp.getString("message"));
                    continue;
                }
                for (int i = 0; i < data.size(); i++) {
                    JSONObject tool = data.getJSONObject(i);
                    String method = tool.getString("name");
                    String description = tool.getString("description");
                    String inputSchema = tool.getString("inputSchema");
                    toolCollection.addMcpTool(method, description, inputSchema, mcpServer);
                }
            }
        } catch (Exception e) {
            log.error("{} add mcp tool failed", agentContext.getRequestId(), e);
        }

        return toolCollection;
    }

    /**
     * 探活接口
     *
     * @return
     */
    @RequestMapping(value = "/web/health", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("ok");
    }


    /**
     * 处理Agent流式增量查询请求，返回SSE事件流
     * @param params 查询请求参数对象，包含GPT查询所需信息
     * @return 返回SSE事件发射器，用于流式传输增量响应结果
     */
    @RequestMapping(value = "/web/api/v1/gpt/queryAgentStreamIncr", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter queryAgentStreamIncr(@RequestBody GptQueryReq params) {
        return gptProcessService.queryMultiAgentIncrStream(params);
    }

    /**
     * 获取所有可用的LLM模型列表
     * @return 模型列表
     */
    @GetMapping("/api/llm/models")
    public ResponseEntity<List<LLMModelInfo>> getAllModels() {
        try {
            Map<String, com.jd.genie.agent.llm.LLMSettings> allModels = genieConfig.getAllAvailableModels();
            String currentModel = genieConfig.getCurrentModelName();
            
            List<LLMModelInfo> modelInfoList = new ArrayList<>();
            
            // 添加默认模型（如果不在settings中）
            if (!allModels.containsKey(currentModel)) {
                modelInfoList.add(LLMModelInfo.builder()
                        .modelKey(currentModel)
                        .displayName(getDisplayName(currentModel))
                        .description("默认模型")
                        .isCurrent(true)
                        .available(true)
                        .modelType(getModelType(currentModel))
                        .build());
            }
            
            // 添加配置中的模型
            for (Map.Entry<String, com.jd.genie.agent.llm.LLMSettings> entry : allModels.entrySet()) {
                String modelKey = entry.getKey();
                com.jd.genie.agent.llm.LLMSettings settings = entry.getValue();
                
                modelInfoList.add(LLMModelInfo.builder()
                        .modelKey(modelKey)
                        .displayName(getDisplayName(modelKey))
                        .description("支持" + settings.getMaxTokens() + "个token")
                        .isCurrent(modelKey.equals(currentModel))
                        .available(true)
                        .maxTokens(settings.getMaxTokens())
                        .modelType(getModelType(modelKey))
                        .build());
            }
            
            return ResponseEntity.ok(modelInfoList);
        } catch (Exception e) {
            log.error("获取LLM模型列表失败", e);
            return ResponseEntity.ok(new ArrayList<>());
        }
    }

    /**
     * 获取当前使用的LLM模型
     * @return 当前模型信息
     */
    @GetMapping("/api/llm/current")
    public ResponseEntity<Map<String, String>> getCurrentModel() {
        try {
            String currentModel = genieConfig.getCurrentModelName();
            Map<String, String> result = new HashMap<>();
            result.put("currentModel", currentModel);
            result.put("displayName", getDisplayName(currentModel));
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            log.error("获取当前LLM模型失败", e);
            return ResponseEntity.internalServerError().build();
        }
    }

    /**
     * 切换LLM模型
     * @param request 切换请求
     * @return 切换结果
     */
    @PostMapping("/api/llm/switch")
    public ResponseEntity<Map<String, Object>> switchModel(@RequestBody LLMSwitchRequest request) {
        try {
            String modelName = request.getModelName();
            if (StringUtils.isEmpty(modelName)) {
                Map<String, Object> errorResult = new HashMap<>();
                errorResult.put("success", false);
                errorResult.put("message", "模型名称不能为空");
                return ResponseEntity.badRequest().body(errorResult);
            }

            // 验证模型是否存在
            if (!genieConfig.isModelAvailable(modelName) && !modelName.equals(genieConfig.getDefaultModelName())) {
                Map<String, Object> errorResult = new HashMap<>();
                errorResult.put("success", false);
                errorResult.put("message", "指定的模型不存在或不可用");
                return ResponseEntity.badRequest().body(errorResult);
            }

            // 切换模型
            genieConfig.setCurrentModelName(modelName);
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("message", "模型切换成功");
            result.put("currentModel", modelName);
            result.put("displayName", getDisplayName(modelName));
            
            log.info("LLM模型已切换到: {}", modelName);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            log.error("切换LLM模型失败", e);
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("message", "切换失败: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResult);
        }
    }

    /**
     * 根据模型key获取显示名称
     */
    private String getDisplayName(String modelKey) {
        if (modelKey.contains("gpt-4")) {
            return "GPT-4";
        } else if (modelKey.contains("gpt-3.5")) {
            return "GPT-3.5";
        } else if (modelKey.contains("claude")) {
            return "Claude";
        } else if (modelKey.contains("gemini")) {
            return "Gemini";
        } else {
            return modelKey.toUpperCase();
        }
    }

    /**
     * 根据模型key获取模型类型
     */
    private String getModelType(String modelKey) {
        if (modelKey.contains("gpt")) {
            return "OpenAI GPT";
        } else if (modelKey.contains("claude")) {
            return "Anthropic Claude";
        } else if (modelKey.contains("gemini")) {
            return "Google Gemini";
        } else {
            return "Other";
        }
    }

}
    