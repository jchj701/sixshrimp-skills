# 固化判定标准

本文档定义 BrowserLearn AI Agent 从"可执行"到"完全固化"的渐进式判定标准。

---

## 1. 固化等级体系

### 1.1 四级固化模型

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         固化等级演进图                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────┐                                                           │
│  │   L1    │  草稿态 (Draft)                                             │
│  │  0-0.59 │  ─ 需要人工全程监督                                           │
│  └────┬────┘    AI自主执行能力：0%                                       │
│       │         适用场景：初始学习阶段                                      │
│       │                                                                  │
│       │  升级条件:                                                       │
│       │  • 连续3次执行成功                                                 │
│       │  • 平均置信度 ≥ 0.65                                             │
│       ▼                                                                  │
│  ┌─────────┐                                                           │
│  │   L2    │  可执行态 (Executable)                                       │
│  │ 0.60-   │  ─ AI执行，发现问题暂停                                       │
│  │  0.74   │    AI自主执行能力：60%                                       │
│  └────┬────┘    适用场景：开发测试、演示                                    │
│       │                                                                  │
│       │  升级条件:                                                       │
│       │  • 连续10次执行成功                                               │
│       │  • 平均置信度 ≥ 0.80                                              │
│       │  • 自恢复成功次数 ≥ 3                                            │
│       │  • 无用户介入操作                                                 │
│       ▼                                                                  │
│  ┌─────────┐                                                           │
│  │   L3    │  稳定态 (Stable)                                             │
│  │ 0.75-   │  ─ AI自主执行，异常时自恢复                                    │
│  │  0.89   │    AI自主执行能力：85%                                        │
│  └────┬────┘    适用场景：日常自动化、无人值守                               │
│       │                                                                  │
│       │  升级条件:                                                       │
│       │  • 连续50次执行成功                                               │
│       │  • 平均置信度 ≥ 0.92                                              │
│       │  • 最近30次无失败记录                                             │
│       │  • 用户评价满意度 ≥ 4.0/5.0                                       │
│       ▼                                                                  │
│  ┌─────────┐                                                           │
│  │   L4    │  固化态 (Solidified)                                          │
│  │ 0.90-   │  ─ 完全固化，可独立运行                                        │
│  │  1.00   │    AI自主执行能力：100%                                       │
│  └─────────┘    适用场景：生产环境、关键业务                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 等级特征对比

| 特征 | L1 草稿态 | L2 可执行态 | L3 稳定态 | L4 固化态 |
|------|----------|------------|----------|----------|
| **自主执行能力** | 0% | 60% | 85% | 100% |
| **人工监督需求** | 全程 | 关键节点 | 异常时 | 无 |
| **自恢复能力** | 无 | 基础 | 完整 | 完全 |
| **置信度要求** | < 0.60 | ≥ 0.60 | ≥ 0.75 | ≥ 0.90 |
| **连续成功要求** | 无 | 3次 | 10次 | 50次 |
| **适用环境** | 仅测试 | 测试/演示 | 生产/日常 | 生产/关键 |
| **脚本形式** | 动态生成 | 半静态 | 静态+容错 | 稳定脚本 |

---

## 2. 升级判定标准

### 2.1 L1 → L2 升级标准

**触发条件**（需同时满足）：

| 条件 | 要求 | 当前值 | 状态 |
|------|------|--------|------|
| 连续执行成功次数 | ≥ 3 | ? | ☐ |
| 平均置信度 | ≥ 0.65 | ? | ☐ |
| 无致命错误 | 100% | ? | ☐ |
| 执行时间稳定 | 波动 < 30% | ? | ☐ |

**判定检查清单**：
```
☐ 连续3次执行均成功
☐ 最近5次平均置信度 ≥ 0.65
☐ 无 STATE_CHANGE 类误操作
☐ 元素定位方式已验证
☐ 无用户手动介入记录
```

**升级检查脚本**：
```python
def check_l1_to_l2_upgrade(skill_id):
    history = get_execution_history(skill_id, limit=10)
    
    # 条件1: 连续成功次数
    consecutive_success = count_consecutive_success(history, required=3)
    
    # 条件2: 平均置信度
    recent_confidences = [h.confidence for h in history[-5:]]
    avg_confidence = sum(recent_confidences) / len(recent_confidences)
    
    # 条件3: 无致命错误
    no_fatal_errors = not any(h.has_fatal_error for h in history[-3:])
    
    # 条件4: 执行时间稳定
    execution_times = [h.duration_ms for h in history[-5:]]
    time_variance = calculate_variance(execution_times)
    time_stable = time_variance < 0.30
    
    can_upgrade = (
        consecutive_success >= 3 and
        avg_confidence >= 0.65 and
        no_fatal_errors and
        time_stable
    )
    
    return {
        "can_upgrade": can_upgrade,
        "consecutive_success": consecutive_success,
        "avg_confidence": avg_confidence,
        "no_fatal_errors": no_fatal_errors,
        "time_stable": time_stable,
        "blocking_conditions": get_blocking_conditions(...)
    }
```

