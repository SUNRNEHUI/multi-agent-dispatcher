# Multi-Agent Dispatcher

简体中文 | [English](README.md)

**一个多智能体任务路由 skill：先判断 Direct / Lite / Full，再决定是否真的调度多个 agent。**

> v5.2.1：适合公开分享的版本。它补充了对 `obra/superpowers` 的明确借鉴声明，收紧了 `SKILL.md` 的触发描述，并新增干净 runtime-only 打包脚本。

---

## 它解决什么问题

多 agent 任务最容易失败在这些地方：

- 主 agent 在长上下文后丢失状态。
- 子 agent 编辑范围重叠，最后合并冲突。
- 子 agent 报告变成聊天记录，不能复用和验收。
- worker 说完成了，但实际还有 stub、TODO、mock 或未验证路径。
- 高风险操作没有停止点、回滚路径和证据。

这个 skill 的核心不是“只要用户说多 agent 就开多个 agent”，而是先选模式：

- **Direct：** 小任务、单文件改动、简单命令、窄范围 bug。单 agent 直接做并验证。
- **Lite：** 中等任务，有清楚拆分面，但不需要完整持久化 harness。用短计划、清楚 owner、必要证据。
- **Full：** 长任务、高风险、可续跑、多阶段、需要 evaluator、worktree 隔离或完整验收证据。才启用完整 harness。

主 agent 永远负责模式判断、调度、合并、验证和最终结论。子 agent 只负责边界清楚的局部任务。

---

## 用户收益

### 长任务可续跑

Full Harness 会把任务状态写到 `<project>/workspace/<task-slug>/`，包括 spec、progress、worker report、acceptance registry、trace 等。后续 agent 可以从文件继续，而不是从聊天记录猜。

### 不会过度调度

显式说“多智能体”只代表授权评估，不代表一定开多个 agent。小任务会走 Direct。

### 验收有证据

worker 的“已完成”不是最终完成。最终完成需要测试、build、lint、浏览器验证、API readback、日志、截图、CI 或 evaluator 报告等证据。

### 适合工程闭环

Full Harness 包含：

- Capability Gate：确认当前运行时真的有什么能力。
- State Machine：记录任务状态，不靠聊天漂移。
- Acceptance Registry：每条验收标准绑定证据。
- Budget Circuit Breaker：时间、上下文、重试、成本超界时停下来。
- Trace：记录关键决策、命令、证据和 stop reason。

---

## 什么时候用

当用户明确要求这些内容时使用：

- 多智能体 / 多 Agent
- sub-agent / 子 agent
- 并行 agent
- delegation / 委托
- DAG 调度
- 分头处理 / 分别派 / 拆给不同 agent
- worktree-based parallel execution
- 需要可续跑、可验收证据的长任务

不要因为任务“大”就自动使用。没有用户授权多 agent 时，最多简短建议，默认按普通单 agent 工作流推进。

---

## 运行机制

```text
Context Intake
-> Mode Selection: Direct / Lite / Full
-> Execute the selected mode
   Direct: 直接做、验证、汇报
   Lite: 轻量拆分、短报告、必要证据
   Full: capability gate、acceptance registry、state machine、trace、evaluator
-> Merge / Handoff
```

---

## 安装

先生成干净 runtime 包：

```bash
python3 scripts/package_skill.py --output /tmp/multi-agent-dispatcher-runtime --force
```

再安装到 Codex：

```bash
mkdir -p ~/.codex/skills/multi-agent-dispatcher
rsync -a --delete /tmp/multi-agent-dispatcher-runtime/ ~/.codex/skills/multi-agent-dispatcher/
```

使用示例：

```text
这个项目有前端、后端、测试三块，帮我用多个 agent 并行做，但要有验收证据。
```

---

## 和 Superpowers 的关系

本项目是独立 skill，不依赖 Superpowers 运行。

我们明确借鉴了 [obra/superpowers](https://github.com/obra/superpowers) 中一些成熟工程方法，包括：

- test-first evidence
- fresh-context subagents
- review gates
- worktree isolation
- verification-before-completion

但本项目不复制 Superpowers 的 skill 正文，也不要求用户安装 Superpowers 插件。这里的关系是：

```text
multi-agent-dispatcher = 总入口 / 路由器
Superpowers-style methods = 可选的支持方法
```

也就是说，先由本 skill 判断 Direct / Lite / Full，再决定是否借用 TDD、review、worktree、verification 等方法。

---

## 分享给别人应该包含什么

分享 GitHub repo 时可以包含完整项目文档和工具。

别人真正安装到 runtime skill 目录时，只需要：

- `SKILL.md`
- `master-prompt.md`
- `sub-prompt.md`
- `agents/openai.yaml`
- `adapters/`
- `references/`
- `templates/`
- `scripts/init_run.py`
- `scripts/validate_report.py`

不要把这些放进 runtime 安装目录：

- `.git`
- `README.md`
- `scripts/package_skill.py`
- 本地 memory
- session 日志
- 生成过的 workspace artifacts
- `__pycache__`
- 私人配置
- API key / 凭据

`scripts/package_skill.py` 会自动生成干净 runtime 包。

---

## v5.2.1 更新内容

- 明确声明本项目独立运行，并借鉴了 `obra/superpowers` 的工程方法。
- 收紧 `SKILL.md` frontmatter，只写触发条件，避免把流程摘要塞进 metadata。
- 新增 `scripts/package_skill.py`，用于生成干净 runtime-only 安装包。
- README 默认提供中英双语说明。

## v5.2.0 累计更新

- 保留 `multi-agent-dispatcher` 作为唯一入口。
- 吸收 Superpowers-style 的 TDD、review、fresh-context、verification 思路。
- 新增 Lite / Full 中的 testing 和 review gates。
- 新增更多 eval cases，覆盖 TDD evidence、two-stage review、Superpowers interaction 和 clean sharing。

## v5.1.0 累计更新

- 新增 Direct / Lite / Full 三模式路由。
- Full Harness 不再是默认路径，只在长任务、高风险、可续跑时启用。
- 中小任务避免生成过多 artifacts。

---

## 版本

**v5.2.1** · 2026-05-28

上一公开版本：**v5.0.1** · 2026-05-27
