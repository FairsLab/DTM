# DTM (Data on the Move)

## 项目简介
DTM（Data on the Move）项目旨在通过数据交易和分析，优化城市交通系统。该项目结合SUMO交通流仿真和智能数据定价算法，通过交通信号灯与车辆间的数据交易，提高交通效率。

## 功能特点
- 使用SUMO模拟城市主干道交通流和事故。
- 信号灯与车辆间进行数据交易，包括事故信息和交通流数据。
- LLM（Large Language Model）用于数据定价和交易。
- 构建历史数据库，用于交易分析和系统优化。

## 安装和使用
1. 克隆仓库：`git clone https://github.com/FairsLab/DTM.git`
2. 安装依赖：详见`requirements.txt`
3. 运行SUMO仿真：参考`sumo_simulation_guide.md`
4. 数据定价和交易：运行`trade_simulation.py`

## TODO 列表
- [ ] 完善`evaluate`函数（输入：data + preference，输出：price, data description, reason）。
- [ ] 对齐SUMO中获取的数据和trading.py中数据格式。
- [ ] 系统的数据流转图（包括交易平台）
- [ ] 构建交易系统的历史数据库。

## 实验场景和流程
- 双向4车道城市主干道仿真。
- 信号灯购买车辆数据，使用代币作为交易媒介。
- 数据价值提升时，为控制器提供激励。
- 交通效率提升时，系统为控制器提供反馈激励。

## 贡献指南
欢迎通过Issue和Pull Request参与项目贡献。请遵循我们的代码规范和贡献指南。

## 许可
本项目遵循MIT许可。详见`LICENSE`文件。

## 联系方式
有关项目的任何疑问，请联系[项目维护者](test)。

---
