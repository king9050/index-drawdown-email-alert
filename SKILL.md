---
name: index-drawdown-email-alert
description: Configure, create, update, or inspect recurring email alerts for S&P 500 and Nasdaq-100 drawdowns. Use when a user wants market-close monitoring of ^GSPC or ^NDX, configurable recipients and delivery times, 10%-step drawdown notifications, Chinese, English, or bilingual email output, or a Codex automation that sends Gmail alerts without duplicate messages.
---

# Index Drawdown Email Alert

Create a scheduled Codex automation that checks completed daily closes for the S&P 500 and Nasdaq-100 and emails only when a new drawdown threshold is crossed.

## Workflow

1. Collect or infer the configuration:
   - `recipient`
   - `send_time` in `HH:MM`
   - `timezone`
   - `language`: `zh`, `en`, or `bilingual`
   - `thresholds`: ascending percentages, normally `10,20,...,90`
   - weekdays to run
2. Copy `references/config.example.json` to a writable project path and edit it.
3. Run:

   ```bash
   python3 scripts/render_automation.py --config /absolute/path/config.json
   ```

4. Read the returned JSON specification.
5. Search existing Codex automations for a matching drawdown monitor.
6. Use the Codex automation tool to create or update one cron automation with the returned `name`, `prompt`, and `rrule`.
7. Keep the automation active unless the user requests a paused setup.
8. Report the configured time, timezone, recipient, language, thresholds, and automation ID.

## Required Behavior

- Use completed US-market daily closing prices, never unfinished intraday data.
- Calculate drawdown from the latest all-time highest closing price:

  `drawdown = latest_close / all_time_high_close - 1`

- Alert once at each newly crossed configured threshold during the same drawdown cycle.
- If one close crosses several new thresholds, combine them into one email.
- Do not repeat a threshold while the index remains in the same drawdown cycle.
- Reset all threshold state only after the index posts a new all-time closing high.
- Combine both indices into one email when they trigger on the same run.
- Send nothing when no new threshold is crossed.
- Fail closed when prices, dates, or the state record cannot be verified.
- Send through the connected Gmail tool.
- Always begin the subject with `标普纳指回撤提醒`.
- For `zh`, write the body in Simplified Chinese.
- For `en`, write the body in English while preserving the required Chinese subject prefix.
- For `bilingual`, place the complete Chinese section first and the matching English section second.
- Include index, market date, high close and date, latest close, current drawdown, newly crossed thresholds, and previously alerted thresholds.
- Include a short statement that the alert is based on closing prices, does not identify a market bottom, and is not investment advice.

## Editing Existing Alerts

Inspect the existing automation first. Preserve its ID and unrelated settings. Regenerate the full specification after changing recipient, time, timezone, language, thresholds, or weekdays, then update the automation rather than creating a duplicate.

## Resources

- `scripts/render_automation.py`: validate configuration and render the automation specification.
- `references/config.example.json`: editable configuration template.
- `references/email-layouts.md`: language-specific subject and body rules.
