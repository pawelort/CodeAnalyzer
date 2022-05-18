import re, os, sys, ast


def message_printer(path, line_no, code, message):
    print(f"{path}: Line {line_no}: {code} {message}")


def S001(path, line, line_no):
    if len(line) > 79:
        message_printer(path, line_no, 'S001', 'Too long')


def S002(path, line, line_no):
    spaces = 0
    for char in line:
        if char == ' ':
            spaces += 1
        elif char != ' ':
            break
    if spaces % 4 != 0:
        message_printer(path, line_no, 'S002', 'Indentation is not a multiple of four')


def S003(path, line, line_no):
    pattern = r".*;[$\s]"
    statement = line.split('#')
    if re.match(pattern, statement[0]):
        message_printer(path, line_no, 'S003', 'Unnecessary semicolon')


def S004(path, line, line_no):
    pattern = r".*[\s]{2}#"
    if '#' in line:
        if re.match(pattern, line) is None and '#' != line[0]:
            message_printer(path, line_no, 'S004', 'At least two spaces required before inline comments')


def S005(path, line, line_no):
    pattern = r".*[tT][oO][dD][oO]"
    statement = line.split('#')
    if '#' in line and re.match(pattern, statement[1]):
        message_printer(path, line_no, 'S005', 'TODO found')


def S006(path, blank_lines, line, line_no):
    pattern = r"\s$"
    blank = blank_lines
    if re.match(pattern, line):
        blank += 1
    else:
        if blank > 2:
            message_printer(path, line_no, 'S006', 'More than two blank lines used before this line')
        blank = 0
    return blank


def S007(path, line, line_no):
    pattern1 = r'[\s]*def [\w]'
    pattern2 = r'class [\w]'
    if 'def' in line:
        if re.match(pattern1, line) is None:
            message_printer(path, line_no, "S007", "Too many spaces after 'def'")
    elif 'class' in line:
        if re.match(pattern2, line) is None:
            message_printer(path, line_no, "S007", "Too many spaces after 'class'")

def S008(path, line, line_no):
    pattern = r'class[\s]+([A-Z][A-Za-z\d]*)*(\([A-Z][A-Za-z\d]*\))?:'
    if 'class' in line:
        if re.match(pattern, line) is None:
            class_pattern = r"[\w]+[\(:]"
            class_name = re.search(class_pattern, line)
            message_printer(path, line_no, "S008", f"Class name {class_name.group()[:-1]} should be written in CamelCase.")


def S009(path, line, line_no):
    pattern = r'[\s]*def[\s]+[a-z_][a-z\d]*(_[a-z\d]+)*_?_?\('
    if 'def' in line:
        if re.match(pattern, line) is None:
            def_pattern = r"[\w]+[\(:]"
            def_name = re.search(def_pattern, line)
            message_printer(path, line_no, "S009", f"Function name {def_name.group()[:-1]} should be written in snake_case.")

def S010(path, ast_parse):

    pattern = r'[a-z_][a-z\d]*(_[a-z\d]+)*_?_?'
    function_names = [node for node in ast.walk(ast_parse) if isinstance(node, ast.FunctionDef)]
    for function in function_names:
        for argument in function.args.args:
            if re.match(pattern, argument.arg) is None:
                message_printer(path, function.lineno, "S010", f"Argument name {argument.arg} should be written in snake_case")

def S011(path, ast_parse):
    pattern = r'[a-z_][a-z\d]*(_[a-z\d]+)*_?_?'
    assignments = [node for node in ast.walk(ast_parse) if isinstance(node, ast.Assign)]
    for single_assignment in assignments:
        for target in single_assignment.targets:
            try:
                var_name = target.id
            except AttributeError:
                var_name = target.attr

            if re.match(pattern, var_name) is None:
                message_printer(path, single_assignment.lineno, "S011",
                                f"Variable {var_name} should be written in snake_case")


def S012(path, ast_parse):
    function_names = [node for node in ast.walk(ast_parse) if isinstance(node, ast.FunctionDef)]
    for function in function_names:
        for def_argument in function.args.defaults:
            if type(def_argument) in {ast.List, ast.Dict, ast.Set}:
                message_printer(path, function.lineno, "S012", f"Default argument value is mutable")


def create_file_list(path):
    path_to_check = dict()
    if path.endswith('.py'):
        folder = os.sep.join(path.split(os.sep)[:-1])
        file = [path.split(os.sep)[-1]]
        path_to_check[folder] = file
        return path_to_check
    else:
        for path, dirname, files in os.walk(path):
            files = [file for file in files if file.endswith('.py')]
            path_to_check[path] = files
        return path_to_check


def code_check(path, line, line_no):
    S001(path, line, line_no)
    S002(path, line, line_no)
    S003(path, line, line_no)
    S004(path, line, line_no)
    S005(path, line, line_no)
    S007(path, line, line_no)
    S008(path, line, line_no)
    S009(path, line, line_no)

items_to_check = create_file_list(sys.argv[1])
# items_to_check = create_file_list('C:\\Users\\pawel\\PycharmProjects\\Static Code Analyzer\\Static Code Analyzer\\task\\test')
for folder_path, file_name in items_to_check.items():
    for file in file_name:
        empty_lines = 0
        path_to_current_file = ''.join((folder_path, os.sep, file))
        with open(path_to_current_file, mode='r', encoding='utf-8') as current_file:
            for enum, single_line in enumerate(current_file, start=1):
                code_check(path_to_current_file, single_line, enum)
                empty_lines = S006(path_to_current_file, empty_lines, single_line, enum)
            current_file.seek(0)
            tree = ast.parse(current_file.read())
            S010(path_to_current_file, tree)
            S011(path_to_current_file, tree)
            S012(path_to_current_file, tree)
