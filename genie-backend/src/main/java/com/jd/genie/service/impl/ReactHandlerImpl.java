package com.jd.genie.service.impl;

import com.jd.genie.agent.agent.AgentContext;
import com.jd.genie.agent.agent.ReActAgent;
import com.jd.genie.agent.agent.ReactImplAgent;
import com.jd.genie.agent.agent.SummaryAgent;
import com.jd.genie.agent.dto.File;
import com.jd.genie.agent.dto.TaskSummaryResult;
import com.jd.genie.agent.enums.AgentType;
import com.jd.genie.config.GenieConfig;
import com.jd.genie.model.req.AgentRequest;
import com.jd.genie.service.AgentHandlerService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;

import java.util.*;

@Slf4j
@Component
public class ReactHandlerImpl implements AgentHandlerService {

    @Autowired
    private GenieConfig genieConfig;


    @Override
    public String handle(AgentContext agentContext, AgentRequest request) {
        long startTime = System.currentTimeMillis();
        String requestId = agentContext.getRequestId();
        
        log.info("{} ReactHandler starting task execution for query: {}", requestId, request.getQuery());

        ReActAgent executor = new ReactImplAgent(agentContext);
        SummaryAgent summary = new SummaryAgent(agentContext);
        summary.setSystemPrompt(summary.getSystemPrompt().replace("{{query}}", request.getQuery()));

        log.info("{} Starting REACT agent execution", requestId);
        String executorResult = executor.run(request.getQuery());
        log.info("{} REACT agent execution completed in {}ms, result: {}", requestId, 
                System.currentTimeMillis() - startTime, 
                executorResult != null ? executorResult.substring(0, Math.min(100, executorResult.length())) + "..." : "null");
        
        log.info("{} Product files count after execution: {}", requestId, agentContext.getProductFiles().size());
        if (!agentContext.getProductFiles().isEmpty()) {
            agentContext.getProductFiles().forEach(file -> 
                log.info("{} Product file: {} - {}", requestId, file.getFileName(), file.getDescription()));
        }

        log.info("{} Starting task summary generation", requestId);
        TaskSummaryResult result = summary.summaryTaskResult(executor.getMemory().getMessages(), request.getQuery());
        log.info("{} Task summary completed: {}", requestId, result.getTaskSummary().substring(0, Math.min(100, result.getTaskSummary().length())) + "...");

        Map<String, Object> taskResult = new HashMap<>();
        taskResult.put("taskSummary", result.getTaskSummary());

        if (CollectionUtils.isEmpty(result.getFiles())) {
            log.info("{} No files in summary result, checking context files", requestId);
            if (!CollectionUtils.isEmpty(agentContext.getProductFiles())) {
                List<File> fileResponses = agentContext.getProductFiles();
                // 过滤中间搜索结果文件
                fileResponses.removeIf(file -> Objects.nonNull(file) && file.getIsInternalFile());
                Collections.reverse(fileResponses);
                taskResult.put("fileList", fileResponses);
                log.info("{} Added {} files from context to result", requestId, fileResponses.size());
            } else {
                log.warn("{} No files found in context or summary result", requestId);
            }
        } else {
            taskResult.put("fileList", result.getFiles());
            log.info("{} Added {} files from summary result", requestId, result.getFiles().size());
        }

        agentContext.getPrinter().send("result", taskResult);
        log.info("{} ReactHandler completed task in {}ms", requestId, System.currentTimeMillis() - startTime);

        return "";
    }

    @Override
    public Boolean support(AgentContext agentContext, AgentRequest request) {
        return AgentType.REACT.getValue().equals(request.getAgentType());
    }
}
