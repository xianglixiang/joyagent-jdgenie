import React, { useState } from 'react';
import { 
  Modal, 
  Input, 
  Button, 
  Select, 
  Card, 
  Empty, 
  List, 
  Tag, 
  Slider, 
  Form,
  Row,
  Col,
  Divider,
  Spin,
  message
} from 'antd';
import { Search, Database, FileText, Target } from 'lucide-react';
import { Dataset, Chunk, searchApi } from '@/services/knowledge';

const { TextArea } = Input;

interface SearchModalProps {
  visible: boolean;
  datasets: Dataset[];
  onCancel: () => void;
}

const SearchModal: React.FC<SearchModalProps> = ({
  visible,
  datasets,
  onCancel,
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<Chunk[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchTime, setSearchTime] = useState<number>(0);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    try {
      setLoading(true);
      setHasSearched(true);
      const values = await form.validateFields();
      setSearchQuery(values.query);
      
      const startTime = Date.now();
      
      const response = await searchApi.search({
        query: values.query,
        dataset_id: values.dataset_id,
        top_k: values.top_k || 10,
        similarity_threshold: values.similarity_threshold || 0.1,
      });

      const endTime = Date.now();
      setSearchTime(endTime - startTime);

      if (response.data?.success) {
        setResults(response.data.data?.chunks || []);
      } else {
        message.error(response.data?.message || '搜索失败');
        setResults([]);
      }
    } catch (error: any) {
      console.error('搜索失败:', error);
      if (error.errorFields) {
        return;
      }
      message.error('搜索失败');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    form.resetFields();
    setResults([]);
    setSearchQuery('');
    setHasSearched(false);
    setSearchTime(0);
  };

  const handleCancel = () => {
    handleReset();
    onCancel();
  };

  const highlightText = (text: string, query: string) => {
    if (!query) return text;
    
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <span key={index} className="bg-yellow-200 font-semibold">
          {part}
        </span>
      ) : part
    );
  };

  const formatSimilarity = (similarity?: number) => {
    if (similarity === undefined) return '-';
    const percentage = Math.round(similarity * 100);
    let color = 'default';
    
    if (percentage >= 80) color = 'green';
    else if (percentage >= 60) color = 'orange';
    else color = 'red';
    
    return <Tag color={color}>{percentage}%</Tag>;
  };

  return (
    <Modal
      title={
        <div className="flex items-center">
          <Search className="w-20 h-20 text-blue-500 mr-8" />
          <span>知识检索</span>
        </div>
      }
      open={visible}
      onCancel={handleCancel}
      width={1200}
      footer={null}
      destroyOnClose
    >
      <div className="space-y-24">
        {/* 搜索表单 */}
        <Card title="检索设置" size="small">
          <Form
            form={form}
            layout="vertical"
            initialValues={{
              top_k: 10,
              similarity_threshold: 0.1,
            }}
          >
            <Row gutter={16}>
              <Col span={24}>
                <Form.Item
                  name="query"
                  label="搜索内容"
                  rules={[{ required: true, message: '请输入搜索内容' }]}
                >
                  <TextArea
                    placeholder="请输入要搜索的内容..."
                    rows={3}
                    maxLength={500}
                    showCount
                  />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={8}>
                <Form.Item
                  name="dataset_id"
                  label="数据集"
                >
                  <Select placeholder="选择数据集（可选，留空则搜索所有）" allowClear>
                    {datasets.map(dataset => (
                      <Select.Option key={dataset.id} value={dataset.id}>
                        <div className="flex items-center">
                          <Database className="w-14 h-14 mr-4" />
                          {dataset.name}
                        </div>
                      </Select.Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>

              <Col span={8}>
                <Form.Item
                  name="top_k"
                  label="返回结果数"
                  tooltip="最多返回多少条相关结果"
                >
                  <Slider
                    min={1}
                    max={50}
                    marks={{
                      1: '1',
                      10: '10',
                      25: '25',
                      50: '50'
                    }}
                  />
                </Form.Item>
              </Col>

              <Col span={8}>
                <Form.Item
                  name="similarity_threshold"
                  label="相似度阈值"
                  tooltip="过滤掉相似度低于此阈值的结果"
                >
                  <Slider
                    min={0}
                    max={1}
                    step={0.1}
                    marks={{
                      0: '0%',
                      0.5: '50%',
                      1: '100%'
                    }}
                    tooltip={{
                      formatter: (value) => `${Math.round((value || 0) * 100)}%`
                    }}
                  />
                </Form.Item>
              </Col>
            </Row>

            <div className="flex justify-center space-x-16">
              <Button
                type="primary"
                size="large"
                icon={<Search className="w-16 h-16" />}
                onClick={handleSearch}
                loading={loading}
              >
                开始搜索
              </Button>
              <Button size="large" onClick={handleReset}>
                重置
              </Button>
            </div>
          </Form>
        </Card>

        {/* 搜索结果 */}
        {hasSearched && (
          <Card 
            title={
              <div className="flex items-center justify-between">
                <span>搜索结果</span>
                <div className="text-14 font-normal text-gray-500">
                  {loading ? (
                    <Spin size="small" />
                  ) : (
                    <>
                      找到 {results.length} 条结果
                      {searchTime > 0 && ` • 用时 ${searchTime}ms`}
                      {searchQuery && (
                        <>
                          {' • 关键词: '}
                          <Tag color="blue">{searchQuery}</Tag>
                        </>
                      )}
                    </>
                  )}
                </div>
              </div>
            }
            size="small"
          >
            {loading ? (
              <div className="text-center py-40">
                <Spin size="large" />
                <p className="mt-16 text-gray-500">正在搜索...</p>
              </div>
            ) : results.length === 0 ? (
              <Empty
                image={<Target className="w-64 h-64 text-gray-300 mx-auto" />}
                description={
                  <div>
                    <p className="text-gray-500">没有找到相关内容</p>
                    <p className="text-12 text-gray-400 mt-4">
                      试试调整搜索关键词或降低相似度阈值
                    </p>
                  </div>
                }
              />
            ) : (
              <List
                itemLayout="vertical"
                dataSource={results}
                renderItem={(item, index) => (
                  <List.Item
                    key={item.id}
                    className="border-b border-gray-100 last:border-b-0"
                  >
                    <div className="space-y-8">
                      {/* 头部信息 */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-8">
                          <span className="bg-blue-100 text-blue-600 px-6 py-2 rounded text-12 font-medium">
                            #{index + 1}
                          </span>
                          <FileText className="w-14 h-14 text-gray-400" />
                          <span className="text-12 text-gray-500">
                            文档ID: {item.document_id}
                          </span>
                          {item.similarity !== undefined && (
                            <>
                              <Divider type="vertical" />
                              <div className="flex items-center space-x-4">
                                <span className="text-12 text-gray-500">相似度:</span>
                                {formatSimilarity(item.similarity)}
                              </div>
                            </>
                          )}
                        </div>
                      </div>

                      {/* 内容 */}
                      <div className="bg-gray-50 p-16 rounded-8">
                        <p className="text-14 leading-6 text-gray-900">
                          {highlightText(item.content, searchQuery)}
                        </p>
                      </div>

                      {/* 关键词 */}
                      {item.important_keywords && item.important_keywords.length > 0 && (
                        <div className="flex items-center space-x-8">
                          <span className="text-12 text-gray-500">关键词:</span>
                          <div className="flex flex-wrap gap-4">
                            {item.important_keywords.map((keyword, idx) => (
                              <Tag key={idx} size="small" color="geekblue">
                                {keyword}
                              </Tag>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </List.Item>
                )}
              />
            )}
          </Card>
        )}
      </div>
    </Modal>
  );
};

export default SearchModal;