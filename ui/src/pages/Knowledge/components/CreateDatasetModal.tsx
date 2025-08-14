import React from 'react';
import { Modal, Form, Input, Select, message } from 'antd';
import { datasetApi } from '@/services/knowledge';

const { TextArea } = Input;

interface CreateDatasetModalProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: () => void;
}

const CreateDatasetModal: React.FC<CreateDatasetModalProps> = ({
  visible,
  onCancel,
  onSuccess,
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = React.useState(false);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const values = await form.validateFields();
      
      const response = await datasetApi.create({
        name: values.name,
        description: values.description || '',
        embedding_model: values.embedding_model || 'text-embedding-3-small',
      });

      if (response.data?.success) {
        message.success('数据集创建成功');
        form.resetFields();
        onSuccess();
        onCancel();
      } else {
        message.error(response.data?.message || '创建失败');
      }
    } catch (error: any) {
      console.error('创建数据集失败:', error);
      if (error.errorFields) {
        // 表单验证错误
        return;
      }
      message.error('创建失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    form.resetFields();
    onCancel();
  };

  return (
    <Modal
      title="创建数据集"
      open={visible}
      onOk={handleSubmit}
      onCancel={handleCancel}
      confirmLoading={loading}
      width={600}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          embedding_model: 'text-embedding-3-small',
        }}
      >
        <Form.Item
          name="name"
          label="数据集名称"
          rules={[
            { required: true, message: '请输入数据集名称' },
            { max: 50, message: '名称不能超过50个字符' },
          ]}
        >
          <Input
            placeholder="请输入数据集名称"
            maxLength={50}
            showCount
          />
        </Form.Item>

        <Form.Item
          name="description"
          label="描述"
          rules={[
            { max: 200, message: '描述不能超过200个字符' },
          ]}
        >
          <TextArea
            placeholder="请输入数据集描述（可选）"
            maxLength={200}
            showCount
            rows={4}
          />
        </Form.Item>

        <Form.Item
          name="embedding_model"
          label="嵌入模型"
          rules={[{ required: true, message: '请选择嵌入模型' }]}
        >
          <Select placeholder="选择嵌入模型">
            <Select.Option value="text-embedding-3-small">
              text-embedding-3-small
            </Select.Option>
            <Select.Option value="text-embedding-3-large">
              text-embedding-3-large
            </Select.Option>
            <Select.Option value="text-embedding-ada-002">
              text-embedding-ada-002
            </Select.Option>
            <Select.Option value="bge-large-zh-v1.5">
              bge-large-zh-v1.5
            </Select.Option>
            <Select.Option value="bge-base-zh-v1.5">
              bge-base-zh-v1.5
            </Select.Option>
          </Select>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default CreateDatasetModal;