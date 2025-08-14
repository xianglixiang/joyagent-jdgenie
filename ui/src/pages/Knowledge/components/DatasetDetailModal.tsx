import React, { useState, useEffect } from 'react';
import { 
  Modal, 
  Tabs, 
  Card, 
  Table, 
  Button, 
  Space, 
  message, 
  Tooltip, 
  Tag, 
  Upload, 
  Input,
  Empty,
  Statistic,
  Row,
  Col,
  Progress
} from 'antd';
import { 
  FileText, 
  Upload as UploadIcon, 
  Trash2, 
  Download, 
  Eye, 
  Search,
  BarChart3,
  Database,
  Clock
} from 'lucide-react';
import type { ColumnsType } from 'antd/es/table';
import type { UploadProps } from 'antd';
import { Dataset, Document, documentApi } from '@/services/knowledge';

const { TabPane } = Tabs;
const { Search: SearchInput } = Input;

interface DatasetDetailModalProps {
  visible: boolean;
  dataset: Dataset | null;
  onCancel: () => void;
  onUpdate: () => void;
}

const DatasetDetailModal: React.FC<DatasetDetailModalProps> = ({
  visible,
  dataset,
  onCancel,
  onUpdate,
}) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [stats, setStats] = useState({
    document_count: 0,
    chunk_count: 0,
    avg_chunks_per_doc: 0,
  });

  // 加载文档列表
  const loadDocuments = async (page = 1, size = 10, keyword = '') => {
    if (!dataset) return;

    try {
      setLoading(true);
      const response = await documentApi.list(dataset.id, {
        page,
        page_size: size,
        keywords: keyword || undefined,
      });

      if (response.data?.success) {
        const docs = response.data.data?.documents || [];
        setDocuments(docs);
        setTotal(response.data.data?.total || 0);
        
        // 计算统计信息
        const docCount = docs.length;
        const chunkCount = docs.reduce((sum, doc) => sum + (doc.chunk_count || 0), 0);
        setStats({
          document_count: docCount,
          chunk_count: chunkCount,
          avg_chunks_per_doc: docCount > 0 ? Math.round(chunkCount / docCount) : 0,
        });
      } else {
        message.error(response.data?.message || '加载文档列表失败');
      }
    } catch (error) {
      console.error('加载文档列表失败:', error);
      message.error('加载文档列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (visible && dataset) {
      setCurrentPage(1);
      setSearchKeyword('');
      loadDocuments();
    }
  }, [visible, dataset]);

  // 搜索处理
  const handleSearch = (value: string) => {
    setSearchKeyword(value);
    setCurrentPage(1);
    loadDocuments(1, pageSize, value);
  };

  // 分页处理
  const handlePageChange = (page: number, size?: number) => {
    setCurrentPage(page);
    if (size) setPageSize(size);
    loadDocuments(page, size || pageSize, searchKeyword);
  };

  // 删除文档
  const handleDeleteDocument = async (document: Document) => {
    if (!dataset) return;

    Modal.confirm({
      title: '确认删除',
      content: `确定要删除文档"${document.name}"吗？此操作不可恢复。`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          const response = await documentApi.delete(dataset.id, document.id);
          if (response.data?.success) {
            message.success('删除成功');
            loadDocuments(currentPage, pageSize, searchKeyword);
            onUpdate(); // 更新上级组件数据
          } else {
            message.error(response.data?.message || '删除失败');
          }
        } catch (error) {
          console.error('删除失败:', error);
          message.error('删除失败');
        }
      },
    });
  };

  // 文件上传配置
  const uploadProps: UploadProps = {
    name: 'file',
    multiple: true,
    showUploadList: false,
    beforeUpload: (file) => {
      // 检查文件类型
      const allowedTypes = [
        'text/plain',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/markdown',
      ];
      
      if (!allowedTypes.includes(file.type)) {
        message.error('只支持 TXT、PDF、DOC、DOCX、MD 格式的文件');
        return false;
      }

      // 检查文件大小 (10MB)
      if (file.size > 10 * 1024 * 1024) {
        message.error('文件大小不能超过 10MB');
        return false;
      }

      handleUpload(file);
      return false; // 阻止自动上传
    },
  };

  // 处理文件上传
  const handleUpload = async (file: File) => {
    if (!dataset) return;

    try {
      setUploadLoading(true);
      
      // 这里简化处理，实际应该上传文件到服务器并获取路径
      const response = await documentApi.upload(dataset.id, {
        file_path: file.name, // 实际应该是上传后的文件路径
        name: file.name,
      });

      if (response.data?.success) {
        message.success('上传成功');
        loadDocuments(currentPage, pageSize, searchKeyword);
        onUpdate();
      } else {
        message.error(response.data?.message || '上传失败');
      }
    } catch (error) {
      console.error('上传失败:', error);
      message.error('上传失败');
    } finally {
      setUploadLoading(false);
    }
  };

  // 文档状态渲染
  const renderStatus = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      'processing': { color: 'processing', text: '处理中' },
      'completed': { color: 'success', text: '已完成' },
      'failed': { color: 'error', text: '失败' },
      'pending': { color: 'default', text: '待处理' },
    };
    
    const { color, text } = statusMap[status] || { color: 'default', text: status };
    return <Tag color={color}>{text}</Tag>;
  };

  // 文档表格列定义
  const columns: ColumnsType<Document> = [
    {
      title: '文档名称',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
      render: (text, record) => (
        <div className="flex items-center">
          <FileText className="w-16 h-16 text-blue-500 mr-8" />
          <div>
            <div className="font-medium text-gray-900">{text}</div>
            <div className="text-12 text-gray-500 mt-2">
              {record.type} • {record.size}
            </div>
          </div>
        </div>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: renderStatus,
    },
    {
      title: '块数',
      dataIndex: 'chunk_count',
      key: 'chunk_count',
      width: 80,
      align: 'center',
      render: (count) => <span className="font-medium">{count || 0}</span>,
    },
    {
      title: '上传时间',
      dataIndex: 'create_time',
      key: 'create_time',
      width: 160,
      render: (time) => time ? new Date(time).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      align: 'center',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看">
            <Button
              type="text"
              size="small"
              icon={<Eye className="w-14 h-14" />}
            />
          </Tooltip>
          <Tooltip title="删除">
            <Button
              type="text"
              size="small"
              danger
              icon={<Trash2 className="w-14 h-14" />}
              onClick={() => handleDeleteDocument(record)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  if (!dataset) return null;

  return (
    <Modal
      title={
        <div className="flex items-center">
          <Database className="w-20 h-20 text-blue-500 mr-8" />
          <span>{dataset.name}</span>
        </div>
      }
      open={visible}
      onCancel={onCancel}
      width={1000}
      footer={null}
      destroyOnClose
    >
      <Tabs defaultActiveKey="overview">
        <TabPane
          tab={
            <span className="flex items-center">
              <BarChart3 className="w-16 h-16 mr-4" />
              概览
            </span>
          }
          key="overview"
        >
          <div className="space-y-16">
            {/* 基本信息 */}
            <Card title="基本信息" size="small">
              <Row gutter={16}>
                <Col span={12}>
                  <p><strong>名称:</strong> {dataset.name}</p>
                  <p><strong>描述:</strong> {dataset.description || '无'}</p>
                </Col>
                <Col span={12}>
                  <p><strong>嵌入模型:</strong> <Tag color="blue">{dataset.embedding_model}</Tag></p>
                  <p><strong>创建时间:</strong> {dataset.create_time ? new Date(dataset.create_time).toLocaleString() : '-'}</p>
                </Col>
              </Row>
            </Card>

            {/* 统计信息 */}
            <Card title="统计信息" size="small">
              <Row gutter={16}>
                <Col span={8}>
                  <Statistic
                    title="文档数量"
                    value={dataset.document_count || 0}
                    prefix={<FileText className="w-16 h-16 text-blue-500" />}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="总块数"
                    value={dataset.chunk_count || 0}
                    prefix={<Database className="w-16 h-16 text-green-500" />}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="平均块数/文档"
                    value={stats.avg_chunks_per_doc}
                    prefix={<BarChart3 className="w-16 h-16 text-purple-500" />}
                  />
                </Col>
              </Row>
            </Card>
          </div>
        </TabPane>

        <TabPane
          tab={
            <span className="flex items-center">
              <FileText className="w-16 h-16 mr-4" />
              文档管理
            </span>
          }
          key="documents"
        >
          <div className="space-y-16">
            {/* 操作栏 */}
            <div className="flex items-center justify-between">
              <SearchInput
                placeholder="搜索文档..."
                onSearch={handleSearch}
                className="w-300"
                allowClear
              />
              
              <Upload {...uploadProps}>
                <Button
                  type="primary"
                  icon={<UploadIcon className="w-16 h-16" />}
                  loading={uploadLoading}
                >
                  上传文档
                </Button>
              </Upload>
            </div>

            {/* 文档列表 */}
            <Table
              columns={columns}
              dataSource={documents}
              rowKey="id"
              loading={loading}
              pagination={{
                current: currentPage,
                pageSize,
                total,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total, range) => `第 ${range[0]}-${range[1]} 项，共 ${total} 项`,
                onChange: handlePageChange,
                onShowSizeChange: handlePageChange,
              }}
              locale={{
                emptyText: (
                  <Empty
                    image={<FileText className="w-64 h-64 text-gray-300 mx-auto" />}
                    description={
                      <div>
                        <p className="text-gray-500 mb-16">暂无文档</p>
                        <Upload {...uploadProps}>
                          <Button
                            type="primary"
                            icon={<UploadIcon className="w-16 h-16" />}
                            loading={uploadLoading}
                          >
                            上传第一个文档
                          </Button>
                        </Upload>
                      </div>
                    }
                  />
                ),
              }}
            />
          </div>
        </TabPane>
      </Tabs>
    </Modal>
  );
};

export default DatasetDetailModal;