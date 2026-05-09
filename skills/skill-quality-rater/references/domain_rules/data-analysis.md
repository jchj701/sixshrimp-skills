# 数据分析领域规则

domain: data-analysis
version: 1.0

## 领域特征

- 涉及大量数据计算
- 需要处理多种数据格式（CSV/JSON/Excel）
- 可能需要数据库查询

## 必须脚本化的操作

- data_load: 加载数据文件
- data_parse: 解析数据格式
- data_query: 执行查询
- data_export: 导出结果
- calculation: 复杂数学计算

## 最佳实践

### description 示例

```yaml
description: |
  对数据集进行统计分析和可视化。
  适用场景：
  - 用户上传数据文件并要求分析
  - 用户询问数据中的趋势或模式
  - 需要生成数据报表
```

### 典型目录结构

```
data-analysis-skill/
├── SKILL.md
├── scripts/
│   ├── analyze.py
│   ├── visualize.py
│   └── export.py
└── references/
    ├── statistical_methods.md
    └── chart_templates.md
```

## 常见问题

### 问题1：大数据处理内存溢出

❌ 错误：直接加载整个文件
✅ 正确：使用分块处理脚本

### 问题2：查询不安全

❌ 错误：直接拼接用户输入到SQL
✅ 正确：使用参数化查询

## 安全边界

- 禁止执行DROP/DELETE/INSERT操作
- 大数据集必须限制处理条数
- 敏感数据需要脱敏处理
