package com.jd.genie.agent.agent;

import com.alibaba.fastjson.JSON;
import com.jd.genie.agent.dto.Message;
import com.jd.genie.agent.dto.tool.ToolCall;
import com.jd.genie.agent.dto.tool.ToolChoice;
import com.jd.genie.agent.enums.AgentState;
import com.jd.genie.agent.enums.RoleType;
import com.jd.genie.agent.llm.LLM;
import com.jd.genie.agent.prompt.ToolCallPrompt;
import com.jd.genie.agent.tool.BaseTool;
import com.jd.genie.agent.util.FileUtil;
import com.jd.genie.agent.util.SpringContextHolder;
import com.jd.genie.config.GenieConfig;
import com.jd.genie.model.response.AgentResponse;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.ApplicationContext;

import java.util.*;
import java.util.concurrent.CompletableFuture;

/**
 * 工具调用代理 - 处理工具/函数调用的基础代理类
 */
@Data
@Slf4j
@EqualsAndHashCode(callSuper = true)
public class ReactImplAgent extends ReActAgent {

    private List<ToolCall> toolCalls;
    private Integer maxObserve;
    private String systemPromptSnapshot;
    private String nextStepPromptSnapshot;

    public ReactImplAgent(AgentContext context) {
        setName("react");
        setDescription("an agent that can execute tool calls.");
        ApplicationContext applicationContext = SpringContextHolder.getApplicationContext();
        GenieConfig genieConfig = applicationContext.getBean(GenieConfig.class);

        StringBuilder toolPrompt = new StringBuilder();
        for (BaseTool tool : context.getToolCollection().getToolMap().values()) {
            toolPrompt.append(String.format("工具名：%s 工具描述：%s\n", tool.getName(), tool.getDescription()));
        }

        String promptKey = "default";
        String nextPromptKey = "default";

        setSystemPrompt(genieConfig.getReactSystemPromptMap().getOrDefault(promptKey, ToolCallPrompt.SYSTEM_PROMPT)
                .replace("{{tools}}", toolPrompt.toString())
                .replace("{{query}}", context.getQuery())
                .replace("{{date}}", context.getDateInfo())
                .replace("{{basePrompt}}", context.getBasePrompt()));
        setNextStepPrompt(genieConfig.getReactNextStepPromptMap().getOrDefault(nextPromptKey, ToolCallPrompt.NEXT_STEP_PROMPT)
                .replace("{{tools}}", toolPrompt.toString())
                .replace("{{query}}", context.getQuery())
                .replace("{{date}}", context.getDateInfo())
                .replace("{{basePrompt}}", context.getBasePrompt()));

        setSystemPromptSnapshot(getSystemPrompt());
        setNextStepPromptSnapshot(getNextStepPrompt());

        setPrinter(context.printer);
        setMaxSteps(genieConfig.getReactMaxSteps());
        setLlm(new LLM(genieConfig.getReactModelName(), ""));
        setContext(context);

        // 初始化工具集合
        availableTools = context.getToolCollection();
        setDigitalEmployeePrompt(genieConfig.getDigitalEmployeePrompt());
    }