### 2.2 L2 → L3 升级标准

**触发条件**（需同时满足）：

| 条件 | 要求 | 当前值 | 状态 |
|------|------|--------|------|
| 连续执行成功次数 | ≥ 10 | ? | ☐ |
| 平均置信度 | ≥ 0.80 | ? | ☐ |
| 自恢复成功次数 | ≥ 3 | ? | ☐ |
| 无用户介入操作 | 最近5次 | ? | ☐ |
| 选择器稳定性 | 已优化 | ? | ☐ |

**额外要求**：
- 所有高风险操作已有降级方案
- 关键节点有结果验证
- 异常日志记录完整

### 2.3 L3 → L4 升级标准

**触发条件**（需同时满足）：

| 条件 | 要求 | 当前值 | 状态 |
|------|------|--------|------|
| 连续执行成功次数 | ≥ 50 | ? | ☐ |
| 平均置信度 | ≥ 0.92 | ? | ☐ |
| 最近失败次数 | 0 (最近30次) | ? | ☐ |
| 用户满意度 | ≥ 4.0/5.0 | ? | ☐ |
| 性能达标 | P95 < 10s | ? | ☐ |

**质量检查**：
```
☐ 代码审查通过
☐ 边界条件测试通过
☐ 并发安全检查通过（如适用）
☐ 资源泄漏检查通过
☐ 安全扫描通过（如涉及敏感操作）
```

---

## 3. 降级判定标准

### 3.1 降级触发条件

| 触发事件 | 降级幅度 | 说明 |
|---------|---------|------|
| 单次执行失败 | L→L-1 | 降1级 |
| 连续2次失败 | L→L-2 | 降2级 |
| 置信度骤降 > 0.3 | 立即降级 | 紧急处理 |
| 用户标记失败 | L→L-1 | 降1级 |
| 检测到致命错误 | 降至L1 | 最低级 |

### 3.2 降级决策流程

```python
def handle_execution_failure(skill_id, failure_info):
    current_level = get_current_level(skill_id)
    failure_type = classify_failure(failure_info)
    
    if failure_type == "fatal":
        new_level = "L1"
        reason = "检测到致命错误"
    elif failure_type == "consecutive":
        new_level = max("L1", decrement_level(current_level, 2))
        reason = "连续执行失败"
    elif failure_type == "single":
        new_level = decrement_level(current_level, 1)
        reason = "单次执行失败"
    elif failure_type == "confidence_drop":
        if failure_info.confidence_drop > 0.3:
            new_level = "L1"
            reason = "置信度骤降"
        else:
            new_level = decrement_level(current_level, 1)
            reason = "置信度下降"
    else:
        new_level = current_level
    
    # 记录降级事件
    record_downgrade_event(skill_id, current_level, new_level, reason)
    
    # 生成降级报告
    generate_downgrade_report(skill_id, failure_info, new_level)
    
    return {
        "old_level": current_level,
        "new_level": new_level,
        "reason": reason,
        "action_required": get_action_for_level(new_level)
    }
```

---

## 4. 渐进式固化流程

### 4.1 固化检查点

```
执行进度 ──────────────────────────────────────────────────────────────▶

    │              │              │              │              │
    ▼              ▼              ▼              ▼              ▼
┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
│ L1-1   │───▶│ L1-2   │───▶│ L2-1   │───▶│ L2-2   │───▶│ L3-1   │
│ 初始   │    │ 验证   │    │ 初步   │    │ 稳定   │    │ 成熟   │
│ 脚本   │    │ 选择器 │    │ 执行   │    │ 验证   │    │ 验证   │
└────────┘    └────────┘    └────────┘    └────────┘    └────────┘
    │              │              │              │              │
    ▼              ▼              ▼              ▼              ▼
 人工            优化            自动            扩展            最终
 监督          选择器           执行            测试            固化
```

### 4.2 各阶段验收标准

#### L1 阶段（草稿态）

