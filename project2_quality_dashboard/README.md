# 运营数据质量报告

这个项目把一份订单 CSV 转成可解释的数据质量报告，面向运营或业务分析场景。示例数据是合成数据，故意包含重复订单、缺失字段、非法状态、负金额和非法日期。

## 运行

```powershell
python quality_dashboard.py sample/orders.csv --output quality-report.html --json quality-report.json
```

打开 `quality-report.html` 可以查看摘要和逐行问题。规则写在 `quality_dashboard.py` 的 `inspect_rows` 中，方便面试时解释每条指标的定义。

## 可展示的能力

- 把业务口径转成可执行的数据质量规则
- 同时输出给人看的 HTML 和给系统使用的 JSON
- 使用固定的异常样本验证规则是否识别问题

项目没有线上数据，也没有把模拟发现表述成业务节省或收入增长。

