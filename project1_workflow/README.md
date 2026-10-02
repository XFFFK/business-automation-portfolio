# Project 1：业务事项优先级与日报工作流

这是一个面向运营/项目协调场景的最小自动化工具：把 CSV 里的事项导入，按固定规则计算优先级和截止风险，再同时输出适合人阅读的 Markdown 日报与适合后续系统消费的 JSON 结果。

项目刻意只使用 Python 标准库，规则是确定性的，`--date` 可以固定参考日期，所以示例和测试可以复现。

## 快速演示

在本目录执行：

```powershell
python -m workflow demo --out out --date 2026-10-02
```

命令会生成：

- `out/demo_tasks.csv`：合成输入数据
- `out/daily_report.md`：日报和行动队列
- `out/daily_result.json`：汇总指标及每条事项的分类结果

处理自己的 CSV：

```powershell
python -m workflow run --input sample_tasks.csv --out out --date 2026-10-02
```

输入必须包含 `id,title,owner,due_date,status,impact` 六列。`due_date` 使用 `YYYY-MM-DD`；状态为 `open`、`in_progress`、`blocked` 或 `done`；影响为 `low`、`medium` 或 `high`。截止日期可以留空。

## 规则

- `P0`：已阻塞或已逾期；风险分别为 `blocked` / `overdue`。
- `P1`：距离截止日 0–2 天，风险为 `due_soon`。
- `P2`：距离截止日 3–7 天，或影响为 high，风险为 `watch`；无截止日期时风险为 `missing_due_date`。
- `P3`：其余未完成事项，风险为 `on_track`。
- 已完成事项标记为 `done/closed`，始终排在行动队列末尾。

## 测试

测试只验证核心规则、输入校验和两个输出格式，不依赖网络或外部服务：

```powershell
python -m unittest discover -s tests -q
```

## 可写入简历的表述（基于本项目真实实现）

> 使用 Python 标准库实现 CSV 事项导入与规则化工作流：按状态、影响和截止日期自动分级 P0–P3，生成可读 Markdown 日报及结构化 JSON 结果；通过可注入参考日期和 8 项自动化测试保证结果可复现。

## 当前边界

这是一个可演示的离线流程原型，不包含数据库、登录、消息推送或真实业务数据；这些可以作为后续项目迭代，而不影响本项目的核心演示。

