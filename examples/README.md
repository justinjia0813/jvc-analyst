# 示例怎么使用

这里的公司和数字均为虚构，只用于说明交付格式和验证计算。不能作为行业或项目证据。

- `market-sizing-example.xlsx`：带假设、双路径计算、差异对账和来源的市场模型。
- `roi-modeler-example.xlsx`：普通股、一次后续融资、无跟投、三情景退出的回报模型。全部金额为万元，现金流按年末口径。
- `comps-dd-example.xlsx`：一家公司构成的最小可比表，不表示覆盖了市场。
- `*.checks.json`：独立给定的基准结果，以及修改一个输入后应得到的结果。
- `portfolio-cash-input.json`：经营现金流为正，但设备支出和到期还款使现金不足的情景。融资只在单独情景中到账。

修改输入前先复制文件。Excel 计算验证需要本机 LibreOffice；脚本在临时目录重算，不改原文件。安装器只注册 Skill，不安装文档或计算依赖。

维护者可运行 `python3 scripts/build-workbook-examples.py` 重建这三个工作簿，再运行 `bash scripts/check-excel-workbooks.sh` 验证。
