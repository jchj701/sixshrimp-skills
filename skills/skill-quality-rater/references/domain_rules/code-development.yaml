# 代码开发领域规则

domain: code-development
version: 1.0

## 领域特征

- 涉及文件创建、修改
- 需要执行命令
- 可能需要安装依赖

## 必须脚本化的操作

- file_create: 创建文件
- file_modify: 修改文件
- command_run: 执行命令
- dependency_install: 安装依赖
- test_run: 运行测试

## 最佳实践

### description 示例

```yaml
description: |
  根据需求生成代码并进行质量检查。
  适用场景：
  - 用户描述功能需求
  - 用户要求重构代码
  - 用户询问代码问题
```

### 典型目录结构

```
code-dev-skill/
├── SKILL.md
├── scripts/
│   ├── lint.py
│   ├── test.py
│   └── format.py
└── references/
    ├── style_guide.md
    └── templates/
```

## 常见问题

### 问题1：命令执行不安全

❌ 错误：直接执行用户输入的命令
✅ 正确：使用白名单验证命令

### 问题2：依赖版本冲突

❌ 错误：全局安装依赖
✅ 正确：使用虚拟环境

## 安全边界

- 禁止执行rm -rf等危险命令
- 禁止访问系统敏感文件
- 用户代码必须在沙箱中执行
