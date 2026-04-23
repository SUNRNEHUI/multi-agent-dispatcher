# Multi-Agent Dispatcher Example

> 演示完整的任务调度流程

## 任务依赖图

```
T1-1 (设计登录页面布局)
   ├── T2-1 (实现登录表单)
   │      └── T3-1 (实现用户资料页面)
   └── T2-2 (实现注册表单)
          └── T3-2 (实现密码重置页面)
```

## 并行执行矩阵

| 阶段 | 任务 | 并行数 |
|------|------|--------|
| Phase 1 | T1-1 | 1 |
| Phase 2 | T2-1, T2-2 | 2 |
| Phase 3 | T3-1, T3-2 | 2 |

## 使用方法

### 1. 初始化调度器

```bash
cd example
mkdir -p SUMMARY CACHE LOGS
# TASKS.json 已预置
```

### 2. Master Agent 启动调度

```
用户: 开始执行计划
Master Agent:
1. 读取 TASKS.json
2. 扫描 pending 任务
3. 发现 T1-1 无依赖，可运行
4. 启动 T1-1 子 agent
```

### 3. 子 Agent 执行并返回摘要

```bash
# 子 agent 完成后写入摘要
cat > .dispatcher/SUMMARY/T1-1.json << 'EOF'
{
  "task_id": "T1-1",
  "status": "completed",
  "result": "登录页面布局设计完成",
  "artifacts": ["src/auth/LoginPage.tsx"],
  "confidence": "high"
}
EOF
```

### 4. Master Agent 验证并继续调度

```
Master Agent:
1. 读取 T1-1 摘要
2. 验证产物存在
3. 标记 T1-1 为 completed/verified
4. 扫描发现 T2-1, T2-2 可运行
5. 并行启动 T2-1, T2-2
```

## 文件结构

```
example/
├── .dispatcher/
│   ├── TASKS.json          # 任务状态机
│   ├── SUMMARY/            # 子 agent 摘要
│   │   └── T1-1.json
│   ├── CACHE/              # 结果缓存
│   └── LOGS/               # 审计日志
└── src/
    └── auth/               # 产物目录
```

## 验证命令

```bash
# 查看可运行任务
jq '[.tasks[] | select(.status == "pending") | select(
  [.tasks[] | select(.id == .depends_on[]).status] | all(. == "completed" or . == "verified")
)]' .dispatcher/TASKS.json

# 查看任务状态
jq '.tasks[] | {id, status, depends_on}' .dispatcher/TASKS.json
```
