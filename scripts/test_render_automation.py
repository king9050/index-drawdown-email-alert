#!/usr/bin/env python3

import json
import tempfile
import unittest
from pathlib import Path

from render_automation import load_config, render_spec


BASE_CONFIG = {
    "recipient": "alerts@example.com",
    "send_time": "08:15",
    "timezone": "Asia/Shanghai",
    "language": "zh",
    "thresholds": [10, 20, 30],
    "weekdays": ["MO", "TU", "WE", "TH", "FR"],
    "indices": ["sp500", "nasdaq100"],
    "subject_prefix": "标普纳指回撤提醒",
}


class RenderAutomationTests(unittest.TestCase):
    def write_config(self, config):
        temp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
        with temp:
            json.dump(config, temp, ensure_ascii=False)
        return Path(temp.name)

    def test_supported_languages(self):
        for language in ("zh", "en", "bilingual"):
            config = dict(BASE_CONFIG, language=language)
            loaded = load_config(self.write_config(config))
            spec = render_spec(loaded)
            self.assertIn("alerts@example.com", spec["prompt"])
            self.assertIn('"标普纳指回撤提醒"', spec["prompt"])
            self.assertIn("BYHOUR=8;BYMINUTE=15", spec["rrule"])

    def test_rejects_unsorted_thresholds(self):
        config = dict(BASE_CONFIG, thresholds=[20, 10])
        with self.assertRaises(ValueError):
            load_config(self.write_config(config))

    def test_rejects_wrong_subject_prefix(self):
        config = dict(BASE_CONFIG, subject_prefix="Index Alert")
        with self.assertRaises(ValueError):
            load_config(self.write_config(config))


if __name__ == "__main__":
    unittest.main()