| 检查项 | 验收标准 | 检查方法 |
|-------|---------|---------|
| 脚本完整性 | 所有录制步骤都已转换 | 步骤数对比 |
| 语义理解 | AI对每个操作的理解与用户意图一致 | 用户确认 |
| 选择器有效 | 每个选择器在目标页面可定位 | 自动化测试 |
| 基础可执行 | 脚本可以启动并执行第一步 | 手动验证 |

#### L2 阶段（可执行态）

| 检查项 | 验收标准 | 检查方法 |
|-------|---------|---------|
| 连续成功 | 连续3次执行成功 | 自动化测试 |
| 错误处理 | 基础错误有捕获和处理 | 注入异常测试 |
| 日志完整 | 执行过程有完整日志 | 日志审查 |
| 结果验证 | 操作结果有验证机制 | 结果检查 |

#### L3 阶段（稳定态）

| 检查项 | 验收标准 | 检查方法 |
|-------|---------|---------|
| 长期稳定 | 连续10次执行成功 | 自动化测试 |
| 自恢复能力 | 常见异常可自动恢复 | 异常注入测试 |
| 性能达标 | P95执行时间 < 阈值 | 性能测试 |
| 并发安全 | 多实例执行无冲突 | 并发测试 |

#### L4 阶段（固化态）

| 检查项 | 验收标准 | 检查方法 |
|-------|---------|---------|
| 工业级稳定 | 连续50次执行成功 | 压力测试 |
| 文档完整 | 有完整的使用文档 | 文档审查 |
| 代码质量 | 通过代码审查 | CR检查 |
| 生产就绪 | 可部署到生产环境 | 环境验证 |

---

## 5. 固化判定工具

### 5.1 固化评估脚本

```python
#!/usr/bin/env python3
"""
固化等级评估工具
usage: python solidify_assessor.py --skill_id login-system
"""

import argparse
import json
from typing import Dict, List, Optional

class SolidificationAssessor:
    def __init__(self, skill_id: str):
        self.skill_id = skill_id
        self.history = self.load_history()
    
    def assess_current_level(self) -> Dict:
        """评估当前固化等级"""
        level = self.determine_level()
        upgrade_candidates = self.check_upgrade_conditions(level)
        downgrade_risks = self.check_downgrade_risks(level)
        
        return {
            "skill_id": self.skill_id,
            "current_level": level,
            "confidence": self.calculate_overall_confidence(),
            "upgrade_candidates": upgrade_candidates,
            "downgrade_risks": downgrade_risks,
            "recommendations": self.generate_recommendations(level)
        }
    
    def determine_level(self) -> str:
        """确定当前等级"""
        if self.meets_l4_criteria():
            return "L4"
        elif self.meets_l3_criteria():
            return "L3"
        elif self.meets_l2_criteria():
            return "L2"
        else:
            return "L1"
    
    def meets_l4_criteria(self) -> bool:
        """检查L4条件"""
        return (
            self.get_consecutive_success() >= 50 and
            self.get_avg_confidence() >= 0.92 and
            self.get_recent_failures(30) == 0 and
            self.get_user_satisfaction() >= 4.0
        )
    
    def meets_l3_criteria(self) -> bool:
        """检查L3条件"""
        return (
            self.get_consecutive_success() >= 10 and
            self.get_avg_confidence() >= 0.80 and
            self.get_self_recovery_count() >= 3
        )
    
    def meets_l2_criteria(self) -> bool:
        """检查L2条件"""
        return (
            self.get_consecutive_success() >= 3 and
            self.get_avg_confidence() >= 0.65
        )
```

### 5.2 固化报告模板

```json
{
  "report_id": "solid_20260429_001",
  "generated_at": "2026-04-29T10:30:00Z",
  "skill_id": "登录系统",
  
  "current_status": {
    "level": "L2",
    "level_name": "可执行态",
    "autonomy": "60%",
    "confidence": 0.72,
    "consecutive_success": 5,
    "total_executions": 8
  },
  
  "upgrade_assessment": {
    "target_level": "L3",
    "meets_criteria": false,
    "criteria_check": [
      {
        "criterion": "连续成功次数 ≥ 10",
        "required": 10,
        "current": 5,
        "status": "fail"
      },
      {
        "criterion": "平均置信度 ≥ 0.80",
        "required": 0.80,
        "current": 0.72,
        "status": "fail"
      },
      {
        "criterion": "自恢复成功次数 ≥ 3",
        "required": 3,
        "current": 1,
        "status": "fail"
      }
    ],
    "gap_analysis": {
      "consecutive_success_gap": 5,
      "confidence_gap": 0.08,
      "recovery_gap": 2,
      "estimated_iterations": 15
    }
  },
  
  "downgrade_risks": {
    "risk_level": "low",
    "triggers": [
      {
        "type": "single_failure",
        "current_status": "not_triggered",
        "impact": "降级至L1"
      }
    ]
  },
  
  "recommendations": [
    {
      "priority": "high",
      "action": "继续执行以积累成功次数",
      "estimated_time": "5-10次执行"
    },
    {
      "priority": "medium",
      "action": "优化步骤3的置信度",
      "current_confidence": 0.58,
      "target_confidence": 0.75
    }
  ],
  
  "next_review": "2026-04-30T10:30:00Z"
}
```

