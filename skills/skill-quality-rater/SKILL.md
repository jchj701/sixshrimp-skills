---
name: skill-quality-rater
description: "Skill quality evaluation framework with 8-dimension scoring, freedom spectrum analysis, layered architecture check, and inversion test. Evaluates AI skill quality systematically."
version: "0.1.0"
user_invocable: true
---

# Skill Quality Rater - 技能质量评估器

> **概念溯源**
> - 自由度光谱 → Anthropic [Degrees of Freedom](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/skill-authoring-best-practices)
> - 分层架构 → Anthropic [Progressive Disclosure](https://www.anthropic.com/news/equipping-agents-for-the-real-world-with-agent-skills) (2025-10-16)
> - 反转测试 → 受 OpenAI [skill-creator](https://github.com/openai/skills) 启发，系统化为评估维度
> - 融合 SkillCheck、agent-skill-evaluator 等工具的评估思路

---

## 核心原则

> Skill 是给 AI 写指令，本质是：
> **"用最少的 token，在正确的层级，给 AI 最精准的约束，让它在边界内自由发挥"**

### 三大核心评估维度

1. **自由度光谱**（源自 [Anthropic "Degrees of Freedom"](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/skill-authoring-best-practices)）：检查脆弱操作是否用脚本锁死，创造性任务是否过度约束
2. **分层架构**（源自 [Anthropic "Progressive Disclosure"](https://www.anthropic.com/news/equipping-agents-for-the-real-world-with-agent-skills)）：L1/L2/L3是否各在其位，零token成本利用references
3. **反转测试**（受 [OpenAI skill-creator](https://github.com/openai/skills) "inversion test" 启发，系统化为评估维度）：每条正面指导能否改写为"不要做X"

---

## 评分维度（满分10分，精度0.1分）

| 维度 | 名称 | 权重 | 核心检查点 |
|:---:|:---|:---:|:---|
| D1 | 触发精准度 | 15% | description含"when to use"、触发词无冲突、无层错位 |
| D2 | 分层合理性 | 20% | 触发条件在frontmatter、参考细节在references、scripts执行不读入 |
| D3 | 自由度匹配 | 20% | 脆弱操作→脚本、创造性→文字、判断"该用哪种" |
| D4 | 简洁约束 | 15% | 无README/CHANGELOG、每句话值得token、无冗余 |
| D5 | 反模式表达 | 10% | "不做什么"比"做什么"精确、有反转测试 |
| D6 | 资源组织 | 10% | scripts/references/assets区分正确、无重复 |
| D7 | 领域适配 | 5% | 是否符合领域最佳实践 |
| D8 | 安全边界 | 5% | 无危险命令、无敏感信息泄露 |

### 等级映射

| 等级 | 分数 | 说明 |
|:---:|:---:|:---|
| S | 9.0-10 | 优秀，可直接作为范本 |
| A | 8.0-8.9 | 良好，小改进即可 |
| B | 7.0-7.9 | 及格，有明显短板 |
| C | 6.0-6.9 | 不及格，需重写 |
| D | <6.0 | 失败，建议删除重来 |

---

## 评估模式

### 完整评估（8维度）
对所有维度进行全面评估，生成完整报告。

### 快速评估（3核心维度）
只评估最关键的3个维度：
- D1 触发精准度（30%）
- D2 分层合理性（35%）
- D3 自由度匹配（35%）

### 批量评估
对多个Skill进行横向对比，识别共性问题和最佳实践。

---

## 评估流程（7步检查法）

### 步骤1：检查触发精准度（D1）
```
□ description是否包含"when to use"（使用场景）？
□ 触发条件/关键词是否在frontmatter？
□ 触发词是否与其他Skill冲突？（使用 trigger_collision.py）
□ 有无层错位？（L1内容漏到body）
```

### 步骤2：检查分层架构（D2）
```
□ L1层（frontmatter）：触发条件是否在description？
□ L2层（SKILL.md body）：是否有不该放的L3参考细节？
□ L3层（references/）：是否零token成本利用？
□ scripts/ 是否被当作文本读入？
```

### 步骤3：分析自由度光谱（D3）
```
□ 识别脆弱操作（文件IO、API调用）→ 是否用脚本？
□ 识别创造性任务（文案生成）→ 是否过度约束？
□ 使用 suggest_freedom.py 生成自由度建议
```

### 步骤4：检查简洁性（D4）
```
□ 是否有禁止文件（README.md、CHANGELOG.md等）？
□ 每句话是否值得token？
□ 是否有冗余解释？
```

### 步骤5：执行反转测试（D5）
```
□ 每条正面指导能否改写为"不要做X"？
□ 反模式清单是否比正面描述更具体？
□ 边界情况是否处理？
```

### 步骤6：检查资源组织（D6）
```
□ scripts/ 是否只包含可执行脚本？
□ references/ 是否只包含参考资料？
□ assets/ 是否只包含静态资源？
□ 是否有内容重复？
```

### 步骤7：检查领域适配和安全边界（D7+D8）
```
□ 是否符合领域最佳实践？（见 domain_rules/）
□ 是否有危险命令？
□ 是否有敏感信息泄露？（使用 leakage_detector.py）
```

---

## 特殊功能

### 1. 自由度建议器 (suggest_freedom.py)
自动分析哪些操作应该用脚本，哪些应该用文字。

### 2. 触发词冲突检测 (trigger_collision.py)
批量扫描多个Skill，检测description触发词重叠。

### 3. 反转测试提示
对正面描述给出"不要做X"的改写建议。

### 4. 分层迁移建议
指出L2内容应该移到L3的具体位置。

---

## 输出报告结构

```markdown
# Skill 质量评估报告

## 📊 总分：X.X / 10（X级）

## 🔍 维度详情

| 维度 | 得分 | 权重 | 状态 | 核心问题 |
|------|------|------|------|----------|
| D1. 触发精准度 | X.X | 15% | 🟢/🟡/🔴 | xxx |
| D2. 分层合理性 | X.X | 20% | 🟢/🟡/🔴 | xxx |
| D3. 自由度匹配 | X.X | 20% | 🟢/🟡/🔴 | xxx |
| D4. 简洁约束 | X.X | 15% | 🟢/🟡/🔴 | xxx |
| D5. 反模式表达 | X.X | 10% | 🟢/🟡/🔴 | xxx |
| D6. 资源组织 | X.X | 10% | 🟢/🟡/🔴 | xxx |
| D7. 领域适配 | X.X | 5% | 🟢/🟡/🔴 | xxx |
| D8. 安全边界 | X.X | 5% | 🟢/🟡/🔴 | xxx |

## 🎯 原文核心诊断

### 自由度光谱分析
- 脆弱操作检测：发现X个需要用脚本的操作
- 建议：`xxx操作` 应封装为 `scripts/xxx.py`

### 分层架构分析
- L1层错位：触发条件写在body → 应移到description
- L2层膨胀：参考细节占X行 → 应拆到references

### 反模式测试
- 原句："保持专业语气" → 建议改为："不要使用口语化表达..."

## ⚠️ 关键问题（按影响排序）
1. [高影响] xxx
2. [中影响] xxx
3. [低影响] xxx

## 💡 改进建议
- 立即修复：xxx
- 建议优化：xxx
- 可选改进：xxx
```

---

## 文件结构

```
skill-quality-rater/
├── SKILL.md                      # 主文件
├── templates/
│   ├── eval_report.md            # 评估报告模板
│   ├── improvement_plan.md       # 改进计划模板
│   └── batch_summary.md          # 批量评估汇总
├── references/
│   ├── dimension_rubric.md       # 各维度详细评分细则
│   ├── freedom_spectrum.md       # 自由度光谱判断指南 ⭐核心
│   ├── layer_architecture.md     # L1/L2/L3分层架构说明 ⭐核心
│   ├── antipattern_library.md    # 反模式库
│   ├── domain_rules/
│   │   ├── document-processing.yaml  # 文档处理领域规则
│   │   ├── data-analysis.yaml        # 数据分析领域规则
│   │   └── code-development.yaml     # 代码开发领域规则
│   └── forbidden_files.md        # 禁止文件清单
├── scripts/
│   ├── trigger_collision.py      # 触发词冲突检测
│   ├── leakage_detector.py       # 测试泄露检测
│   └── suggest_freedom.py        # 自由度建议生成
└── store/
    └── .gitkeep
```

---

## 参考资料

| 文档 | 说明 |
|:---|:---|
| [自由度光谱指南](./references/freedom_spectrum.md) | 如何判断该用脚本还是文字 |
| [分层架构说明](./references/layer_architecture.md) | L1/L2/L3各层职责 |
| [评分细则](./references/dimension_rubric.md) | 每个维度详细评分标准 |
| [反模式库](./references/antipattern_library.md) | 常见问题汇总 |
| [禁止文件清单](./references/forbidden_files.md) | 不应出现的文件 |
| [领域规则库](./references/domain_rules/) | 各领域最佳实践 |
