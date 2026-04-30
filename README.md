# sixshrimp-skills

[English](./README_en.md) | 中文

我的 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 自定义技能集。

## 安装

使用 [skills CLI](https://github.com/vercel-labs/skills)（基于 `npx`）一行安装：

```bash
# 安装全部技能（全局）
npx skills add jchj701/sixshrimp-skills -g --all

# 安装单个技能
npx skills add jchj701/sixshrimp-skills -g --skill skill-quality-rater

# 查看可用技能
npx skills add jchj701/sixshrimp-skills -l
```

或手动安装：

```bash
git clone https://github.com/jchj701/sixshrimp-skills.git
cp -r sixshrimp-skills/skills/* ~/.claude/skills/
```

## 技能列表

| 技能 | 版本 | 说明 | 依赖 |
|:---|:---:|:---|:---|
| **skill-quality-rater** | 0.1.0 | 8维度技能质量评估器 | Python 3 |
| **browser-learn-skill** | 0.1.0 | 浏览器操作录制与AI自主学习 | Python 3, browser-use SDK |

## ⚠️ 状态：未经测试

这些技能是**进行中的作品，尚未在真实的 Claude Code 环境中测试过**。以当前状态分享，目的是：

- 为技能设计模式提供参考和灵感
- 收集社区反馈与协作
- 在正式使用前迭代改进

预期会有粗糙之处，使用风险自负。欢迎提 Issue 和 PR。

---

## skill-quality-rater

8维度技能质量评估器，将 Anthropic、OpenAI、Google 等官方 Skill 设计原则系统化为一套可执行的评估框架。

### 概念溯源

本技能的评估维度并非凭空发明，而是源自行业已有的权威实践：

| 评估维度 | 溯源 | 说明 |
|:---|:---|:---|
| 自由度光谱 | [Anthropic "Degrees of Freedom"](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/skill-authoring-best-practices) | 高/中/低自由度分类，脆弱操作→脚本，创造性→文字 |
| 分层架构 L1/L2/L3 | [Anthropic "Progressive Disclosure"](https://www.anthropic.com/news/equipping-agents-for-the-real-world-with-agent-skills) (2025-10-16) | 三级渐进式披露，也被 [OpenAI skill-creator](https://github.com/openai/skills) 和 [Google ADK](https://cloud.google.com/blog/topics/developers-practitioners/5-agent-skill-design-patterns-every-adk-developer-should-know) 采用 |
| 反转测试 | 受 [OpenAI skill-creator](https://github.com/openai/skills) "inversion test" 启发 | skill-creator 提到了将正面指导改写为"不要做X"的思路，本技能将其**系统化为一个正式评估维度** |
| 负面触发词 | [Anthropic 最佳实践](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/skill-authoring-best-practices) + [Google ADK Inversion Pattern](https://cloud.google.com/blog/topics/developers-practitioners/5-agent-skill-design-patterns-every-adk-developer-should-know) | 解决 over-triggering 的共识方案 |

**本技能的创新点**：将上述分散在各官方文档中的设计原则，整合为一套可执行的 8 维度评分框架，并提供自动化检测脚本（触发词冲突检测、敏感信息泄露检测、自由度建议生成）。

### 8维度评分体系

| 维度 | 权重 | 核心检查点 |
|:---|:---:|:---|
| D1 触发精准度 | 15% | description 包含 "when to use"、触发词无冲突 |
| D2 分层合理性 | 20% | L1/L2/L3 各在其位、scripts 执行不读入 |
| D3 自由度匹配 | 20% | 脆弱操作→脚本、创造性→文字 |
| D4 简洁约束 | 15% | 无 README/CHANGELOG 冗余、每句话值得 token |
| D5 反模式表达 | 10% | "不要做X" 比 "做Y" 更精确 |
| D6 资源组织 | 10% | scripts/references/assets 归位正确 |
| D7 领域适配 | 5% | 符合领域最佳实践 |
| D8 安全边界 | 5% | 无危险命令、无敏感信息泄露 |

### 文件结构

```
skill-quality-rater/
├── SKILL.md                      # 主文件（8维度评分框架）
├── references/
│   ├── dimension_rubric.md       # 各维度详细评分细则
│   ├── freedom_spectrum.md       # 自由度光谱判断指南
│   ├── layer_architecture.md     # L1/L2/L3 分层架构说明
│   ├── antipattern_library.md    # 反模式库
│   ├── forbidden_files.md        # 技能中不应出现的文件清单
│   └── domain_rules/             # 领域规则库
│       ├── document-processing.yaml
│       ├── data-analysis.yaml
│       └── code-development.yaml
├── scripts/
│   ├── trigger_collision.py      # 触发词冲突检测
│   ├── leakage_detector.py       # 敏感信息泄露检测
│   └── suggest_freedom.py        # 自由度建议生成
└── templates/
    ├── eval_report.md            # 评估报告模板
    ├── improvement_plan.md       # 改进计划模板
    └── batch_summary.md          # 批量评估汇总模板
```

---

## browser-learn-skill

浏览器操作录制与 AI 自主学习执行技能。定义从人类演示到自动化执行的完整流程。

### 核心原则

> **"AI不做不确定的决策。一次性操作必须标记。环境不行不往下走。"**

### 5个执行阶段

| 阶段 | 名称 | 做什么 |
|:---:|:---|:---|
| 1 | 可复现性判定 | 判断操作是否可脚本化 |
| 2 | 环境就绪检查 | 验证依赖、权限、网络状态 |
| 3 | 录制解读 | 解析人类操作序列 |
| 4 | 置信度检测 | 执行前自我评估确定性 |
| 5 | 脚本固化 | 高置信度操作转为可复用脚本 |

### 7条 AI 边界约束

技能对 AI 自主性设定严格边界：
- 不可在未确认时执行不可逆操作
- 环境检查未通过不可继续
- 不得跳过异常上报
- 不得伪造置信度分数

### 文件结构

```
browser-learn-skill/
├── SKILL.md                      # 主文件（446行）
├── references/
│   ├── reproducibility-checklist.md  # 可复现性判定标准
│   ├── script-format-spec.md         # 脚本格式规范
│   ├── confidence-scoring.md         # 置信度评分标准
│   └── solidification-criteria.md    # 脚本固化判定标准
└── scripts/
    ├── env_readiness_check.py    # 环境就绪检查脚本
    └── script_sanitize.py        # 录制脚本清洗脚本
```

---

## 参考资料

- [Anthropic: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/news/equipping-agents-for-the-real-world-with-agent-skills) (2025-10-16)
- [Anthropic: Skill authoring best practices](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/skill-authoring-best-practices)
- [Anthropic: The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [OpenAI: skill-creator](https://github.com/openai/skills)
- [Google ADK: 5 Agent Skill Design Patterns](https://cloud.google.com/blog/topics/developers-practitioners/5-agent-skill-design-patterns-every-adk-developer-should-know)
- [OpenAI: Prompt Engineering Best Practices](https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-openai-api)

---

## 许可证

[MIT](./LICENSE)
