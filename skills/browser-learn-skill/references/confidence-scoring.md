# 置信度评分体系

本文档定义 BrowserLearn AI Agent 的置信度评分方法，包括评分维度、权重计算、阈值定义和动态调整机制。

---

## 1. 评分维度体系

### 1.1 四大核心维度

| 维度 | 代码 | 权重 | 描述 |
|------|------|------|------|
| **元素稳定性** | ELEMENT_STABILITY | 0.30 | 目标元素的稳定程度 |
| **操作确定性** | OPERATION_DETERMINISM | 0.25 | 操作结果的确定性 |
| **环境依赖度** | ENVIRONMENT_DEPENDENCY | 0.20 | 对外部环境的依赖 |
| **数据依赖度** | DATA_DEPENDENCY | 0.25 | 对动态数据的依赖 |

### 1.2 维度详细说明

#### 元素稳定性（ELEMENT_STABILITY）

评估目标元素是否容易被定位、是否稳定可靠。

| 评分 | 条件 | 示例 |
|------|------|------|
| **1.0** | 固定ID + 语义标记 | `#login-btn` + `role="button"` |
| **0.85** | 固定ID | `#login-btn` |
| **0.70** | 稳定class | `.btn-primary` |
| **0.55** | 语义选择器 | `button:has-text("登录")` |
| **0.40** | XPath位置选择 | `//div[2]/button[1]` |
| **0.25** | 动态ID | `#btn-{random}` |
| **0.10** | 坐标定位 | `x=100, y=200` |

**稳定性因子计算**：
```python
def calculate_element_stability(selector_info):
    score = 1.0
    
    # ID稳定性
    if selector_info.has_fixed_id:
        score *= 1.0
    elif selector_info.has_dynamic_id:
        score *= 0.3
    else:
        score *= 0.6
    
    # 选择器类型
    selector_type_bonus = {
        "id": 1.0,
        "data-testid": 0.95,
        "class": 0.7,
        "text": 0.75,
        "xpath": 0.5,
        "coordinate": 0.2
    }
    score *= selector_type_bonus.get(selector_info.type, 0.5)
    
    # 匹配数量（歧义惩罚）
    if selector_info.match_count > 1:
        score *= (1.0 / selector_info.match_count)
    
    return max(0.0, min(1.0, score))
```

#### 操作确定性（OPERATION_DETERMINISM）

评估操作执行后结果的可预测性。

| 评分 | 条件 | 示例 |
|------|------|------|
| **1.0** | 无副作用的确定性操作 | 纯展示页面点击 |
| **0.85** | 有预期副作用 | 表单输入 |
| **0.70** | 条件依赖操作 | toggle 类操作 |
| **0.55** | 状态变更操作 | 提交、删除 |
| **0.40** | 不可逆操作 | 永久删除 |
| **0.20** | 外部系统交互 | 支付、发送 |

**确定性因子计算**：
```python
def calculate_operation_determinism(operation_info):
    base_scores = {
        "click": 0.9,
        "type": 0.85,
        "select": 0.7,
        "hover": 0.8,
        "scroll": 0.95,
        "navigate": 0.85,
        "submit": 0.5,
        "delete": 0.3,
        "upload": 0.6,
        "execute": 0.4
    }
    
    score = base_scores.get(operation_info.type, 0.5)
    
    # 副作用惩罚
    if operation_info.has_side_effects:
        score *= 0.8
    
    # 状态依赖惩罚
    if operation_info.depends_on_current_state:
        score *= 0.7
    
    return max(0.0, min(1.0, score))
```

#### 环境依赖度（ENVIRONMENT_DEPENDENCY）

评估操作对外部环境的依赖程度。

| 评分 | 条件 | 示例 |
|------|------|------|
| **1.0** | 完全本地化 | 纯前端页面 |
| **0.85** | 依赖本地资源 | 图片加载 |
| **0.70** | 依赖服务端 | API调用 |
| **0.55** | 依赖第三方 | 第三方登录 |
| **0.40** | 依赖网络质量 | 视频加载 |
| **0.20** | 高度不稳定 | WebSocket实时数据 |

