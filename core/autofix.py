def autofix(code, error):
    # if NameError on 'nmae' and 'name' exists → replace
    # if '=' used in if condition → replace with '=='
    # if 'print x' → replace with 'print(x)'
    return fixed_code, changes