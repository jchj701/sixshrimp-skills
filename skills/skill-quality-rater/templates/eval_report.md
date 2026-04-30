# Skill 质量评估报告

## 📊 总分：{total_score} / 10（{grade}级）

## 基本信息

| 项目 | 内容 |
|:---|:---|
| **Skill名称** | {skill_name} |
| **Skill路径** | {skill_path} |
| **评估时间** | {timestamp} |
| **评估模式** | {mode} |

---

## 🔍 维度详情

| 维度 | 得分 | 权重 | 状态 | 核心问题 |
|------|------|------|------|----------|
| D1. 触发精准度 | {d1_score} | 15% | {d1_status} | {d1_issues} |
| D2. 分层合理性 | {d2_score} | 20% | {d2_status} | {d2_issues} |
| D3. 自由度匹配 | {d3_score} | 20% | {d3_status} | {d3_issues} |
| D4. 简洁约束 | {d4_score} | 15% | {d4_status} | {d4_issues} |
| D5. 反模式表达 | {d5_score} | 10% | {d5_status} | {d5_issues} |
| D6. 资源组织 | {d6_score} | 10% | {d6_status} | {d6_issues} |
| D7. 领域适配 | {d7_score} | 5% | {d7_status} | {d7_issues} |
| D8. 安全边界 | {d8_score} | 5% | {d8_status} | {d8_issues} |

**状态说明**：🟢良好(≥8) 🟡需改进(6-8) 🔴严重(<6)

---

## 🎯 原文核心诊断

### 自由度光谱分析
{freedom_analysis}

### 分层架构分析
{layer_analysis}

### 反模式测试
{antipattern_analysis}

---

## ⚠️ 关键问题（按影响排序）

### 🔴 高影响问题

{high_impact_issues}

### 🟡 中影响问题

{medium_impact_issues}

### 🟢 低影响问题

{low_impact_issues}

---

## 💡 改进建议

### 立即修复

{immediate_fixes}

### 建议优化

{recommended_improvements}

### 可选改进

{optional_improvements}

---

## 📁 文件结构

```
{file_tree}
```

---

## 总结

### 核心优势

{strengths}

### 主要不足

{weaknesses}

### 最终建议

{final_recommendation}

---

*报告生成时间：{timestamp}*
*使用工具：skill-quality-rater*
*基于《如何写出好的 Skill？拆解 skill-creator 背后的设计》*
