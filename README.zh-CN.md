# Plimsoll

**一套"每个数字都能查账"的参数化船舶性能计算工具。** Plimsoll 对参数化船体计算静水力、稳性、载荷、进水与破损，
并记录**每个数值的来源**：每个内核带方法版本，每个值带 `source` 与 `estimate` 标记，输入缺失处的量明确保持未知。

它由两部分组成：Python 计算核心 + 命令行界面，以及构建在其上的**中英双语网页工作台**——项目修订、计算运行、
可切换显示单位的报告与 JSON/CSV 导出，还有一个用于命中研究的破损实验室。

**授权：MIT**（`LICENSE`，版权 2026 Yang Rui）。第三方组件与随仓库分发的素材见 `THIRD-PARTY.md`。

## 它为什么存在

多数工程计算器给你一个数字，把推理过程藏起来。Plimsoll 反过来做：

- **未知就是未知。** 没人提供的量是 `null`，不会塞一个"看起来合理"的默认值，也绝不悄悄变成 0。
- **每个值都带出处。** 内核有版本号（`connected-quasi-static-flooding-3`、`holtrop_mennen_1982` …），数据带
  `source` / `estimate` 标记，因此"工程代理值"永远不会被误当成实测值或史实验证值。
- **对照拒绝说谎。** 两次运行**只有口径一致**（修订、工况、方法版本）才给差值；每个格子的状态明确是
  `已知 / 未知 / 未请求 / 不可比`；方向一律写明（B − A）；未知操作数得到的是未知差值，而不是零。
- **解释只从记录推导，不解析文案。** 实验室对受损目标的解释来自已记录的破片路径、舱壁响应与已接受事件；
  它绝不解析日志文本，**起爆之前被接受的帧也不会泄露后来发生的事**。
- **验证随代码一起发布。** 独立预言机、收敛研究与已记录的核心验证报告都在仓库里。

## 快速开始

核心需要 **Python 3.12+，不需要任何第三方库**：

```bash
python tools/plimsoll/cli.py --help
python tools/plimsoll/cli.py tools/plimsoll/cases/generic_test_steamer_1910.json
python tools/plimsoll/run_all_tests.py        # 核心回归
```

安装形式（会同时在 PATH 上提供 `plimsoll` 命令）：

```bash
pip install -e .          # 在仓库根目录
plimsoll --help
```

网页工作台需要 Node.js 与 Python 环境：

```bash
pip install -e .                                  # 先装核心：服务端会 import 它
cd web/frontend && npm ci && npm run dev          # http://127.0.0.1:5173
cd web/backend  && pip install -e '.[dev]' && alembic upgrade head
cd web/backend  && pytest
```

开发时 Vite 必须占用 5173 端口：服务端允许的来源被钉在该端口上。生产形态（PostgreSQL、nginx、容器）见 `web/deploy/`。

## 目录

| 路径 | 内容 |
|---|---|
| `tools/plimsoll/` | 计算核心与 CLI，含测试套件与合成案例 |
| `web/frontend/` | React 工作台、破损实验室与公开外壳（Vite + TypeScript） |
| `web/backend/` | FastAPI 服务：项目、修订、运行、worker |
| `web/deploy/` | 容器、nginx 模板与发布构建材料 |
| `web/dev/` | 用于离线工作的匿名模式本地服务 |
| `docs/plimsoll-1.0/` | 规格、当前状态与工程证据 |
| `data/` | 核心读取的装甲标准数据集 |

## 状态

Alpha，并且如实说明。核心回归共 **592 个测试**；其中 4 个在任何"包不可作为 `tools.plimsoll.*` 导入"的环境里会失败——
这是测试运行器的既有性质（作者私有仓库里同样如此），不是回归。网页两套皆绿：**前端 792 个测试**，
**服务端 109 通过、4 跳过**（跳过的是依赖本仓库未携带的大型内联几何夹具的用例）。

**结果是工程估算。** 这里没有任何数值经过船级社认可、实测或实验验证，界面在需要说明的地方都写明了这一点。

## 本仓库刻意不含的内容

历史舰船案例数据（以及锚定其上的测试）、游戏/三维建模素材、项目内部开发记录，都留在作者的私有仓库中。
这里是通用工具，附合成研究案例。

## 授权与第三方

MIT —— 见 `LICENSE`。随仓库分发的字体为 SIL OFL 1.1 并附带许可全文；交互音效是本项目的原创作品；
依赖许可列于 `THIRD-PARTY.md`，其中包括唯一的非宽松许可依赖（**psycopg，LGPL-3.0-only**，以已安装库的方式使用，
并未链接进 Plimsoll 自身源码）。

部分计算数据由作者从大学教材摘录，文件自身写明了出处。例如 `tools/plimsoll/cases/taylor_gertler_cr_table.json` 记录了
*Molland, Turnock & Hudson, Ship Resistance and Propulsion*，附录 A3，表 A3.8–A3.11（第 495–498 页）。

## 参与贡献

见 `CONTRIBUTING.md`，贡献按 MIT 授权接受。最重要的三条约定：数字保持诚实（未知就是未知）、
面向用户的文案两种语言都要写、**能被测量的说法就去测量**。

[English README](README.md)
