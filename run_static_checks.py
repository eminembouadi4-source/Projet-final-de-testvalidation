
import os
import re
import sys

def check_file_content(file_path, checks, errors):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
            for i, line in enumerate(lines):
                for check_name, check_regex in checks.items():
                    if re.search(check_regex, line):
                        errors.append(f"[{check_name}] File: {file_path}:{i+1} - Found: {line.strip()}")
    except Exception as e:
        pass

def scanning_directory(root_dir):
    security_errors = []
    template_errors = []
    python_errors = []

    print(f"Scanning directory: {root_dir} ...")

    for root, dirs, files in os.walk(root_dir):
        if 'venv' in root or '.git' in root or '__pycache__' in root:
            continue

        for file in files:
            file_path = os.path.join(root, file)

            # 1. Security & Config Checks (Python)
            if file.endswith('.py'):
                checks = {
                    'SECRET_KEY_EXPOSED': r'SECRET_KEY\s*=\s*[\'"][^\'"]+[\'"]',
                    'DEBUG_TRUE': r'DEBUG\s*=\s*True',
                    'EMAIL_HOST_PASSWORD_EXPOSED': r'EMAIL_HOST_PASSWORD\s*=\s*[\'"][^\'"]+[\'"]',
                    'PRINT_STATEMENT': r'^\s*print\(',
                }
                check_file_content(file_path, checks, python_errors)

            # 2. Template Checks (HTML)
            if file.endswith('.html'):
                checks = {
                    'HARDCODED_LINK_HASH': r'href="#"',
                    'HARDCODED_LINK_INDEX': r'href="index.html"',
                    'MISSING_ALT': r'<img(?!.*alt=).*?>',
                    'UNSAFE_URL_ACCESS': r'\.url\s(?!.*if)', # Very basic check, lots of false positives likely, but good for flagging
                }
                check_file_content(file_path, checks, template_errors)

    return security_errors, template_errors, python_errors

def main():
    root_dir = os.getcwd()
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]

    sec, tmpl, py = scanning_directory(root_dir)

    print("\n--- REPORT ---")
    
    print("\n[SECURITY / CONFIGURATION]")
    if sec:
        for e in sec: print(e)
    else:
        print("No obvious security issues found (regex based).")

    print("\n[PYTHON QUALITY]")
    if py:
        # Limited output
        for e in py[:20]: print(e)
        if len(py) > 20: print(f"... and {len(py)-20} more.")
    else:
        print("No issues found.")

    print("\n[TEMPLATES]")
    if tmpl:
        # Limited output
        for e in tmpl[:50]: print(e)
        if len(tmpl) > 50: print(f"... and {len(tmpl)-50} more.")
    else:
        print("No issues found.")

if __name__ == "__main__":
    main()
