#!/usr/bin/env python3
"""Validate drawdown-alert config and render a Codex automation specification."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


VALID_LANGUAGES = {"zh", "en", "bilingual"}
VALID_DAYS = {"MO", "TU", "WE", "TH", "FR", "SA", "SU"}
VALID_INDICES = {"sp500", "nasdaq100"}
INDEX_LABELS = {
    "sp500": "S&P 500 (^GSPC)",
    "nasdaq100": "Nasdaq-100 (^NDX)",
}


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)

    required = {
        "recipient",
        "send_time",
        "timezone",
        "language",
        "thresholds",
        "weekdays",
        "indices",
        "subject_prefix",
    }
    missing = sorted(required - config.keys())
    if missing:
        raise ValueError(f"Missing fields: {', '.join(missing)}")

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", config["recipient"]):
        raise ValueError("recipient must be a valid email address")
    if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", config["send_time"]):
        raise ValueError("send_time must use 24-hour HH:MM format")
    if not re.fullmatch(r"[A-Za-z_]+/[A-Za-z0-9_+\-]+", config["timezone"]):
        raise ValueError("timezone must be an IANA name such as Asia/Shanghai")
    if config["language"] not in VALID_LANGUAGES:
        raise ValueError("language must be zh, en, or bilingual")
    if not config["subject_prefix"].startswith("标普纳指回撤提醒"):
        raise ValueError("subject_prefix must start with 标普纳指回撤提醒")

    thresholds = config["thresholds"]
    if (
        not isinstance(thresholds, list)
        or not thresholds
        or any(not isinstance(x, int) or x <= 0 or x >= 100 for x in thresholds)
        or thresholds != sorted(set(thresholds))
    ):
        raise ValueError("thresholds must be unique ascending integers from 1 to 99")

    weekdays = config["weekdays"]
    if not isinstance(weekdays, list) or not weekdays or any(x not in VALID_DAYS for x in weekdays):
        raise ValueError("weekdays must contain MO..SU values")

    indices = config["indices"]
    if not isinstance(indices, list) or not indices or any(x not in VALID_INDICES for x in indices):
        raise ValueError("indices supports sp500 and nasdaq100")

    return config


def render_prompt(config: dict) -> str:
    thresholds = ", ".join(f"{x}%" for x in config["thresholds"])
    indices = ", ".join(INDEX_LABELS[x] for x in config["indices"])
    language_rule = {
        "zh": "Write the email body in Simplified Chinese.",
        "en": (
            "Write the email body in English, but keep the required Chinese "
            "subject prefix unchanged."
        ),
        "bilingual": (
            "Write the complete Simplified Chinese section first, followed by "
            "a complete matching English section."
        ),
    }[config["language"]]

    return f"""Monitor {indices} using the latest completed US-market daily close.

For each index, find the latest all-time highest closing price and calculate
drawdown as latest_close / all_time_high_close - 1. Track these configured
drawdown thresholds: {thresholds}.

Maintain persistent per-index state for the current drawdown cycle. Send an
email only when a configured threshold is crossed for the first time in that
cycle. If one close crosses multiple new thresholds, combine them in one
email. Do not repeat previously alerted thresholds. Reset the index state only
after it records a new all-time closing high. Combine both indices in one
message when they trigger on the same run.

Use reliable public market data and verify the latest completed trading date.
Never use an unfinished intraday price. If data, dates, or prior state cannot
be verified, send nothing and record the reason.

Send through the connected Gmail tool to {config["recipient"]}. Every subject
must begin exactly with \"{config["subject_prefix"]}\". Include index name,
market date, high close and date, latest close, current drawdown, thresholds
newly crossed in this run, and thresholds alerted earlier in the cycle.
{language_rule}

End with a concise disclaimer that this is a closing-price discipline alert,
does not mean the market has bottomed, and is not investment advice. If no new
threshold is crossed, do not send an email."""


def render_spec(config: dict) -> dict:
    hour, minute = config["send_time"].split(":")
    days = ",".join(config["weekdays"])
    rrule = (
        f"DTSTART;TZID={config['timezone']}:20260101T{hour}{minute}00\n"
        f"RRULE:FREQ=WEEKLY;BYDAY={days};BYHOUR={int(hour)};BYMINUTE={int(minute)}"
    )
    return {
        "name": "S&P 500 and Nasdaq drawdown email alert",
        "prompt": render_prompt(config),
        "rrule": rrule,
        "summary": {
            "recipient": config["recipient"],
            "time": config["send_time"],
            "timezone": config["timezone"],
            "language": config["language"],
            "thresholds": config["thresholds"],
            "weekdays": config["weekdays"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    config = load_config(args.config)
    print(json.dumps(render_spec(config), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