**环境依赖度计算**：
```python
def calculate_environment_dependency(context_info):
    score = 1.0
    
    # 网络依赖
    if context_info.requires_network:
        score *= 0.8
    
    # 登录依赖
    if context_info.requires_login:
        score *= 0.9
    
    # 第三方依赖
    if context_info.depends_on_third_party:
        score *= 0.6
    
    # 服务端状态
    if context_info.depends_on_server_state:
        score *= 0.75
    
    # 并发影响
    if context_info.affected_by_concurrency:
        score *= 0.7
    
    return max(0.0, min(1.0, score))
```

#### 数据依赖度（DATA_DEPENDENCY）

评估操作对动态数据的依赖程度。

| 评分 | 条件 | 示例 |
|------|------|------|
| **1.0** | 无数据依赖 | 静态表单 |
| **0.85** | 依赖固定数据集 | 固定选项列表 |
| **0.70** | 依赖用户数据 | 用户名、邮箱 |
| **0.55** | 依赖实时数据 | 库存数量 |
| **0.40** | 依赖外部数据源 | 第三方API |
| **0.20** | 高度动态数据 | 验证码、token |

**数据依赖度计算**：
```python
def calculate_data_dependency(operation_info):
    score = 1.0
    
    # 输入数据来源
    if operation_info.uses_fixed_value:
        score *= 1.0
    elif operation_info.uses_user_input:
        score *= 0.7
    elif operation_info.uses_dynamic_data:
        score *= 0.5
    
    # 数据存在性
    if operation_info.data_must_exist:
        score *= 0.8
    
    # 数据唯一性
    if operation_info.requires_unique_data:
        score *= 0.6
    
    # 数据时效性
    if operation_info.uses_temporary_token:
        score *= 0.4
    
    return max(0.0, min(1.0, score))
```

---

## 2. 综合置信度计算

### 2.1 加权求和公式

```
Confidence = Σ (维度得分 × 权重)
           = Element_Stability × 0.30 
           + Operation_Determinism × 0.25 
           + Environment_Dependency × 0.20 
           + Data_Dependency × 0.25
```

### 2.2 计算示例

```python
# 示例：点击登录按钮
confidence = calculate_overall_confidence({
    "element_stability": 0.85,      # 使用固定ID
    "operation_determinism": 0.50, # 提交操作
    "environment_dependency": 0.85, # 需要网络
    "data_dependency": 0.70        # 依赖用户输入
})

# 计算过程
# = 0.85 × 0.30 + 0.50 × 0.25 + 0.85 × 0.20 + 0.70 × 0.25
# = 0.255 + 0.125 + 0.17 + 0.175
# = 0.725

print(f"综合置信度: {confidence:.2f}")  # 输出: 0.73
```

---

## 3. 阈值体系

### 3.1 置信度等级

| 等级 | 分数范围 | 标识 | 含义 | 建议行为 |
|------|---------|------|------|---------|
| **A** | 0.90 - 1.00 | 🟢 极高 | 非常可靠 | 正常执行 |
| **B** | 0.80 - 0.89 | 🟢 高 | 可靠 | 正常执行，可选提示 |
| **C** | 0.70 - 0.79 | 🟡 中 | 基本可靠 | 谨慎执行 |
| **D** | 0.60 - 0.69 | 🟠 低 | 存在风险 | 人工确认后执行 |
| **E** | 0.50 - 0.59 | 🔴 很低 | 高风险 | 必须人工确认 |
| **F** | < 0.50 | 🔴 极低 | 不可执行 | 拒绝执行或重写 |

### 3.2 决策阈值

