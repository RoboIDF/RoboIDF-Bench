# M0 之前的历史说明

以下状态仅代表 M0 实现前，请以仓库 README 为准。

# RoboIDF-Bench

更新日期：2026-11-01。状态：评测规划与 Pixi 基础环境；尚无评测实现、数据集或成绩。

[项目群总览](https://github.com/RoboIDF/RoboIDF/blob/main/docs/overview.md) · [主项目](https://github.com/RoboIDF/RoboIDF) · [社区项目](https://github.com/RoboIDF/RoboIDF-Ecosystem)

## 论文草稿

[论文目录与待补证据](papers/README.md) · [RoboIDF-Bench 中文完整初稿 v0.1](papers/roboidf-bench-draft.md)

2026-11-01：已形成研究协议初稿，覆盖四套件、指标、统计、公平对照与复现要求。
草稿中的合同字段和验收细则是待评审提案，社区等级沿用 Ecosystem 的 L0–L3；实验表均为待测，尚无评测实现、数据集或成绩。

## 定位

定义“什么叫做成功”，为辨识后端、Agent Harness 和社区适配提供独立、可复现的验收协议。
评测器应独立于 Agent 的任务完成声明，不能把成功生成模型文件视为辨识成功。

## 四类评测套件

| 套件 | 输入与任务 | 核心指标 |
|---|---|---|
| A Synthetic | 已知真值的仿真系统及噪声/失配条件 | 可辨识参数恢复误差、收敛、鲁棒性、不可辨识与失配检测 |
| B Offline Real Robot | 固定真实数据、明确训练与独立测试轨迹 | 位置/速度 RMSE、时延误差、频率响应、长期回放误差 |
| C Agentic SysID | 相同初始模型、实验限制与资源预算 | 达标实验次数/时间、误差、人工干预、完成与恢复率、预算和安全事件 |
| D Model & Compatibility | 组件装配、Adapter 与模型产物 | 合同符合性、是否需修改 Core、独立加载、跨引擎动态误差、复现完整度 |

Cross-Simulator 验证属于 D，并与 B/C 的动态误差协议共用定义。
只有可辨识且物理含义匹配的参数才比较真值恢复误差；等效参数应按其声明的预测目标验证。

## 对照与公平性

计划比较原始模型、固定实验 Traditional SysID、信息驱动 Active SysID、
不使用 Agent 的预定义工作流、完整 Harness，以及条件允许时的人类专家。
隔离实验选择的贡献时保持同一优化器、数据权限和预算；专家采用的方法另行记录。

每次评测固定数据版本与哈希、随机种子、初始模型、配置、后端版本、控制模式、
指标单位、聚合规则、停止条件与资源预算。时间和计算成本分别记录。
将训练、开发验证与最终测试分离；最终测试集不向 Agent 开放迭代反馈。
真实阈值需在实验前声明，当前不编造阈值或基线成绩。

报告至少包括误差、实验成本、人工成本、失败原因、置信或不确定性说明及安全违规记录，
不以未经论证的单一加权总分替代各维度结果。

## 与其他项目的合同

- 消费 RoboIDF 版本化任务、运行记录、模型和数据合同；协议指标由本项目负责。
- 给 Ecosystem 提供适配验收与数据/模型报告要求。
- 将失败案例和回归用例反馈给 Core，但不得靠修改测试集掩盖失败。

## 环境与操作

本仓库独立维护 `pixi.toml` 和 `pixi.lock`，无需父目录或其他项目即可安装。
当前仅配置 linux-64 / Python 3.12；尚未安装或验证机器人 SDK 与辨识后端。

```bash
pixi install --locked
pixi run --locked info
pixi run --locked python --version
```

在本仓库执行以上命令。通过 `pixi add <package>` 或 `pixi add --pypi <package>`
添加依赖，清单与锁文件一起提交；不提交 `.pixi/`。`info` 只展示本文，不执行辨识。

## 当前进展与下一步

- 已建立：A–D 套件边界、对照原则、环境配置和项目文档。
- 已验证（2026-11-01）（迁移前记录）：工作区环境安装成功；`info` 与本文一致；锁定环境运行 Python 3.12.16，解释器位于工作区对应环境。
- 待实现：M0 指标规范、数据切分合同、最小合成任务及报告格式。
- 随后：合成回归 → Wuji/Tianji 离线数据 → Agentic 对照 → 跨引擎及社区兼容性。
- 验证边界：本轮只检查环境和文档入口；尚未运行任何辨识评测。
- 后续修改协议、指标或数据切分时更新本文；跨项目合同及里程碑变化同步根 README。

## 仓库与发布范围

仓库：https://github.com/RoboIDF/RoboIDF-Bench 。首次提交仅包含规划文档、维护约定与 Pixi 配置。
当前未选择项目许可证；公开可见不代表已授予开源再分发许可。

2026-11-01 独立仓库验证：`pixi install` 成功，`pixi run --locked info` 与 README 一致；Python 解释器位于本仓库 `.pixi/envs/default`，仓库内文档链接检查通过。

## LaTeX 科研写作环境

见 [写作与编译说明](paper/README.md)。使用 `pixi run --locked paper-build` 生成 LaTeX、PDF 与 Overleaf 导入包；使用 `pixi run --locked paper-check` 检查引用和输出。

2026-11-01：本地 LaTeX 编译与 PDF 检查通过；已检查全部页面排版。Overleaf 项目链接已收到，导入与同步尚未完成，具体状态见写作说明。

GitHub Actions 自动编译已启用，2026-11-01 首次运行通过：[验证记录](https://github.com/RoboIDF/RoboIDF-Bench/actions/runs/41294469437)。论文、脚本或环境变更会自动编译、检查并上传产物。Overleaf 仍待有效 Git 认证。
