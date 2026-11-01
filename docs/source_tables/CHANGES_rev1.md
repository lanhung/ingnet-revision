# rev1 改动说明（2026-09-28）

旧代码（utils.py / train.py / test.py / configs/*.json）和旧的 outputs/ **一律不动**。rev1 是一个独立目录，产出只写到 `outputs_rev1/`。

## 审稿意见 / 审计发现 → 代码改动

| 编号 | 问题 | rev1 的做法 | 位置 |
|---|---|---|---|
| #1 / 审计 B1 | 没给 τ、带宽、窗；代码里每段恰好 1 个 burst，长度 0.2ξ·T | 按论文 Eq.(1)(2) 实现：到达时间是 Poisson 过程；τ 固定为 4 ms（8 个采样点）；ξ = Rτ；每个事件是 Hann 窗白噪声，限带 20–1000 Hz；每段期望事件数 ≈ 1000ξ | `utils_rev1.Simulator.draw_signal` |
| #2 / 审计 B2 | 式(8)量纲不对，信号方差多乘了 f_s | σ1² = ∫S_gw/P_n df / (1000−20)；每个事件的方差为 (Ω/ξ)σ1²，时间平均方差为 Ωσ1² | `calibration_sigma1` |
| 新发现 | 旧白化会把 15 Hz 以下的残余放大，每段功率大幅起伏（合成数据上达到 ±0.5 dex），且用含首尾瞬态的 std 归一化 | 白化后限带 20–1000 Hz，去掉首尾各 16 s，按主体 std 归一化；每段方差起伏降到约 0.01 dex | `whiten_block` |
| #5 | 训练 / null / CFAR / 注入都用同一段数据 | 前 75% 用于训练，后 25% 用于 CFAR、null 和注入，中间隔 8 s；两段各自估 PSD 并白化 | `prepare_dataset` |
| #6 | ξ 先验在线性尺度上均匀 | θ = (log10Ω, log10ξ)，log10ξ 在 [−3, 0] 上均匀 | 配置 + `train_rev1` |
| #4 / 审计 B3 | Trad-FR 没有功率信息 | 32 个频段的相干性 + 32 个频段的 log10(P_H·P_L)，共 64 维 | `compute_fr_features` |
| #11 | 需要把注入方式的影响单独拆出来 | 新增 `rev1_identical.json`：和 antenna 配置只差 mode 这一项 | configs |
| 次要：CFAR | 99.7% 阈值只用了 500 个样本 | n_calib = 10000，并用 bootstrap 给出阈值不确定度 | `calibrate_cfar` → `cfar.json` |
| 次要：s(x) | 未定义 | s(x) = 200 个 flow 样本中 log10Ω 的均值，不做先验截断；所有管线的 CFAR 和注入都用同一个定义 | `detection_statistic` |
| 审计 B4 / B11 | 发散的 run 被静默剔除；聚合时"取最新一轮" | 每个 (配置, 数据集, seed) 只允许有一个 run；聚合同时给出"全部"和"剔除发散"两版，并单独列出发散清单 | `sweep_rev1.py` |
| 审计 B13 | 读数据失败时悄悄换成白噪声 | 删掉 try/except，失败直接报错；run_meta 里记录数据文件的 sha256 | `prepare_dataset` |
| #9 | SNR 阶梯 | results.csv 同时记录每点幅度 ρ_s 和单事件累积 SNR ρ_acc = ρ_s·√(τf_s)；保存每轮原始极限 rounds.npz，供显著性检验用 | `train_rev1` |
| #6 | 限制 ξ<1e-2 的 P-P 图 | eval 同时给全先验和 ξ<1e-2 两版，并给出 KS 检验 | `eval_rev1 pp` |
| #5 | null 段 | 取自 eval 时段、互不重叠的 4 s 段（1024 s 数据约 240 段），给出配对差、t 检验 p 值和 bootstrap CI | `eval_rev1 null` |

## v9 追加（2026-10-01）

- 新增 `probe_null_leak.py`：只读，在全部 run 上量化纯噪声后验的先验外泄漏，并比较两种 null 上限定义（截断后 / 裁剪到边界后）。
- `selftest_b.py` 并入 local 的 GPU device 修复。
- `collect_evidence.sh` 新增 `_failures.txt`，自动登记 rc 非零的 run 和含 Traceback 的日志，同时收集 `probe_*.json` / `probe_*.csv`。
- `utils_rev1.py`、`train_rev1.py`、`train_b.py`、`glitchaug_b.py` 保持不变。

## v8 追加（2026-10-01）

- 新增 `probe_posterior.py`：只读、零训练，检查后验在纯噪声段上的形状，包括截断前后的分位数、先验外样本比例和双峰提示。用于排查 03B seed1401 的 null 上限异常。
- 其余文件与 v7 相同。

## v7 追加（2026-09-30）

- `sweep_rev1.py`：
  - 新增 `--train-script` 参数，B 线用 `train_b.py`；
  - 汇总输出改为按配置命名（`summary_<tag>.csv`、`diverged_<tag>.csv`）。修复的问题是：run_A 里 antenna 和 identical 两次汇总写入同一个文件，后一次覆盖了前一次。
- 新增 `run_B2.sh`：B 线 glitch 增广，3 个观测期 × 5 个 seed，每个 run 跑完接 eval 和 veto_diag，最后汇总。
- 新增 `collect_evidence.sh`：只读，打包所有小文件证据。
- `utils_rev1.py`、`train_rev1.py`、`train_b.py`、`glitchaug_b.py` 保持不变。

## v6 追加（2026-09-29，A 主 B 辅）

- **A 线代码不变**：`utils_rev1.py` 和 `train_rev1.py` 与 v4/v5 逐字节相同。
- **B 线新增**：
  - `glitchaug_b.py`：`GlitchSimulator` 只在训练中注入合成的单探测器 glitch；
  - `train_b.py`：与 `train_rev1.py` 只差训练模拟器一处；
  - `configs/rev1_glitchaug.json`；
  - `selftest_b.py`。
- **汇总与运行脚本**：`aggregate_veto.py`（多 seed 否决结果汇总）、`run_A.sh`、`run_B.sh`。
- **本地预演**（合成噪声，n_train=20k，CPU）：
  - 未增广时，eval 里的单探测器 glitch 把 ING-Net 的阈值从 −5.36 抬到 −0.37；
  - 增广后，阈值回到 −5.37，glitch 窗口的中位得分（−6.39）低于纯噪声（−6.15），说明网络学会了把 glitch 当噪声；
  - 在 ξ=0.01、logΩ=−4.6 处，探测效率 ING-Net 为 0.48，Trad 为 0.21；
  - 局限：预演中评估用的 glitch 与训练增广属于同一族，结果偏乐观。

## v4 追加（2026-09-29，data-integrity-guard）

- **数据门槛**：`raw_data_gate` 要求预处理后的数据满足下面任意一条，否则直接报错：
  - 谱形 20–30 Hz 相对 200–300 Hz 的比值 > 3；
  - 60 Hz 谱线相对邻近频段 > 3。
  本地测试：纯白噪声报错，类 LIGO 数据通过。
- **randn 并排对照**：run_meta 里的指纹都和同长度 randn 的指纹并排记录。
- **输入文件信息**：run_meta 记录每个输入文件的 shape 和 dtype。
- **严格加载**：eval 缺少模型时直接报错。
- **合成数据标记**：用合成数据跑出的目录加 `_SYNTHETIC` 后缀。
- **版本记录**：run_meta 增记 scipy 和 gwpy 的版本。

## v3 追加（2026-09-29）

- **采样器**：不再调用 sbi 的无上限拒绝采样。改为直接从 flow 抽样，在先验范围内截断，最多 6 轮；采样不足的观测会补齐并计数（`SAMPLING_STATS`，写入 run_meta 和 eval_summary）。起因是旧 probe 在 04A 真实数据上卡死。
- **噪声指纹**：每次运行都把 train 和 eval 两段白化噪声的峰度尾部、每段方差起伏写入 run_meta，作为确实读到真实数据的正向证据。
- **σ1**：限带后分母改为 980 Hz，σ1 与旧常数之比 ≈ 44.3。

## 自检结果（合成数据，CPU）

- `selftest_rev1.py` 全部通过。ξ 从 1e-3 到 1：能量比 0.96–1.02，事件数符合 Poisson，antenna 模式零延迟相关 ≈ −0.89，峰度随 ξ 单调下降，纯噪声通路无泄漏。
- `train_rev1 --synthetic --quick` 和 `eval_rev1` 端到端跑通。
- σ1 与旧常数之比 = 45.25 = √2048，和审计推导一致。

## 需要确认的物理选择（有默认值，试跑后可以改）

1. **τ = 4 ms。** ξ=1e-3 时每段平均 1 个事件，37% 的段里没有信号。这是 Poisson 过程本身的结果，也正是审稿人 #3 要求讨论多段叠加的原因。
2. **每个事件独立抽取天空方向。** 旧版是每段一个方向。
3. **限制 ξ<1e-2 的 P-P 图不在校准保证范围内。** 即使后验完全校准，在 θ 的一个子区域上条件化后，覆盖率也不必落在对角线上。写回复时要说明这一点，主要依据仍是全先验 P-P（log 先验下 ξ<1e-2 占 1/3 的先验质量）。
4. **Ω 先验取 [−8, −1]。** 修正标定后，单段极限预计在 −4 到 −5 附近。试跑时检查结果是否贴到先验边界。

## 本轮不做（在 rev1 模型上追加即可，不需要重训）

- #3b 多段叠加
- #4 网络容量扫描（需要额外机时）
- #8 glitch 注入（需要下载 Gravity Spy 数据）
- #10 Drasco–Flanagan 基线

## 论文正文要随之修改的地方

Eq.(1)(2) 与 τ、Eq.(4) 改为混合后的峰度、Eq.(8)、VI B 的事件数公式、"V 形"的解释、"ξ→1 高斯极限"的措辞、Trad-FR 的描述、第 IV 节"合成有色噪声"的说法、log1p|κ| 特征变换。所有 Ω 绝对值都会变，Δ 需要重新测。
