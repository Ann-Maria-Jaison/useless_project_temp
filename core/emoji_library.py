# core/emoji_library.py — AYYO Emoji Code Library concepts data

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional


@dataclass
class Concept:
    emoji: str
    name: str
    category: str
    description_ml: str
    code: str
    emoji_view: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


CONCEPTS_CATALOG: List[Concept] = [
    # Basics
    Concept(
        emoji="🔢",
        name="Number",
        category="Basics",
        description_ml="ഒരു number സൂക്ഷിക്കാൻ. Simple!",
        code="x = 10\ny = 3.14",
        emoji_view="📝 x = 10\n📝 y = 3.14"
    ),
    Concept(
        emoji="📝",
        name="String",
        category="Basics",
        description_ml="Text വാക്കുകൾ store ചെയ്യാൻ ഉപയോഗിക്കുന്നു.",
        code='name = "Ayyo"',
        emoji_view='📝 name = "Ayyo"'
    ),
    Concept(
        emoji="✅",
        name="Boolean",
        category="Basics",
        description_ml="True അല്ലെങ്കിൽ False മൂല്യങ്ങൾ സൂക്ഷിക്കാൻ.",
        code="is_active = True",
        emoji_view="📝 is_active = True"
    ),
    Concept(
        emoji="❓",
        name="None",
        category="Basics",
        description_ml="Value ഒന്നും ഇല്ല എന്ന് കാണിക്കാൻ.",
        code="nothing = None",
        emoji_view="📝 nothing = None"
    ),

    # Data Structures
    Concept(
        emoji="📋",
        name="List",
        category="Data Structures",
        description_ml="പല values ഒരുമിച്ച് അടുക്കിവെക്കാൻ.",
        code="nums = [1, 2, 3]",
        emoji_view="📝 nums = [1, 2, 3]"
    ),
    Concept(
        emoji="🎯",
        name="Tuple",
        category="Data Structures",
        description_ml="മാറ്റാൻ പറ്റാത്ത (immutable) list.",
        code="point = (10, 20)",
        emoji_view="📝 point = (10, 20)"
    ),
    Concept(
        emoji="🗺️",
        name="Dictionary",
        category="Data Structures",
        description_ml="Key-Value ജോഡികളായി data സൂക്ഷിക്കാൻ.",
        code='person = {"name": "Ayyo", "age": 20}',
        emoji_view='📝 person = {"name": "Ayyo", "age": 20}'
    ),
    Concept(
        emoji="🎒",
        name="Set",
        category="Data Structures",
        description_ml="Duplicate ഇല്ലാത്ത unique items കൂട്ടം.",
        code="unique_nums = {1, 2, 3}",
        emoji_view="📝 unique_nums = {1, 2, 3}"
    ),

    # Operators
    Concept(
        emoji="➕",
        name="Add",
        category="Operators",
        description_ml="രണ്ട് numbers തമ്മിൽ കൂട്ടാൻ.",
        code="sum_val = a + b",
        emoji_view="📝 sum_val = a + b"
    ),
    Concept(
        emoji="➖",
        name="Subtract",
        category="Operators",
        description_ml="കുറക്കാൻ ഉപയോഗിക്കുന്നു.",
        code="diff = a - b",
        emoji_view="📝 diff = a - b"
    ),
    Concept(
        emoji="✖️",
        name="Multiply",
        category="Operators",
        description_ml="ഗുണിക്കാൻ ഉപയോഗിക്കുന്നു.",
        code="prod = a * b",
        emoji_view="📝 prod = a * b"
    ),
    Concept(
        emoji="➗",
        name="Divide",
        category="Operators",
        description_ml="ഹരിക്കാൻ ഉപയോഗിക്കുന്നു.",
        code="result = a / b",
        emoji_view="📝 result = a / b"
    ),
    Concept(
        emoji="🟰",
        name="Equals",
        category="Operators",
        description_ml="രണ്ട് values തുല്യമാണോ എന്ന് നോക്കാൻ (==).",
        code="is_equal = (a == b)",
        emoji_view="📝 is_equal = (a == b)"
    ),

    # Loops & Conditions
    Concept(
        emoji="🔁",
        name="For loop",
        category="Loops & Conditions",
        description_ml="ഒരേ കാര്യം പല times ചെയ്യാൻ.",
        code="for i in range(5):\n    print(i)",
        emoji_view="🔁 for i in range(5):\n    🔢 print(i)"
    ),
    Concept(
        emoji="🔄",
        name="While loop",
        category="Loops & Conditions",
        description_ml="Condition ശരിയാവുന്നിടത്തോളം വരെ ചെയ്യൂ.",
        code="x = 5\nwhile x > 0:\n    x -= 1",
        emoji_view="📝 x = 5\n🔄 while x > 0:\n    📝 x -= 1"
    ),
    Concept(
        emoji="🔀",
        name="If",
        category="Loops & Conditions",
        description_ml="Condition നോക്കി തീരുമാനമെടുക്കാൻ.",
        code='if x > 5:\n    print("Big!")',
        emoji_view='🔀 if x > 5:\n    🔢 print("Big!")'
    ),
    Concept(
        emoji="🚪",
        name="Break",
        category="Loops & Conditions",
        description_ml="Loop ഉടനടി നിർത്തി പുറത്തുകടക്കാൻ.",
        code="for i in range(10):\n    if i == 5:\n        break",
        emoji_view="🔁 for i in range(10):\n    🔀 if i == 5:\n        🚪 break"
    ),
    Concept(
        emoji="⏭️",
        name="Continue",
        category="Loops & Conditions",
        description_ml="ഇപ്പോഴത്തെ iteration സ്കിപ്പ് ചെയ്ത് അടുത്തതിലേക്ക് പോകാൻ.",
        code="for i in range(5):\n    if i == 2:\n        continue",
        emoji_view="🔁 for i in range(5):\n    🔀 if i == 2:\n        ⏭️ continue"
    ),

    # Functions
    Concept(
        emoji="🎁",
        name="Function",
        category="Functions",
        description_ml="വീണ്ടും ഉപയോഗിക്കാവുന്ന reusable code block.",
        code='def greet():\n    print("Hello!")',
        emoji_view='🎁 def greet():\n    🔢 print("Hello!")'
    ),
    Concept(
        emoji="📥",
        name="Parameter",
        category="Functions",
        description_ml="Function-ലേക്ക് നൽകുന്ന input values.",
        code="def add(a, b):\n    return a + b",
        emoji_view="🎁 def add(a, b):\n    <ctrl42> return a + b"
    ),
    Concept(
        emoji="📤",
        name="Return",
        category="Functions",
        description_ml="Function തിരിച്ച് തരുന്ന output result.",
        code="def get_five():\n    return 5",
        emoji_view="🎁 def get_five():\n    <ctrl42> return 5"
    ),
    Concept(
        emoji="🏹",
        name="Lambda",
        category="Functions",
        description_ml="ഒറ്റ വരിയിലുള്ള വലിപ്പമില്ലാത്ത anonymous function.",
        code="double = lambda x: x * 2",
        emoji_view="📝 double = lambda x: x * 2"
    ),

    # Errors
    Concept(
        emoji="🛡️",
        name="Try/Except",
        category="Errors",
        description_ml="Error വന്നാൽ crash ആകാതെ പിടിക്കാൻ.",
        code='try:\n    res = 10 / 0\nexcept Exception as e:\n    print(e)',
        emoji_view='🛡️ try:\n    📝 res = 10 / 0\n🛡️ except Exception as e:\n    🔢 print(e)'
    ),
    Concept(
        emoji="⚠️",
        name="Raise",
        category="Errors",
        description_ml="സ്വന്തമായി error വലിച്ച് പുറത്തിടാൻ (throw error).",
        code='raise ValueError("Invalid number!")',
        emoji_view='🚨 raise ValueError("Invalid number!")'
    ),

    # Files
    Concept(
        emoji="📂",
        name="Open",
        category="Files",
        description_ml="ഒരു file തുറന്ന് വായിക്കാനോ എഴുതാനോ സജ്ജമാക്കുക.",
        code='with open("file.txt", "r") as f:\n    content = f.read()',
        emoji_view='📂 with open("file.txt", "r") as f:\n    📝 content = f.read()'
    ),
    Concept(
        emoji="📖",
        name="Read",
        category="Files",
        description_ml="File-ൽ ഉള്ള കാര്യങ്ങൾ വായിച്ചെടുക്കുക.",
        code="text = f.read()",
        emoji_view="📝 text = f.read()"
    ),
    Concept(
        emoji="✍️",
        name="Write",
        category="Files",
        description_ml="File-ലേക്ക് വിവരങ്ങൾ എഴുതിച്ചേർക്കുക.",
        code='f.write("Hello World")',
        emoji_view='📝 f.write("Hello World")'
    ),

    # Shortcuts
    Concept(
        emoji="💬",
        name="Comment",
        category="Files & Shortcuts",
        description_ml="Python എക്സിക്യൂട്ട് ചെയ്യാത്ത വിവരണക്കുറിപ്പ്.",
        code="# This is an AYYO comment",
        emoji_view="# This is an AYYO comment"
    ),
    Concept(
        emoji="🔤",
        name="f-string",
        category="Files & Shortcuts",
        description_ml="Variables എളുപ്പത്തിൽ string-നുള്ളിൽ വെക്കാൻ.",
        code='name = "Ann"\nmsg = f"Hi {name}"',
        emoji_view='📝 name = "Ann"\n📝 msg = f"Hi {name}"'
    ),
    Concept(
        emoji="📦",
        name="Import",
        category="Files & Shortcuts",
        description_ml="മറ്റ് libraries / modules പ്രോജക്റ്റിലേക്ക് കൊണ്ടുവരാൻ.",
        code="import math\nres = math.sqrt(16)",
        emoji_view="📦 import math\n📝 res = math.sqrt(16)"
    )
]


def get_all_concepts() -> List[Concept]:
    """Returns all catalog concepts."""
    return CONCEPTS_CATALOG


def search_concepts(query: str, category: Optional[str] = None) -> List[Concept]:
    """Filters concepts by category and search query in name, category, or code."""
    query = (query or "").lower().strip()
    category = (category or "").strip()

    results = []
    for c in CONCEPTS_CATALOG:
        if category and category.lower() != "all" and c.category.lower() != category.lower():
            continue
        if query:
            matches = (
                query in c.name.lower() or
                query in c.category.lower() or
                query in c.description_ml.lower() or
                query in c.code.lower()
            )
            if not matches:
                continue
        results.append(c)
    return results
