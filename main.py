# main.py — CLI interface for AYYO Malayalam Python Playground

import sys
from core.analyzer import analyze_code_full
from core.explainer import explain_code
from core.detective import inspect_code
from core.cleaner import clean_code
from core.personality import analyze_personality
from core.runner import run_code, DEFAULT_TIMEOUT
from core.test_lab import generate_test_lab, run_test_lab_tests


def print_banner():
    print("=" * 60)
    print("  AYYO.py — Malayalam Python Companion ")
    print("=" * 60)


def get_user_code() -> str:
    print("\nEnter or paste your Python code below.")
    print("Type 'END' on a new line when finished:\n")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


def render_diagnose(code: str):
    print("\n------------------------------------------------------------")
    print("🔴 1. DIAGNOSE MODE (Run & Error Explainer)")
    print("------------------------------------------------------------")
    res = run_code(code, timeout=DEFAULT_TIMEOUT)
    if res.get("ok"):
        print("✅ SUCCESS! Output:")
        print(res.get("output") or "(No stdout output)")
    else:
        err = res.get("error") or {}
        print("AYYO! ERROR DETECTED 💀")
        print(f"Line {err.get('line') or 1} | {err.get('title')}")
        if err.get("code"):
            print(f"   Code: {err.get('code')}")
        print(f"   Desc: {err.get('desc')}")
        print(f"   Tip:  {err.get('tip')}")
        if err.get("hints"):
            print("   Hints:")
            for h in err["hints"]:
                print(f"     - {h}")


def render_explain(analysis):
    res = explain_code(analysis)
    print("\n------------------------------------------------------------")
    print("🧠 2. AYYO CODE EXPLAINER")
    print("------------------------------------------------------------")
    print(res.summary)
    if res.variables_summary:
        print("\nVariables:")
        for v in res.variables_summary:
            print(f"  • {v}")
    if res.functions_summary:
        print("\nFunctions:")
        for f in res.functions_summary:
            print(f"  • {f}")
    if res.loops_summary:
        print("\nLoops:")
        for l in res.loops_summary:
            print(f"  • {l}")
    if res.conditions_summary:
        print("\nConditions:")
        for c in res.conditions_summary:
            print(f"  • {c}")
    if res.predictable_output:
        print(f"\nExpected Output:\n{res.predictable_output}")
    print(f"\nAYYO says:\n{res.manglish_take}")


def render_detective(analysis):
    res = inspect_code(analysis)
    print("\n------------------------------------------------------------")
    print("🕵️ 3. AYYO CODE DETECTIVE")
    print("------------------------------------------------------------")
    print("Evidence found:")
    for k, v in res.counts.items():
        print(f"  {k:<12}: {v}")

    print("\n🔍 Suspicious activity:")
    if not res.suspicious_activities:
        print("  None found! Code looks suspicious-free.")
    else:
        for item in res.suspicious_activities:
            line_str = f"Line {item['line']}: " if item.get("line") else ""
            print(f"  [{item['severity']}] {line_str}{item['message']}")

    print(f"\n{res.verdict}")


def render_cleaner(analysis):
    res = clean_code(analysis)
    print("\n------------------------------------------------------------")
    print("🧹 4. AYYO CODE CLEANER")
    print("------------------------------------------------------------")
    if res.is_modified:
        print("🧹 BEFORE:")
        print(res.original)
        print("\n        ↓\n")
        print("✨ AFTER:")
        print(res.cleaned)
        print("\nChanges made:")
        for c in res.changes_made:
            print(f"  • {c}")
    else:
        print("✨ CODE IS ALREADY CLEAN:")
        print(res.cleaned)
    print(f"\nAYYO:\n{res.manglish_comment}")


def render_personality(analysis):
    res = analyze_personality(analysis)
    print("\n------------------------------------------------------------")
    print("🧬 5. YOUR CODE PERSONALITY")
    print("------------------------------------------------------------")
    for trait, score in res.scores.items():
        bars = "█" * (score // 10) + "░" * (10 - (score // 10))
        print(f"  {trait:<14} {bars} {score}%")
    print(f"\nDeveloper Type:\n  {res.developer_type}")
    print(f"\nAYYO says:\n  {res.manglish_comment}")


def render_test_lab(analysis, code: str):
    res = generate_test_lab(analysis)
    print("\n------------------------------------------------------------")
    print("🧪 6. AYYO TEST LAB")
    print("------------------------------------------------------------")
    print(f"Functions found: {len(res.functions)}")

    if res.tests:
        print("\nGenerated tests:")
        for t in res.tests:
            print(f"\n━━━ {t.test_name} ━━━")
            print(t.code)

    if res.skipped:
        print("\nSkipped functions:")
        for s in res.skipped:
            print(f"  • {s['function']}: {s['reason']}")

    print(f"\nAYYO:\n\"{res.summary}\"")

    if res.tests:
        run_choice = input("\nRun generated tests now? (y/n): ").strip().lower()
        if run_choice == "y":
            run_res = run_test_lab_tests(code, [t.to_dict() for t in res.tests])
            print("\nTest Execution Results:")
            for item in run_res.get("results", []):
                badge = "✅ PASSED" if item["passed"] else "❌ FAILED"
                print(f"  {badge} — {item['test_name']}")
                if not item["passed"]:
                    print(f"     Detail: {item['detail']}")


def main():
    print_banner()
    code = get_user_code()
    if not code.strip():
        print("Empty code. Exiting.")
        return

    analysis = analyze_code_full(code)

    while True:
        print("\nChoose AYYO Mode:")
        print("  1. 🔴 Diagnose (Run & Explain Errors)")
        print("  2. 🧠 Explain (What does this code do?)")
        print("  3. 🕵️ Detective (Inspect & Audit Code)")
        print("  4. 🧹 Cleaner (Format & Clean Code)")
        print("  5. 🧬 Personality (Code Personality Profile)")
        print("  6. 🧪 Test Lab (Auto-generate unit tests)")
        print("  7. 🚀 Run All Modes")
        print("  8. ❌ Exit")

        choice = input("\nEnter mode (1-8): ").strip()
        if choice == "1":
            render_diagnose(code)
        elif choice == "2":
            render_explain(analysis)
        elif choice == "3":
            render_detective(analysis)
        elif choice == "4":
            render_cleaner(analysis)
        elif choice == "5":
            render_personality(analysis)
        elif choice == "6":
            render_test_lab(analysis, code)
        elif choice == "7":
            render_diagnose(code)
            render_explain(analysis)
            render_detective(analysis)
            render_cleaner(analysis)
            render_personality(analysis)
            render_test_lab(analysis, code)
        elif choice == "8" or choice.lower() in ("q", "quit", "exit"):
            print("\nNandi! See you next time! 👋")
            break
        else:
            print("Invalid choice. Please enter 1-8.")


if __name__ == "__main__":
    main()