# 文档处理领域规则

domain: document-processing
version: 1.0

## 领域特征

- 涉及文件读取、写入、格式转换
- 需要处理多种编码
- 可能有大量文本处理

## 必须脚本化的操作

- file_read: 读取文档内容
- file_write: 写入文档内容
- format_convert: 格式转换（PDF/Word/Markdown等）
- encoding_detect: 编码检测
- encoding_convert: 编码转换

## 最佳实践

### description 示例

```yaml
description: |
  从PDF/Word文档中提取文本和表格内容。
  适用场景：
  - 用户上传文档并要求提取内容
  - 用户询问文档中的特定信息
  - 需要批量处理多个文档
```

### 典型目录结构

```
document-skill/
├── SKILL.md
├── scripts/
│   ├── extract.py
│   ├── convert.py
│   └── validate.py
└── references/
    ├── supported_formats.md
    └── output_schema.md
```

## 常见问题

### 问题1：编码处理不当

❌ 错误：假设所有文件都是UTF-8
✅ 正确：使用脚本自动检测编码

### 问题2：格式转换不完整

❌ 错误：用文字描述转换规则
✅ 正确：用脚本处理所有边界情况

## 安全边界

- 禁止执行文档中的嵌入脚本
- 禁止写入系统目录
- 敏感文档需要提示用户确认