    @Override
    public boolean think() {
        // 获取文件内容
        String filesStr = FileUtil.formatFileInfo(context.getProductFiles(), true);
        setSystemPrompt(getSystemPromptSnapshot().replace("{{files}}", filesStr));
        setNextStepPrompt(getNextStepPromptSnapshot().replace("{{files}}", filesStr));

        if (!getMemory().getLastMessage().getRole().equals(RoleType.USER)) {
            Message userMsg = Message.userMessage(getNextStepPrompt(), null);
            getMemory().addMessage(userMsg);
        }
        try {
            // 获取带工具选项的响应
            context.setStreamMessageType("tool_thought");
            
            log.info("{} ReactImplAgent think - available tools: {}", context.getRequestId(), 
                    availableTools.getToolMap().keySet());

            CompletableFuture<LLM.ToolCallResponse> future = getLlm().askTool(
                    context,
                    getMemory().getMessages(),
                    Message.systemMessage(getSystemPrompt(), null),
                    availableTools,
                    ToolChoice.AUTO, null, context.getIsStream(), 300
            );

            LLM.ToolCallResponse response = future.get();
            
            log.info("{} ReactImplAgent think - LLM response content: {}", context.getRequestId(), 
                    response.getContent());
            log.info("{} ReactImplAgent think - Tool calls count: {}", context.getRequestId(), 
                    response.getToolCalls() != null ? response.getToolCalls().size() : 0);

            setToolCalls(response.getToolCalls());

            // 记录响应信息
            if (!context.getIsStream() && response.getContent() != null && !response.getContent().isEmpty()) {
                printer.send("tool_thought", response.getContent());
            }

            // 如果没有工具调用但内容表明任务完成，则继续执行
            if ((response.getToolCalls() == null || response.getToolCalls().isEmpty()) && 
                response.getContent() != null && !response.getContent().isEmpty()) {
                log.info("{} No tool calls generated, checking if task is complete", context.getRequestId());
                
                // 检查是否是完成状态
                String content = response.getContent().toLowerCase();
                if (content.contains("完成") || content.contains("结束") || content.contains("finish")) {
                    setState(AgentState.FINISHED);
                    log.info("{} Task marked as finished based on response content", context.getRequestId());
                }
            }

            // 创建并添加助手消息
            Message assistantMsg = response.getToolCalls() != null && !response.getToolCalls().isEmpty() && !"struct_parse".equals(llm.getFunctionCallType()) ?
                    Message.fromToolCalls(response.getContent(), response.getToolCalls()) :
                    Message.assistantMessage(response.getContent(), null);
            getMemory().addMessage(assistantMsg);

        } catch (Exception e) {
            log.error("{} react think error", context.getRequestId(), e);
            getMemory().addMessage(Message.assistantMessage(
                    "Error encountered while processing: " + e.getMessage(), null));
            setState(AgentState.FINISHED);
            return false;
        }

        return true;
    }

    @Override
    public String act() {

        if (toolCalls == null || toolCalls.isEmpty()) {
            log.info("{} No tool calls to execute, finishing task", context.getRequestId());
            setState(AgentState.FINISHED);
            return getMemory().getLastMessage().getContent();
        }

        log.info("{} Executing {} tool calls", context.getRequestId(), toolCalls.size());
        
        // action
        Map<String, String> toolResults = executeTools(toolCalls);
        List<String> results = new ArrayList<>();
        
        for (ToolCall command : toolCalls) {
            String toolName = command.getFunction().getName();
            String result = toolResults.get(command.getId());
            
            log.info("{} Tool {} executed with result length: {}", context.getRequestId(), 
                    toolName, result != null ? result.length() : 0);
            
            if (!Arrays.asList("code_interpreter", "report_tool", "file_tool", "deep_search").contains(toolName)) {
                printer.send("tool_result", AgentResponse.ToolResult.builder()
                        .toolName(toolName)
                        .toolParam((Map<String, Object>) JSON.parseObject(command.getFunction().getArguments(), Map.class))
                        .toolResult(result)
                        .build(), null);
            }

            if (maxObserve != null && result != null) {
                result = result.substring(0, Math.min(result.length(), maxObserve));
            }

            // 添加工具响应到记忆
            if ("struct_parse".equals(llm.getFunctionCallType())) {
                String content = getMemory().getLastMessage().getContent();
                getMemory().getLastMessage().setContent(content + "\n 工具执行结果为:\n" + result);
            } else { // function_call
                Message toolMsg = Message.toolMessage(
                        result != null ? result : "Tool execution failed",
                        command.getId(),
                        null
                );
                getMemory().addMessage(toolMsg);
            }
            
            if (result != null) {
                results.add(result);
            }
        }

        log.info("{} Tool execution completed, product files count: {}", context.getRequestId(), 
                context.getProductFiles().size());

        return results.isEmpty() ? "Tool execution completed" : String.join("\n\n", results);
    }

    @Override
    public String run(String request) {
        return super.run(request);
    }

}