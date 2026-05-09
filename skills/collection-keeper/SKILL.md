---
name: collection-keeper
description: "Mark and collect content to Feishu document. Use when user says '马一下', '收藏', 'mark一下', or wants to save content to their collection document."
version: "0.2.0"
user_invocable: true
---

# 收藏管家 (Collection Keeper)

## 功能说明
当用户提到"请收藏记录"、"放到收藏大全"、"记录到收藏大全"、"mark一下"、"马一下"等意图时，将内容整理后追加到飞书收藏大全文档。

## 触发关键词
- "请收藏记录"
- "放到收藏大全"
- "记录到收藏大全"
- "mark一下"
- "马一下"
- "收藏一下"
- "收藏这个"
- "记录到收藏"
- 其他表达"收藏/记录"意图的描述

## 配置

通过环境变量或本地配置文件 `.env.local` 设置（**不要硬编码私人信息到 SKILL.md**）：

| 环境变量 | 必填 | 说明 | 示例 |
|---------|:---:|------|------|
| `COLLECTION_DOC_ID` | ✅ | 飞书收藏大全文档ID | `R7Oodxxx` （从飞书文档URL中获取） |
| `COLLECTION_DOC_URL` | ❌ | 飞书收藏大全文档链接 | `https://www.feishu.cn/docx/xxx` |
| `FEISHU_IDENTITY` | ✅ | 飞书文档写入身份 | `bot` 或 `user`（文档由bot创建时用 `bot`） |
| `WECHAT_FETCH_SCRIPT` | ❌ | 微信文章提取脚本路径 | 本地路径 |

**配置方式**（二选一）：
1. 在 skill 目录下创建 `.env.local` 文件（已被 `.gitignore` 忽略）
2. 直接设置环境变量

```bash
# .env.local 示例
COLLECTION_DOC_ID=R7Oodxxx
COLLECTION_DOC_URL=https://www.feishu.cn/docx/R7Oodxxx
FEISHU_IDENTITY=bot
WECHAT_FETCH_SCRIPT=/path/to/wechat_fetch_v2.py
```

## 执行流程

### 1. 提取内容（按优先级执行，不走弯路）

**⚠️ 关键原则：优先用验证过的可靠方式，只有不行了才去探索。**

| 优先级 | 来源类型 | 提取方式 | 说明 |
|:---:|---------|---------|------|
| 1️⃣ | 微信公众号链接 | `wechat_fetch_v2.py` 或类似脚本 | 微信有反爬验证墙，通用工具抓不到 |
| 2️⃣ | 普通网页链接 | `fetch_web` 或 `curl` | 通用网页抓取 |
| 3️⃣ | 对话中的内容 | 从上下文提取 | 直接整理 |
| 4️⃣ | 用户上传的文件 | `parse_file` | 解析文件内容 |
| 🔴 | 以上都失败 | 云手机/浏览器（兜底） | 用 `mobile_use` 打开链接获取内容 |

**微信文章说明**：
- 微信文章有反爬验证墙，`fetch_web` 无法获取（返回空白或验证页）
- **必须直接用专用脚本**，不要先试 fetch_web 再绕路
- 推荐脚本：[wechat-article-to-md](https://github.com/likemaoke/wechat-article-to-md)
- 脚本输出 Markdown 文件 + images 目录，读 Markdown 文件即可获取全文
- 短时间频繁请求会触发验证码，建议间隔10分钟以上

### 2. 整理收藏格式
每条收藏记录必须包含以下结构：

```markdown
## YYYY-MM-DD | 标题

### 原始出处
[链接或来源描述]
作者/发布时间（如有）

---

### 5-Why 分析

**问题：[核心问题]**

1. **Why 1** → [第一层原因]
2. **Why 2** → [第二层原因]
3. **Why 3** → [第三层原因]
4. **Why 4** → [第四层原因]
5. **Why 5** → [第五层原因/根本原因]

**核心洞察**：[一句话总结]

---

### 简要分析/表格对比
[如果原文有分析或表格，提取关键内容]
[如果没有，则用自己的理解进行简要分析]

---

### 关键启发
1. [要点1]
2. [要点2]
3. [要点3]
（根据内容提炼）

---
```

### 3. 追加到飞书文档
使用 `lark_cli` 命令追加内容：

```bash
lark-cli docs +update --doc "$COLLECTION_DOC_ID" --mode append --as "$FEISHU_IDENTITY" --markdown "内容"
```

**身份选择**：
- `--as bot`：用机器人身份写入（文档由bot创建时必须用这个，否则会报 forbidden）
- `--as user`：用用户身份写入（默认）

> 💡 **踩坑经验**：如果写入报 forbidden，大概率是身份不对。文档是谁创建的就用谁的身份写入。

### 4. 反馈用户
告知用户收藏成功，并提供文档链接。

## 记录原则

### 必须记录
- **原始出处**：链接、作者、发布时间
- **5-Why 分析**：深度挖掘问题本质，至少3层，最多5层
- **核心洞察**：一句话总结

### 可选记录
- 大表格对比（如果原文有）
- 详细分析（如果原文有）
- 关键启发/要点（提炼3-5条）

### 记录风格
- 简洁清晰，不冗余
- 保留原文核心观点
- 如原文已有深度分析，直接引用而非重复

## 注意事项
1. 5-Why 分析要结合内容本身，不要生搬硬套
2. 如果内容不适合做5-Why分析，可以用其他结构化方式（如SWOT、PEST等）
3. 追加前确认内容完整性，避免多次追加同一内容
4. 使用 `append` 模式追加，不要覆盖原有内容
5. 微信文章直接用专用脚本，不要先用通用工具试错
6. 飞书文档写入注意身份（bot vs user），避免 forbidden 错误
7. 私人配置放 `.env.local`，不要提交到版本库

## 依赖
- **lark_cli**：飞书文档操作
- **微信文章提取脚本**：推荐 [wechat-article-to-md](https://github.com/likemaoke/wechat-article-to-md)
- **fetch_web**：通用网页抓取（内置工具）
- **parse_file**：文件解析（内置工具）
