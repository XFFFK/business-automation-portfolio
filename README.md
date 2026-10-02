# Business Automation Portfolio

A small, reproducible portfolio of business-facing automation projects for career transition roles such as product operations, process operations, operations analysis, and project delivery.

这组项目展示如何把运营问题拆成流程、规则、数据质量检查和带证据的决策材料。项目使用本地合成数据，重点是可运行、可解释、可复现。

## Projects

| Project | What it demonstrates | Validation |
| --- | --- | --- |
| [Priority workflow](project1_workflow/) | CSV intake, P0–P3 triage, deadline risk, Markdown and JSON reports | 8 standard-library tests |
| [Data quality report](project2_quality_dashboard/) | Required-field checks, duplicate detection, status/date validation, HTML and JSON output | 7 seeded issues across 5 rule types |
| [Cited document assistant](project3_report_assistant/) | Local paragraph retrieval, citation links, explicit no-evidence response | 4/4 fixed evaluation cases |

## Quick start

The projects do not require network access or paid APIs.

```powershell
cd project1_workflow
python -m workflow demo --out out --date 2026-10-02
python -m unittest discover -s tests -q

cd ../project2_quality_dashboard
python quality_dashboard.py sample/orders.csv --output quality-report.html --json quality-report.json
python -m unittest discover -s tests -q

cd ../project3_report_assistant
python evaluate.py
python -m unittest discover -s tests -q
```

Each project has its own README, sample inputs and boundaries. The full planning and evidence rules are in [PLAN.md](PLAN.md), and resume wording is in [RESUME_DRAFT.md](RESUME_DRAFT.md).

## Why this portfolio exists

The projects are deliberately small enough to explain in an interview and complete enough to run from a clean checkout. They focus on problem definition, workflow design, data quality, traceability and validation rather than inflated production claims.

All data and results in this repository are synthetic or local test outputs. They do not represent customer adoption, business savings, revenue impact or production scale.

## License

MIT. See [LICENSE](LICENSE).
