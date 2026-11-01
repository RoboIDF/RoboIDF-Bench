# RoboIDF-Bench

2026-11-01：软件／仿真评测开发版。**v0.2 未发布，M2/M4 真机与数字孪生验收仍待证据。**

```bash
pixi install --locked
pixi run --locked test
pixi run --locked demo-all
```

Linux x86_64 / Python 3.12，全部依赖由 Pixi 锁定；Core 固定 Git 提交，单独克隆可运行。

- `pixi run demo`：M0 三组真值的独立参数与回放误差，错误模型和无激励拒绝，见 [M0协议](docs/m0.md)。
- `pixi run compare-demo`：M3 基线与 SciPy 后端的对照，包括连续系统、噪声、失配及零激励；见 [对照协议](docs/comparison.md)。
- `artifacts/`：可重生成的 JSON 报告，记录配置、种子、数据哈希、模型、误差和失败原因。

训练、开发验证与最终测试分离。最终测试数据不进入优化器或激励选择；不能靠更换测试种子或放宽阈值掩盖失败。合成噪声测试不能推断真实机器人性能，连续系统仿真不等于跨机器人引擎验收。

本轮不提供真实数据集、Agent对照或真机成绩。[Core](https://github.com/RoboIDF/RoboIDF) · [Ecosystem](https://github.com/RoboIDF/RoboIDF-Ecosystem) · [贡献指南](CONTRIBUTING.md)。项目许可证待确定。论文工作已停止；[旧说明](docs/pre-m0-status.md)仅作历史参考。
