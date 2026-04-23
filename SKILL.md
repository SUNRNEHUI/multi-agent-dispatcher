---
name: multi-agent-dispatcher
description: Use when user says "帮我计划一下" or "做XXX" that requires multi-task splitting — breaks down tasks to TASKS.json, auto-dispatches sub-agents, manages entire flow without interruption.
---

# Multi-Agent Task Dispatcher

> 计划落盘 + 自动调度 + 干净上下文 = 主 agent 全程控制不中断

## 核心目标

- **计划落盘**：拆分任务 → TASKS.json（不放上下文，防止丢失）
- **自动执行**：无需用户确认，主 agent 直接调度
- **上下文干净**：子 agent 只看到最小输入
- **全程控制**：主 agent 管理、合并、调度、检查整个流程

## 触发条件

| 用户表达 | 动作 |
|---------|------|
| "帮我计划一下" | 拆分任务 → TASKS.json → 开始调度 |
| "做XXX"（需要多步骤） | 拆分任务 → TASKS.json → 开始调度 |
| "开始执行" | 检查 TASKS.json → 继续调度 pending 任务 |
| TASKS.json 存在 + 有 pending | 继续调度 |

## 执行流程

```
用户: "帮我计划一下做一个待办应用"

主 agent:
1. 拆分任务到 TASKS.json（落盘，不放上下文）
2. 扫描可运行任务
3. 自动启动子 agent（无需确认）
4. 监控完成状态
5. 验证结果
6. 继续调度下一批，直到全部完成
7. 合并结果，向用户报告
```

## 文件结构

```
project/
├── .dispatcher/
│   ├── TASKS.json              # 任务状态机（SSOT）
│   ├── SUMMARY/                # 子 agent 摘要
│   ├── CACHE/                 # 结果缓存（加速重跑）
│   └── LOGS/                  # 审计日志
└── src/                       # 实际代码
```

## 任务状态机

```
pending → running → completed/verified
                    ↘ failed → retry (最多 3 次)
                              → blocked (依赖失败)
                              → fatal (需要人工介入)
```

### 状态流转规则

| 状态 | 含义 | 流转条件 |
|------|------|----------|
| `pending` | 待执行 | 依赖全部完成 |
| `running` | 执行中 | 启动子 agent |
| `completed` | 已完成 | 子 agent 返回成功 |
| `verified` | 已验证 | Master 质量检查通过 |
| `failed` | 失败 | 子 agent 返回错误 |
| `blocked` | 阻塞 | 依赖任务失败 |
| `fatal` | 致命 | 重试超过上限 |

## 调度算法

### Step 1: 任务拆分（用户说"计划"时）

```bash
# 用户需求 → 输出 TASKS.json
cat > .dispatcher/TASKS.json << 'EOF'
{
  "version": "1.0",
  "created_at": "...",
  "scheduler": {
    "max_parallel": 3,
    "retry_policy": { "max_attempts": 3, "backoff_seconds": [5, 25, 125] }
  },
  "tasks": [
    {"id": "T1-1", "description": "...", "status": "pending", "depends_on": [], "priority": 1}
  ]
}
EOF
```

### Step 2: 扫描可运行任务

```bash
# 过滤 pending + 依赖满足 + 无锁冲突
jq '[.tasks[] | select(.status == "pending") | select(
  [.depends_on[] as $d | .tasks[] | select(.id == $d) | .status] | all(. == "completed" or . == "verified")
)]' .dispatcher/TASKS.json
```

### Step 3: 自动调度（无需确认）

主 agent 直接：
1. 启动子 agent 执行任务
2. 更新状态为 running
3. 记录到 audit_log

### Step 4: 监控完成

等待子 agent 完成 → 读取 SUMMARY → 验证 → 更新状态

### Step 5: 继续调度

扫描新一轮 pending 任务 → 重复 Step 3-4 直到全部完成

## 质量验证

| 验证项 | 方式 |
|--------|------|
| 格式验证 | summary.json 符合 schema |
| 产物验证 | artifacts 存在且非空 |
| 逻辑验证 | （可选）lint/test |

## 失败处理

| 错误类型 | 处理 |
|----------|------|
| `retryable` | 指数退避重试（5s → 25s → 125s） |
| `fatal` | 标记 fatal，通知用户 |
| `blocked` | 依赖失败，等待解决 |

## 模板文件

- `master-prompt.md` - Master Agent 调度逻辑（含任务拆分）
- `sub-prompt.md` - Sub Agent 执行规范
- `TASKS.schema.json` - 任务定义 Schema
- `summary.schema.json` - 摘要 Schema

## 初始化脚本

```bash
# 创建调度器目录
mkdir -p .dispatcher/SUMMARY .dispatcher/CACHE .dispatcher/LOGS
```

---

*Multi-Agent Dispatcher v2.0 | 2026-04-23*