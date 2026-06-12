# 标普纳指回撤邮件提醒

[English](README.md) · **中文**

这是一个可配置的 Codex Skill，使用已完成交易日的收盘价监控标普500和纳指100回撤，并在首次触发新回撤档位时通过 Gmail 定时发送提醒。

## 主要功能

- 监控标普500（`^GSPC`）和纳指100（`^NDX`）
- 使用最近的历史最高收盘价作为回撤基准
- 支持10%、20%、30%、40%等自定义回撤档位
- 同一轮回撤中，每个档位只提醒一次
- 单日跨越多个档位时合并提醒
- 两个指数同日触发时合并为一封邮件
- 只有创出新的历史最高收盘价后才重置提醒周期
- 支持中文、英文、中英双语邮件
- 可配置收件邮箱、发送时间、时区、执行日期、指数和阈值
- 邮件主题始终以 `标普纳指回撤提醒` 开头

## 使用示例

```text
使用 $index-drawdown-email-alert，在北京时间每个工作日07:30检查标普500和纳指100；每首次触发新的10%回撤档位时，向 investor@example.com 发送中英双语邮件。
```

## 安装

```bash
mkdir -p ~/.codex/skills
cd ~/.codex/skills
git clone https://github.com/king9050/index-drawdown-email-alert.git
```

安装后刷新或重启 Codex，使技能被自动发现。

## 配置

```bash
cp references/config.example.json /tmp/index-alert-config.json
```

主要配置项：

| 字段 | 示例 | 作用 |
|---|---|---|
| `recipient` | `investor@example.com` | 收件邮箱 |
| `send_time` | `07:30` | 每日检查时间 |
| `timezone` | `Asia/Shanghai` | IANA 时区 |
| `language` | `zh`、`en`、`bilingual` | 邮件语言 |
| `thresholds` | `[10,20,30,...]` | 回撤提醒档位 |
| `weekdays` | `MO` 至 `SU` | 执行日期 |
| `indices` | `sp500`、`nasdaq100` | 监控指数 |

语言选项：

- `zh`：简体中文
- `en`：英文正文，保留中文邮件主题前缀
- `bilingual`：完整中文内容后接完整英文内容

## 生成自动化规范

```bash
python3 scripts/render_automation.py --config /tmp/index-alert-config.json
```

脚本会校验配置并输出自动化名称、执行任务、定时规则和配置摘要。Codex 随后创建或更新自动化，并使用已连接的 Gmail 工具发送邮件。

## 提醒逻辑

1. 获取最近一个已完成美国交易日的收盘价。
2. 找到最近的历史最高收盘价。
3. 按 `最新收盘价 / 历史最高收盘价 - 1` 计算回撤。
4. 只有首次触发新档位时才发送邮件。
5. 单日跨越多个新档位时合并提醒。
6. 同一轮回撤中不重复发送已提醒档位。
7. 指数创出新的历史最高收盘价后才重置。
8. 没有新档位或数据无法可靠核验时，不发送邮件。

## 测试

```bash
python3 scripts/test_render_automation.py
```

## 依赖

- Codex 定时自动化
- 已连接的 Gmail 工具
- 可靠的公开日收盘行情数据
- Python 3

## 风险说明

本项目提供基于收盘价的纪律提醒，不代表市场已经见底，也不构成投资建议。

## 许可证

MIT
