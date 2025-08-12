import React, { memo, useEffect, useState } from 'react';
import { Select, message, Tooltip } from 'antd';
import { Brain } from 'lucide-react';
import classNames from 'classnames';
import { agentApi } from '@/services/agent';
import './index.css';

interface LLMModel {
  modelKey: string;
  displayName: string;
  description: string;
  isCurrent: boolean;
  available: boolean;
  maxTokens?: number;
  modelType: string;
}

interface LLMSelectorProps {
  className?: string;
}

const LLMSelector: React.FC<LLMSelectorProps> = memo(({ className }) => {
  const [models, setModels] = useState<LLMModel[]>([]);
  const [currentModel, setCurrentModel] = useState<string>('');
  const [loading, setLoading] = useState(false);

  // 加载可用模型列表
  const loadModels = async () => {
    try {
      const modelList: LLMModel[] = await agentApi.getAllModels();
      console.log('API Response:', modelList); // 调试日志
      
      setModels(modelList || []);
      
      // 设置当前选中的模型
      const current = modelList.find(model => model.isCurrent);
      if (current) {
        setCurrentModel(current.modelKey);
      }
    } catch (error) {
      console.error('Error loading models:', error);
      message.error('加载模型列表失败，请检查后端服务是否启动');
    }
  };

  // 切换模型
  const switchModel = async (modelKey: string) => {
    if (modelKey === currentModel) {
      return;
    }

    setLoading(true);
    try {
      const result = await agentApi.switchModel(modelKey);
      
      if (result.success) {
        setCurrentModel(modelKey);
        // 更新模型列表中的当前状态
        setModels(prev => prev.map(model => ({
          ...model,
          isCurrent: model.modelKey === modelKey
        })));
        message.success(`已切换到 ${result.displayName}`);
      } else {
        message.error(result.message || '切换失败');
      }
    } catch (error) {
      console.error('Error switching model:', error);
      message.error('切换模型时发生错误');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadModels();
  }, []);

  // 自定义选项渲染
  const renderOption = (model: LLMModel) => (
    <div className="flex items-center justify-between py-2">
      <div className="flex items-center">
        <Brain className="w-4 h-4 mr-2 text-blue-500" />
        <div>
          <div className="font-medium text-gray-900">{model.displayName}</div>
          <div className="text-xs text-gray-500">{model.description}</div>
        </div>
      </div>
      {model.isCurrent && (
        <div className="current-model-badge">当前</div>
      )}
    </div>
  );

  return (
    <div className={classNames('flex items-center', className)}>
      <Tooltip title="选择LLM模型">
        <div className="flex items-center mr-2">
          <Brain className="w-4 h-4 text-gray-600" />
          <span className="text-sm text-gray-600 ml-1 mr-2">模型:</span>
        </div>
      </Tooltip>
      
      <Select
        value={currentModel}
        onChange={switchModel}
        loading={loading}
        placeholder="选择模型"
        className="min-w-160"
        size="middle"
        optionLabelProp="label"
      >
        {models.map((model) => (
          <Select.Option
            key={model.modelKey}
            value={model.modelKey}
            label={model.displayName}
            disabled={!model.available}
          >
            {renderOption(model)}
          </Select.Option>
        ))}
      </Select>
    </div>
  );
});

LLMSelector.displayName = 'LLMSelector';

export default LLMSelector;