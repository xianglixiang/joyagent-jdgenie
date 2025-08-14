import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Button, 
  Table, 
  Space, 
  message, 
  Modal, 
  Form, 
  Input, 
  Select,
  Tooltip,
  Tag,
  Empty,
  Spin
} from 'antd';
import { 
  Plus, 
  Database, 
  FileText, 
  Search, 
  Trash2, 
  Eye,
  Edit,
  Upload,
  BarChart3
} from 'lucide-react';
import type { ColumnsType } from 'antd/es/table';
import { Dataset, datasetApi, configApi } from '@/services/knowledge';
import CreateDatasetModal from './components/CreateDatasetModal';
import DatasetDetailModal from './components/DatasetDetailModal';
import SearchModal from './components/SearchModal';

const { TextArea } = Input;

const Knowledge: React.FC = () => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [searchKeyword, setSearchKeyword] = useState('');
  
  // Modal states
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [searchModalVisible, setSearchModalVisible] = useState(false);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  
  // Config state
  const [configValid, setConfigValid] = useState<boolean | null>(null);

  // 加载数据集列表
  const loadDatasets = async (page = 1, size = 10, keyword = '') => {
    try {
      setLoading(true);
      const response = await datasetApi.list({
        page,
        page_size: size,
        name: keyword || undefined,
      });

      if (response.data?.success) {
        setDatasets(response.data.data?.datasets || []);
        setTotal(response.data.data?.total || 0);
      } else {
        message.error(response.data?.message || '加载数据集列表失败');
      }
    } catch (error) {
      console.error('加载数据集列表失败:', error);
      message.error('加载数据集列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 检查配置
  const checkConfig = async () => {
    try {
      const response = await configApi.validateConfig();
      if (response.data?.success) {
        setConfigValid(response.data.data?.config_valid || false);
      }
    } catch (error) {
      console.error('检查配置失败:', error);
      setConfigValid(false);
    }
  };

  useEffect(() => {
    checkConfig();
    loadDatasets();
  }, []);

  // 搜索处理
  const handleSearch = () => {
    setCurrentPage(1);
    loadDatasets(1, pageSize, searchKeyword);
  };

  // 重置搜索
  const handleResetSearch = () => {
    setSearchKeyword('');
    setCurrentPage(1);
    loadDatasets(1, pageSize, '');
  };

  // 分页处理
  const handlePageChange = (page: number, size?: number) => {
    setCurrentPage(page);
    if (size) setPageSize(size);
    loadDatasets(page, size || pageSize, searchKeyword);
  };

  // 删除数据集
  const handleDelete = async (dataset: Dataset) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除数据集"${dataset.name}"吗？此操作不可恢复。`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          const response = await datasetApi.delete(dataset.id);
          if (response.data?.success) {
            message.success('删除成功');
            loadDatasets(currentPage, pageSize, searchKeyword);
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

  // 查看详情
  const handleViewDetail = (dataset: Dataset) => {
    setSelectedDataset(dataset);
    setDetailModalVisible(true);
  };

  // 创建成功回调
  const handleCreateSuccess = () => {
    loadDatasets(currentPage, pageSize, searchKeyword);
  };

  // 表格列定义
  const columns: ColumnsType<Dataset> = [
    {
      title: '数据集名称',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
      render: (text, record) => (
        <div className="flex items-center">
          <Database className="w-16 h-16 text-blue-500 mr-8" />
          <div>
            <div className="font-medium text-gray-900">{text}</div>
            {record.description && (
              <div className="text-12 text-gray-500 mt-2">
                {record.description.length > 50 
                  ? `${record.description.slice(0, 50)}...` 
                  : record.description
                }
              </div>
            )}
          </div>
        </div>
      ),
    },
    {
      title: '模型',
      dataIndex: 'embedding_model',
      key: 'embedding_model',
      width: 150,
      render: (text) => (
        <Tag color="blue">{text}</Tag>
      ),
    },
    {
      title: '文档数',
      dataIndex: 'document_count',
      key: 'document_count',
      width: 100,
      align: 'center',
      render: (count) => (
        <span className="font-medium">{count || 0}</span>
      ),
    },
    {
      title: '块数',
      dataIndex: 'chunk_count',
      key: 'chunk_count',
      width: 100,
      align: 'center',
      render: (count) => (
        <span className="font-medium">{count || 0}</span>
      ),
    },
    {
      title: '权限',
      dataIndex: 'permission',
      key: 'permission',
      width: 80,
      render: (permission) => (
        <Tag color={permission === 'me' ? 'green' : 'orange'}>
          {permission === 'me' ? '私有' : '共享'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
      key: 'create_time',
      width: 160,
      render: (time) => time ? new Date(time).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      align: 'center',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="text"
              size="small"
              icon={<Eye className="w-14 h-14" />}
              onClick={() => handleViewDetail(record)}
            />
          </Tooltip>
          <Tooltip title="统计信息">
            <Button
              type="text"
              size="small"
              icon={<BarChart3 className="w-14 h-14" />}
              onClick={() => handleViewDetail(record)}
            />
          </Tooltip>
          <Tooltip title="删除">
            <Button
              type="text"
              size="small"
              danger
              icon={<Trash2 className="w-14 h-14" />}
              onClick={() => handleDelete(record)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  // 配置无效的提示
  if (configValid === false) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Database className="w-64 h-64 text-gray-300 mx-auto mb-16" />
          <h3 className="text-18 font-medium text-gray-900 mb-8">RAGFlow 配置无效</h3>
          <p className="text-gray-500 mb-16">
            请检查 RAGFlow 服务配置，确保服务正常运行且 API 密钥正确。
          </p>
          <Button type="primary" onClick={checkConfig}>
            重新检查配置
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col p-24">
      {/* 页面标题和操作栏 */}
      <div className="flex items-center justify-between mb-24">
        <div>
          <h1 className="text-24 font-bold text-gray-900 mb-4">知识库管理</h1>
          <p className="text-gray-500">管理您的知识库数据集，上传文档并进行智能检索</p>
        </div>
        
        <Space size="middle">
          <Button
            icon={<Search className="w-16 h-16" />}
            onClick={() => setSearchModalVisible(true)}
          >
            知识检索
          </Button>
          <Button
            type="primary"
            icon={<Plus className="w-16 h-16" />}
            onClick={() => setCreateModalVisible(true)}
          >
            创建数据集
          </Button>
        </Space>
      </div>

      {/* 搜索栏 */}
      <Card className="mb-24">
        <div className="flex items-center space-x-16">
          <Input
            placeholder="搜索数据集名称..."
            value={searchKeyword}
            onChange={(e) => setSearchKeyword(e.target.value)}
            onPressEnter={handleSearch}
            className="flex-1"
            allowClear
          />
          <Button type="primary" onClick={handleSearch}>
            搜索
          </Button>
          <Button onClick={handleResetSearch}>
            重置
          </Button>
        </div>
      </Card>

      {/* 数据集列表 */}
      <Card className="flex-1" bodyStyle={{ padding: 0 }}>
        <Table
          columns={columns}
          dataSource={datasets}
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
                image={<Database className="w-64 h-64 text-gray-300 mx-auto" />}
                description={
                  <div>
                    <p className="text-gray-500 mb-16">暂无数据集</p>
                    <Button
                      type="primary"
                      icon={<Plus className="w-16 h-16" />}
                      onClick={() => setCreateModalVisible(true)}
                    >
                      创建第一个数据集
                    </Button>
                  </div>
                }
              />
            ),
          }}
        />
      </Card>

      {/* 创建数据集模态框 */}
      <CreateDatasetModal
        visible={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        onSuccess={handleCreateSuccess}
      />

      {/* 数据集详情模态框 */}
      <DatasetDetailModal
        visible={detailModalVisible}
        dataset={selectedDataset}
        onCancel={() => {
          setDetailModalVisible(false);
          setSelectedDataset(null);
        }}
        onUpdate={handleCreateSuccess}
      />

      {/* 知识检索模态框 */}
      <SearchModal
        visible={searchModalVisible}
        datasets={datasets}
        onCancel={() => setSearchModalVisible(false)}
      />
    </div>
  );
};

export default Knowledge;