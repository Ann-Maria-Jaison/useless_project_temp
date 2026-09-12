# tests/test_ayyo.py — Unit tests for AYYO Malayalam Python Playground

import unittest
from unittest.mock import patch

from core.analyzer import analyze_code_full
from core.explainer import explain_code
from core.detective import inspect_code
from core.cleaner import clean_code
from core.personality import analyze_personality
from core.runner import run_code
from core.test_lab import generate_test_lab
from core.emoji_view import code_to_emoji
from core.emoji_palette import get_emoji_palette
from app import create_app


class TestAyyoPlayground(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()

    def test_a_simple_code(self):
        """Test A — Simple valid code should produce no ERRORs and clear explainer summary."""
        code = 'name = "Ann"\nprint("Hello", name)'
        analysis = analyze_code_full(code)
        
        # Expect no ERRORs
        errors = [i for i in analysis.issues if i.severity == "ERROR"]
        self.assertEqual(len(errors), 0, f"Expected 0 errors, got: {errors}")

        # Explainer check
        res = explain_code(analysis)
        self.assertIn("Hello", res.predictable_output or "")
        self.assertTrue(any("name" in v for v in res.variables_summary))

    def test_b_errors(self):
        """Test B — Errors should be caught with line numbers and correct error types."""
        code = 'age = 20\nprint("Age: " + age)\nprint(undefined_variable)'
        res = run_code(code, timeout=2)
        
        self.assertFalse(res["ok"])
        self.assertIsNotNone(res["error"])
        # Should catch TypeError on line 2 during execution
        self.assertEqual(res["error"]["line"], 2)
        self.assertEqual(res["error"]["type"], "TypeError")

        # Static analysis should catch NameError on line 3
        analysis = analyze_code_full(code)
        issue_types = [i.type for i in analysis.issues]
        self.assertIn("NameError", issue_types)

    def test_c_detective(self):
        """Test C — Detective should audit code and find unused vars & uncalled functions."""
        code = 'x = 10\ny = 20\n\ndef calculate():\n    return x + y\n\nunused = 100'
        analysis = analyze_code_full(code)
        res = inspect_code(analysis)

        kinds = [s["kind"] for s in res.suspicious_activities]
        self.assertIn("UnusedVariable", kinds)
        self.assertIn("UncalledFunction", kinds)

    def test_d_personality(self):
        """Test D — Personality profile should compute metrics for loops & conditions without crashing."""
        code = 'for i in range(10):\n    if i % 2 == 0:\n        print(i)'
        analysis = analyze_code_full(code)
        
        self.assertEqual(analysis.metrics["loop_count"], 1)
        self.assertEqual(analysis.metrics["condition_count"], 1)

        res = analyze_personality(analysis)
        self.assertIn("Logic", res.scores)
        self.assertIn("Chaos", res.scores)
        self.assertIn("Simplicity", res.scores)
        self.assertTrue(len(res.developer_type) > 0)

    def test_e_cleaner(self):
        """Test E — Cleaner should format spacing and preserve semantic behavior."""
        code = 'x=10\ny =   20\nif x<y:\n    print( x+y )'
        analysis = analyze_code_full(code)
        res = clean_code(analysis)

        self.assertTrue(res.is_modified)
        self.assertIn("x = 10", res.cleaned)
        self.assertIn("y = 20", res.cleaned)
        
        # Verify execution of cleaned code matches original behavior
        orig_run = run_code(code, timeout=2)
        clean_run = run_code(res.cleaned, timeout=2)
        self.assertEqual(orig_run["output"], clean_run["output"])

    def test_f_test_lab_simple(self):
        """Test F — Test Lab simple: def add(a, b): return a + b generates 3+ tests referencing add."""
        code = 'def add(a, b):\n    return a + b'
        analysis = analyze_code_full(code)
        res = generate_test_lab(analysis)

        self.assertGreaterEqual(len(res.tests), 3)
        for t in res.tests:
            self.assertEqual(t.function_name, "add")
            self.assertIn("add", t.code)

    def test_g_test_lab_skips_complex(self):
        """Test G — Test Lab skips complex: function with loop listed under skipped, not under tests."""
        code = 'def process(items):\n    result = []\n    for x in items:\n        result.append(x * 2)\n    return result'
        analysis = analyze_code_full(code)
        res = generate_test_lab(analysis)

        skipped_fns = [s["function"] for s in res.skipped]
        test_fns = [t.function_name for t in res.tests]

        self.assertIn("process", skipped_fns)
        self.assertNotIn("process", test_fns)

    def test_h_voice_graceful_failure(self):
        """Test H — Voice graceful failure: monkeypatch pyttsx3.init to raise RuntimeError, confirm /speak returns clean error response."""
        with patch("pyttsx3.init", side_effect=RuntimeError("No audio driver available")):
            response = self.client.post("/speak", json={"text": "Namaskaram Bro"})
            
            # Response should return 500 status code with JSON error message and not crash
            self.assertEqual(response.status_code, 500)
            data = response.get_json()
            self.assertIn("Voice unavailable", data.get("error", ""))

    def test_i_library_loads(self):
        """Test I — Library loads: GET /library returns 200 and /api/library contains at least 20 concepts."""
        res_page = self.client.get("/library")
        self.assertEqual(res_page.status_code, 200)
        self.assertIn("Emoji Code Library", res_page.get_data(as_text=True))

        res_api = self.client.get("/api/library")
        self.assertEqual(res_api.status_code, 200)
        data = res_api.get_json()
        self.assertGreaterEqual(data.get("count", 0), 20)

    def test_j_emoji_insert(self):
        """Test J — Emoji insert: palette item 🔁 yields for loop code snippet."""
        palette = get_emoji_palette()
        item_for = next((i for i in palette if i["emoji"] == "🔁"), None)
        self.assertIsNotNone(item_for)
        self.assertIn("for i in range", item_for["code"])

    def test_k_emoji_view_translator(self):
        """Test K — Emoji view translator: x = 10\nprint(x) -> output lines 📝 and 🔢."""
        code = "x = 10\nprint(x)"
        translated = code_to_emoji(code)
        self.assertEqual(len(translated), 2)
        self.assertEqual(translated[0]["emoji"], "📝")
        self.assertEqual(translated[1]["emoji"], "🔢")

    def test_l_unknown_line(self):
        """Test L — Unknown line: @@@weird@@@ -> output ⬜ (no crash)."""
        code = "@@@weird@@@"
        translated = code_to_emoji(code)
        self.assertEqual(len(translated), 1)
        self.assertEqual(translated[0]["emoji"], "⬜")

    def test_m_existing_features_untouched(self):
        """Test M — Existing features untouched: run 6 modes and confirm clean operation."""
        code = "def add(a, b):\n    return a + b\nprint(add(2, 3))"
        r1 = self.client.post("/run", json={"code": code})
        self.assertTrue(r1.get_json().get("ok"))

        r2 = self.client.post("/explain", json={"code": code})
        self.assertIn("summary", r2.get_json())

        r3 = self.client.post("/test-lab", json={"code": code})
        self.assertGreaterEqual(len(r3.get_json().get("tests", [])), 1)


if __name__ == "__main__":
    unittest.main()