---

## 6. 固化状态流转

### 6.1 完整状态机

```
                    ┌─────────────────────────────────────┐
                    │                                      │
                    │                                      ▼
┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
│   L1   │───▶│   L2   │───▶│   L3   │───▶│   L4   │    │L4_FALL │
│ 草稿态 │    │可执行态│    │ 稳定态 │    │ 固化态 │◀───│ 降级   │
└────────┘    └────────┘    └────────┘    └────────┘    └────────┘
     │              │              │              │
     │ 降级          │ 降级          │ 降级          │
     ▼              ▼              ▼              │
┌────────┐    ┌────────┐    ┌────────┐             │
│ L1_MIN │    │ L2_MIN │    │ L3_MIN │─────────────┘
│ 最低草稿│    │ 最低可执行│   │ 最低稳定│
└────────┘    └────────┘    └────────┘

降级路径：
• L4 → L3 → L2 → L1 (渐进降级)
• L4 → L1 (致命错误直接降级)
• L3 → L1 (连续失败降级)
```

### 6.2 状态记录

```json
{
  "skill_id": "登录系统",
  "level_history": [
    {
      "level": "L1",
      "entered_at": "2026-04-25T10:00:00Z",
      "exited_at": "2026-04-26T15:30:00Z",
      "duration_hours": 29.5,
      "reason": "初始创建"
    },
    {
      "level": "L2",
      "entered_at": "2026-04-26T15:30:00Z",
      "exited_at": "2026-04-28T10:00:00Z",
      "duration_hours": 42.5,
      "reason": "升级",
      "upgrade_trigger": "连续3次成功"
    },
    {
      "level": "L3",
      "entered_at": "2026-04-28T10:00:00Z",
      "exited_at": null,
      "duration_hours": 24.0,
      "reason": "升级",
      "upgrade_trigger": "连续10次成功，自恢复3次"
    }
  ],
  "current_level": "L3",
  "stats": {
    "total_time_to_l3_hours": 72.0,
    "total_executions": 25,
    "total_failures": 2,
    "success_rate": 0.92
  }
}
```

---

## 7. 特殊场景处理

### 7.1 页面更新检测与响应

```python
def handle_page_update(skill_id, change_info):
    """
    检测到页面更新时的处理流程
    """
    change_type = classify_page_change(change_info)
    
    if change_type == "minor":
        # 微小更新，尝试自恢复
        result = attempt_self_healing(skill_id)
        if result.success:
            return {"action": "self_healed", "confidence_adjustment": -0.05}
        else:
            return handle_failure(skill_id, "recovery_failed")
    
    elif change_type == "major":
        # 重大更新，需要重新评估
        return {
            "action": "require_re_evaluation",
            "confidence_adjustment": -0.30,
            "recommended_level": "L1",
            "reason": "页面结构重大变化，需要重新学习"
        }
    
    elif change_type == "breaking":
        # 破坏性更新，降至最低级
        return {
            "action": "demote_to_l1",
            "confidence_adjustment": -0.50,
            "reason": "检测到破坏性更新，脚本已不适用"
        }
```

### 7.2 环境变化检测

```python
def handle_environment_change(skill_id, env_change):
    """
    检测到环境变化时的处理
    """
    # 网络变化
    if env_change.type == "network":
        if env_change.impact == "slower":
            adjust_timeout(skill_id, multiplier=1.5)
            return {"action": "timeout_adjusted"}
    
    # 登录状态变化
    if env_change.type == "session":
        if not env_change.valid:
            return {
                "action": "require_login",
                "confidence_adjustment": -0.20
            }
    
    # 数据状态变化
    if env_change.type == "data":
        if env_change.data_missing:
            return {
                "action": "require_data_prep",
                "confidence_adjustment": -0.15
            }
```