| 阈值类型 | 数值 | 说明 |
|---------|------|------|
| **执行阈值** | 0.60 | 低于此值不自动执行 |
| **确认阈值** | 0.70 | 需要人工确认 |
| **提示阈值** | 0.80 | 低于此值给出警告 |
| **自恢复阈值** | 0.50 | 低于此值不自恢复 |

---

## 4. 动态调整机制

### 4.1 执行过程调整

```python
def adjust_confidence_during_execution(initial_confidence, execution_result):
    """
    根据执行结果动态调整置信度
    """
    adjusted = initial_confidence
    
    # 元素定位成功
    if execution_result.element_found:
        adjusted += 0.05
    
    # 元素可见
    if execution_result.element_visible:
        adjusted += 0.03
    
    # 结果符合预期
    if execution_result.result_matched:
        adjusted += 0.10
    else:
        adjusted -= 0.20
    
    # 页面状态正常
    if execution_result.page_stable:
        adjusted += 0.02
    else:
        adjusted -= 0.10
    
    # 性能正常
    if execution_result.response_time < 5000:  # < 5秒
        adjusted += 0.02
    
    return max(0.0, min(1.0, adjusted))
```

### 4.2 历史数据调整

```python
def adjust_based_on_history(skill_id, step_id, current_confidence):
    """
    根据历史执行数据调整置信度
    """
    history = get_execution_history(skill_id, step_id, limit=20)
    
    if len(history) < 3:
        return current_confidence
    
    # 计算历史成功率
    success_rate = sum(1 for h in history if h.success) / len(history)
    
    # 计算历史平均置信度
    avg_confidence = sum(h.confidence for h in history) / len(history)
    
    # 成功率调整
    if success_rate >= 0.95:
        current_confidence = min(1.0, current_confidence + 0.05)
    elif success_rate >= 0.85:
        current_confidence = current_confidence  # 保持不变
    elif success_rate >= 0.70:
        current_confidence *= 0.95
    else:
        current_confidence *= 0.80
    
    # 历史置信度趋势
    recent_trend = calculate_trend([h.confidence for h in history[-5:]])
    if recent_trend > 0.02:  # 上升趋势
        current_confidence = min(1.0, current_confidence + 0.03)
    elif recent_trend < -0.02:  # 下降趋势
        current_confidence *= 0.95
    
    return max(0.0, min(1.0, current_confidence))
```

### 4.3 置信度轨迹

```json
{
  "skill_id": "login-system",
  "step_id": 3,
  "execution_id": "exec_20260429_001",
  
  "confidence_trajectory": [
    {
      "phase": "pre_execution",
      "timestamp": "2026-04-29T10:30:00Z",
      "confidence": 0.73,
      "factors": {
        "element_stability": 0.85,
        "operation_determinism": 0.50,
        "environment_dependency": 0.85,
        "data_dependency": 0.70
      }
    },
    {
      "phase": "element_locate",
      "timestamp": "2026-04-29T10:30:01Z",
      "confidence": 0.78,
      "delta": "+0.05",
      "reason": "元素定位成功"
    },
    {
      "phase": "result_check",
      "timestamp": "2026-04-29T10:30:02Z",
      "confidence": 0.88,
      "delta": "+0.10",
      "reason": "执行结果符合预期"
    },
    {
      "phase": "final",
      "timestamp": "2026-04-29T10:30:03Z",
      "confidence": 0.90,
      "delta": "+0.02",
      "reason": "性能正常"
    }
  ],
  
  "summary": {
    "initial_confidence": 0.73,
    "final_confidence": 0.90,
    "improvement": 0.17,
    "execution_time_ms": 3000,
    "status": "success"
  }
}
```

---

## 5. 置信度报告

### 5.1 报告模板

