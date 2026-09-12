# core/emoji_palette.py — Mapping for Emoji Coder palette and Quick Programs

from typing import List, Dict, Any

EMOJI_PALETTE_ITEMS: List[Dict[str, Any]] = [
    {
        "emoji": "📝",
        "label": "Assign",
        "code": "variable = value",
        "block": False,
        "tooltip": "Variable ഉണ്ടാക്കാം (Assign variable)"
    },
    {
        "emoji": "🔢",
        "label": "Print",
        "code": "print(value)",
        "block": False,
        "tooltip": "Print ചെയ്യാം (Print output)"
    },
    {
        "emoji": "🔁",
        "label": "For loop",
        "code": "for i in range(10):\n    ",
        "block": True,
        "tooltip": "Loop ഇടാം (For loop iteration)"
    },
    {
        "emoji": "🔄",
        "label": "While loop",
        "code": "while condition:\n    ",
        "block": True,
        "tooltip": "While loop ഇടാം (Conditional loop)"
    },
    {
        "emoji": "🔀",
        "label": "If",
        "code": "if condition:\n    ",
        "block": True,
        "tooltip": "Condition check ചെയ്യാം (If statement)"
    },
    {
        "emoji": "🎁",
        "label": "Function",
        "code": "def name():\n    ",
        "block": True,
        "tooltip": "Function ഉണ്ടാക്കാം (Define function)"
    },
    {
        "emoji": "📥",
        "label": "Input",
        "code": 'input("Enter: ")',
        "block": False,
        "tooltip": "User input എടുക്കാം (Read input)"
    },
    {
        "emoji": "💬",
        "label": "Comment",
        "code": "# comment",
        "block": False,
        "tooltip": "Comment എഴുതാം (Python comment)"
    },
    {
        "emoji": "📋",
        "label": "List",
        "code": "[1, 2, 3]",
        "block": False,
        "tooltip": "List ഉണ്ടാക്കാം (List collection)"
    },
    {
        "emoji": "🗺️",
        "label": "Dict",
        "code": '{"key": "value"}',
        "block": False,
        "tooltip": "Dictionary ഉണ്ടാക്കാം (Key-value dict)"
    },
    {
        "emoji": "🛡️",
        "label": "Try/Except",
        "code": "try:\n    pass\nexcept Exception as e:\n    print(e)",
        "block": True,
        "tooltip": "Error handle ചെയ്യാം (Try/Except block)"
    },
    {
        "emoji": "📦",
        "label": "Import",
        "code": "import module_name",
        "block": False,
        "tooltip": "Module import ചെയ്യാം (Import library)"
    },
    {
        "emoji": "🔚",
        "label": "Return",
        "code": "return value",
        "block": False,
        "tooltip": "Value return ചെയ്യാം (Function return)"
    },
    {
        "emoji": "🚨",
        "label": "Raise",
        "code": 'raise ValueError("message")',
        "block": False,
        "tooltip": "Error raise ചെയ്യാം (Raise exception)"
    },
    {
        "emoji": "✅",
        "label": "True",
        "code": "True",
        "block": False,
        "tooltip": "Boolean True"
    },
    {
        "emoji": "❌",
        "label": "False",
        "code": "False",
        "block": False,
        "tooltip": "Boolean False"
    }
]

QUICK_EMOJI_PROGRAMS: List[Dict[str, Any]] = [
    {
        "icon": "🎁👋",
        "name": "Hello Function",
        "code": 'def hello():\n    print("hi")\n\nhello()',
        "desc": "def hello(): print('hi')"
    },
    {
        "icon": "🔁🔢",
        "name": "Print Loop",
        "code": "for i in range(5):\n    print(i)",
        "desc": "for loop that prints numbers"
    },
    {
        "icon": "🔀🔢",
        "name": "If Check",
        "code": 'x = 10\nif x > 5:\n    print("x is big!")',
        "desc": "if condition that prints"
    },
    {
        "icon": "📋🔄",
        "name": "List Iteration",
        "code": 'items = ["apple", "banana", "cherry"]\nfor x in items:\n    print(x)',
        "desc": "loop over items in a list"
    }
]


def get_emoji_palette() -> List[Dict[str, Any]]:
    return EMOJI_PALETTE_ITEMS


def get_quick_programs() -> List[Dict[str, Any]]:
    return QUICK_EMOJI_PROGRAMS
