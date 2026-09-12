# core/errors.py

class AyyoTimeout(Exception):
    pass

ERROR_HANDLERS = [
    # ---------- Timeout (custom) ----------
    (AyyoTimeout, ("ബ്രോ, code വളരെ സമയം ഓടുന്നു.",
                   "Code execution time limit (timeout) കഴിഞ്ഞു.",
                   "Infinite loop ഉണ്ടോ? while-ന്റെ condition check ചെയ്യൂ.")),

    # ---------- Syntax / Indentation ----------
    (TabError, ("Tab ഉം space ഉം കൂട്ടിക്കുഴച്ചു ബ്രോ.",
                "Indentation-ൽ tabs-ഉം spaces-ഉം മിക്സ് ചെയ്യരുത്.",
                "ഒന്നുകിൽ tabs, അല്ലെങ്കിൽ spaces. രണ്ടും വേണ്ട.")),
    (IndentationError, ("Indentation ശരിയല്ല ബ്രോ.",
                        "Spaces-ഉം tabs-ഉം കൺഫ്യൂഷൻ ഉണ്ടോ?",
                        "ഒരേ block-ൽ ഒരേ indentation ഉപയോഗിക്കൂ.")),
    (SyntaxError, ("ബ്രോ... syntax ഒന്ന് ശരിയാക്ക്.",
                   "Python-ന് ഈ code മനസ്സിലായില്ല.",
                   "Brackets, quotes, colons എല്ലാം ശരിയാണോ?")),

    # ---------- Import ----------
    (ModuleNotFoundError, ("Module കിട്ടിയില്ല ബ്രോ.",
                           "Module name ശരിയാണോ? Install ചെയ്തിട്ടുണ്ടോ?",
                           "pip install <module> ചെയ്യൂ.")),
    (ImportError, ("Import ചെയ്യാൻ പറ്റുന്നില്ല.",
                   "Module-ൽ ആ function/class ഉണ്ടോ?",
                   "from module import name ശരിയാണോ?")),

    # ---------- File / OS ----------
    (FileNotFoundError, ("ഫയൽ കണ്ടെത്താനായില്ല.",
                         "Path ശരിയാണോ എന്ന് check ചെയ്യൂ.",
                         "ഫയൽ exist ചെയ്യുന്നുണ്ടോ?")),
    (PermissionError, ("ഫയൽ open ചെയ്യാൻ permission ഇല്ല.",
                       "Admin rights വേണോ?",
                       "ഫയൽ permissions check ചെയ്യൂ.")),
    (IsADirectoryError, ("ഇത് ഒരു directory ആണ്, ഫയൽ അല്ല.",
                         "ഫയൽ path ശരിയാണോ?",
                         "Directory-യിൽ open() ചെയ്യരുത്.")),
    (NotADirectoryError, ("ഇത് directory അല്ല.",
                          "Path ശരിയാണോ?",
                          "Directory-യിൽ listdir() ചെയ്യണം.")),

    # ---------- Arithmetic ----------
    (ZeroDivisionError, ("ബ്രോ... zero കൊണ്ട് divide ചെയ്യാൻ നോക്കിയല്ലേ.",
                         "Zero കൊണ്ട് ഒരു number divide ചെയ്യാൻ പറ്റില്ല.",
                         "Denominator zero ആണോ എന്ന് നോക്കൂ.")),
    (OverflowError, ("Number വളരെ വലുതായി പോയി.",
                     "Python-ന്റെ limit കഴിഞ്ഞു.",
                     "ചെറിയ numbers ഉപയോഗിക്കൂ.")),
    (FloatingPointError, ("Floating point calculation-ൽ പ്രശ്നം.",
                          "സാധാരണയായി വരാറില്ല.",
                          "Math operations check ചെയ്യൂ.")),

    # ---------- Value / Type ----------
    (ValueError, ("ബ്രോ, value ശരിയല്ല.",
                  "ഈ value ഈ operation-ന് പറ്റിയതല്ല.",
                  "int('abc') ചെയ്യാൻ പറ്റില്ല.")),
    (TypeError, ("ബ്രോ, ഈ രണ്ട് type-കളെ ഇങ്ങനെ കൂട്ടാൻ പറ്റില്ല.",
                 "രണ്ട് values-ന്റെയും type check ചെയ്യൂ.",
                 "int + str ഒക്കെ ശരിയാവില്ല.")),

    # ---------- Name ----------
    (UnboundLocalError, ("Local variable ഉപയോഗിക്കുന്നതിന് മുൻപ് assign ചെയ്തിട്ടില്ല.",
                         "Function-നുള്ളിൽ variable ഉപയോഗിക്കുന്നതിന് മുൻപ് value കൊടുക്കൂ.",
                         "global variable ആണെങ്കിൽ global keyword ഉപയോഗിക്കൂ.")),
    (NameError, ("ബ്രോ, ഈ variable ആരാടാ?",
                 "ആദ്യം variable define ചെയ്യണം.",
                 "Variable name ശരിയാണോ എന്ന് check ചെയ്യൂ.")),

    # ---------- Lookup ----------
    (IndexError, ("ബ്രോ, ആ position-ൽ ഒന്നുമില്ല.",
                  "List-ന്റെ available indexes check ചെയ്യൂ.",
                  "Index 0 മുതൽ len-1 വരെ മാത്രമേ ഉള്ളൂ.")),
    (KeyError, ("ഈ key dictionary-ൽ ഇല്ല ബ്രോ.",
                "Dictionary-യിലെ keys check ചെയ്യൂ.",
                "get() use ചെയ്താൽ error വരില്ല.")),

    # ---------- Attribute ----------
    (AttributeError, ("ഈ object-ന് ആ attribute ഇല്ല ബ്രോ.",
                      "Object-ന്റെ type-ഉം available methods-ഉം check ചെയ്യൂ.",
                      "ഉദാഹരണം: 'str' object-ന് append ഇല്ല.")),

    # ---------- Assertion ----------
    (AssertionError, ("Assertion പരാജയപ്പെട്ടു.",
                      "Condition തെറ്റാണെന്ന് assert പറയുന്നു.",
                      "Assert statement-ലെ condition check ചെയ്യൂ.")),

    # ---------- Iteration ----------
    (StopIteration, ("Iterator അവസാനിച്ചു.",
                     "next() വിളിക്കാൻ ഇനി items ഇല്ല.",
                     "for loop ഉപയോഗിക്കൂ, safe ആണ്.")),

    # ---------- Recursion / Memory ----------
    (RecursionError, ("Recursion limit കഴിഞ്ഞു ബ്രോ.",
                      "Function സ്വയം വിളിക്കുന്നത് നിർത്താതെ എങ്ങനെ?",
                      "Base condition ഉണ്ടാക്കൂ.")),
    (MemoryError, ("Memory തീർന്നു ബ്രോ.",
                   "ഒരുപാട് data ഒരുമിച്ച് handle ചെയ്യാൻ ശ്രമിക്കുന്നുണ്ടോ?",
                   "Large data-യെ chunks ആക്കി process ചെയ്യൂ.")),

    # ---------- Runtime ----------
    (NotImplementedError, ("ഈ method ഇതുവരെ implement ചെയ്തിട്ടില്ല.",
                           "Abstract method ആണോ?",
                           "Subclass-ൽ implement ചെയ്യൂ.")),
    (RuntimeError, ("Runtime-ൽ എന്തോ പ്രശ്നം.",
                    "Specific error message നോക്കൂ.",
                    "Code logic check ചെയ്യൂ.")),

    # ---------- OS / IO ----------
    (OSError, ("Operating system-ൽ നിന്ന് error.",
               "File, network, permission എന്നിവയിൽ എന്തെങ്കിലും പ്രശ്നമോ?",
               "Error message വിശദമായി വായിക്കൂ.")),
    (EOFError, ("End of file unexpectedly എത്തി.",
                "input() ചെയ്യുമ്പോൾ data തീർന്നോ?",
                "File അവസാനിച്ചു.")),
]