```json
{
  "report_id": "conf_20260429_001",
  "generated_at": "2026-04-29T10:30:00Z",
  "skill_id": "登录系统",
  
  "overall_assessment": {
    "confidence_score": 0.78,
    "grade": "C",
    "risk_level": "medium",
    "recommendation": "谨慎执行，建议人工监督"
  },
  
  "step_scores": [
    {
      "step_id": 1,
      "action": "click",
      "target": "#username",
      "confidence": 0.92,
      "grade": "A",
      "factors": {
        "element_stability": 0.95,
        "operation_determinism": 0.90,
        "environment_dependency": 0.90,
        "data_dependency": 0.95
      }
    },
    {
      "step_id": 2,
      "action": "type",
      "target": "#username",
      "input": "test_user",
      "confidence": 0.85,
      "grade": "B",
      "factors": {
        "element_stability": 0.95,
        "operation_determinism": 0.85,
        "environment_dependency": 0.85,
        "data_dependency": 0.75
      }
    },
    {
      "step_id": 3,
      "action": "click",
      "target": "#login-btn",
      "confidence": 0.58,
      "grade": "E",
      "factors": {
        "element_stability": 0.85,
        "operation_determinism": 0.50,
        "environment_dependency": 0.60,
        "data_dependency": 0.40
      },
      "warnings": [
        {
          "type": "high_risk_operation",
          "message": "提交操作依赖用户凭据有效性"
        },
        {
          "type": "state_change",
          "message": "此操作将改变系统状态"
        }
      ],
      "requires_confirmation": true
    }
  ],
  
  "critical_issues": [
    {
      "issue_id": 1,
      "severity": "high",
      "description": "步骤3的置信度过低",
      "current_score": 0.58,
      "required_score": 0.70,
      "suggestion": "建议使用更稳定的定位方式或优化操作流程"
    }
  ],
  
  "recommendations": [
    {
      "priority": "high",
      "action": "在执行前确认测试账号有效性",
      "estimated_impact": "+0.10"
    },
    {
      "priority": "medium",
      "action": "为步骤3添加结果验证",
      "estimated_impact": "+0.05"
    }
  ]
}
```

---

## 6. 置信度可视化

### 6.1 置信度仪表盘

```
┌─────────────────────────────────────────────────────────────────┐
│                    置信度仪表盘：登录系统                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  综合置信度: 0.78  [███████░░░] C级 🟡                            │
│                                                                  │
│  各维度得分:                                                     │
│  ├── 元素稳定性:   0.85  [████████░░] ████████████████████░░░    │
│  ├── 操作确定性:   0.65  [██████░░░] ████████████████░░░░░░░    │
│  ├── 环境依赖度:   0.80  [████████░] ██████████████████████░░    │
│  └── 数据依赖度:   0.75  [███████░░] ███████████████████░░░░    │
│                                                                  │
│  步骤置信度:                                                     │
│  ├── 步骤1 (点击输入框):    0.92  A级 🟢                         │
│  ├── 步骤2 (输入用户名):    0.85  B级 🟢                         │
│  ├── 步骤3 (点击登录):      0.58  E级 🔴 ⚠️ 需要确认              │
│  └── 步骤4 (等待跳转):      0.75  C级 🟡                         │
│                                                                  │
│  风险提示:                                                       │
│  ⚠️ 步骤3 的操作确定性较低（0.65）                               │
│  ⚠️ 步骤3 的数据依赖度较高（0.40）                               │
│  🔴 步骤3 需要人工确认后才能执行                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. 调整规则总结

| 触发条件 | 调整幅度 | 方向 |
|---------|---------|------|
| 元素定位成功 | +0.05 | 上升 |
| 结果符合预期 | +0.10 | 上升 |
| 页面状态稳定 | +0.02 | 上升 |
| 性能正常 | +0.02 | 上升 |
| 历史成功率高 | +0.05 | 上升 |
| 上升趋势明显 | +0.03 | 上升 |
| 结果不符合预期 | -0.20 | 下降 |
| 页面状态异常 | -0.10 | 下降 |
| 历史成功率低 | -0.05 | 下降 |
| 下降趋势明显 | -0.05 | 下降 |
