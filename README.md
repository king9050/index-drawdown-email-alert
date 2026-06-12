# Index Drawdown Email Alert

**English** · [中文](README.zh-CN.md)

A configurable Codex skill that monitors S&P 500 and Nasdaq-100 drawdowns using completed daily closing prices and sends scheduled Gmail alerts when a new threshold is crossed.

## What it does

- Monitors S&P 500 (`^GSPC`) and Nasdaq-100 (`^NDX`)
- Uses the latest all-time highest closing price as the drawdown reference
- Alerts at configurable levels such as 10%, 20%, 30%, and 40%
- Sends each threshold only once during the same drawdown cycle
- Combines multiple thresholds or both indices into one email when appropriate
- Resets the alert cycle only after a new all-time closing high
- Supports Simplified Chinese, English, or bilingual emails
- Lets you configure the recipient, delivery time, timezone, weekdays, indices, and thresholds
- Always starts the subject with `标普纳指回撤提醒`

## Example

```text
Use $index-drawdown-email-alert to send bilingual alerts at 07:30 Asia/Shanghai to investor@example.com when the S&P 500 or Nasdaq-100 crosses a new 10% drawdown level.
```

## Install

```bash
mkdir -p ~/.codex/skills
cd ~/.codex/skills
git clone https://github.com/king9050/index-drawdown-email-alert.git
```

Then restart or refresh Codex so the skill can be discovered.

## Configuration

Copy the example configuration and edit it:

```bash
cp references/config.example.json /tmp/index-alert-config.json
```

```json
{
  "recipient": "investor@example.com",
  "send_time": "07:30",
  "timezone": "Asia/Shanghai",
  "language": "bilingual",
  "thresholds": [10, 20, 30, 40, 50, 60, 70, 80, 90],
  "weekdays": ["MO", "TU", "WE", "TH", "FR"],
  "indices": ["sp500", "nasdaq100"],
  "subject_prefix": "标普纳指回撤提醒"
}
```

Supported languages:

- `zh`: Simplified Chinese
- `en`: English body with the required Chinese subject prefix
- `bilingual`: complete Chinese section followed by complete English section

## Generate the automation specification

```bash
python3 scripts/render_automation.py --config /tmp/index-alert-config.json
```

The generator validates the configuration and returns the automation name, prompt, schedule, and readable summary. A Codex agent then creates or updates the recurring automation and uses the connected Gmail tool for delivery.

## Alert logic

1. Fetch the latest completed US-market daily close.
2. Find the latest all-time highest closing price.
3. Calculate `latest_close / all_time_high_close - 1`.
4. Send an email only when a configured threshold is newly crossed.
5. If one close crosses several new levels, combine them in one email.
6. Do not repeat previously alerted thresholds in the same drawdown cycle.
7. Reset only after the index records a new all-time closing high.
8. Send nothing when no new threshold is crossed or the data cannot be verified.

## Email contents

Each alert includes:

- Index name
- Latest completed market date
- All-time high close and date
- Latest close
- Current drawdown percentage
- Newly crossed thresholds
- Previously alerted thresholds in the same cycle
- A closing-price and investment-risk disclaimer

## Test

```bash
python3 scripts/test_render_automation.py
```

## Repository structure

```text
.
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── config.example.json
│   └── email-layouts.md
└── scripts/
    ├── render_automation.py
    └── test_render_automation.py
```

## Requirements

- Codex recurring automations
- Connected Gmail tool
- Reliable public daily-close market data
- Python 3 for configuration rendering and tests

## Disclaimer

This project provides closing-price discipline alerts. It does not identify market bottoms and does not constitute investment advice.

## License

MIT
