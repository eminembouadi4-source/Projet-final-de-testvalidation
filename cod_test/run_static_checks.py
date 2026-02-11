
import os
import re
import sys
import subprocess

def check_regex_in_file(file_path, checks, errors):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
            for i, line in enumerate(lines):
                for check_name, check_regex in checks.items():
                    if re.search(check_regex, line):
                        errors.append(f"[{check_name}] File: {file_path}:{i+1} - Found: {line.strip()[:100]}")
    except Exception as e:
        pass

def check_file_existence(root_dir, relative_path, errors):
    full_path = os.path.join(root_dir, relative_path)
    if not os.path.exists(full_path):
        errors.append(f"[MISSING_FILE] File not found: {relative_path}")

def run_django_check():
    print("Running 'python manage.py check'...")
    try:
        result = subprocess.run([sys.executable, 'manage.py', 'check'], capture_output=True, text=True)
        if result.returncode != 0:
            return [f"[DJANGO_CHECK_FAIL] {line}" for line in result.stderr.split('\n') if line]
        return []
    except Exception as e:
        return [f"[DJANGO_CHECK_ERROR] Could not run manage.py check: {e}"]

def scanning_directory(root_dir):
    python_errors = []
    django_config_errors = []
    security_errors = []
    dependency_errors = []
    template_errors = []
    js_css_errors = []
    
    print(f"Scanning directory: {root_dir} ...")

    # 4.2 Check requirements.txt existence
    check_file_existence(root_dir, '../requirements.txt', dependency_errors) # Assuming root is cod_test

    for root, dirs, files in os.walk(root_dir):
        if 'venv' in root or '.git' in root or '__pycache__' in root or 'migrations' in root:
            continue

        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, root_dir)

            # --- 1. Python Static Analysis ---
            if file.endswith('.py'):
                checks = {
                    'PRINT_STATEMENT': r'^\s*print\(', # 1.1
                    'BROAD_EXCEPT': r'except:', # 1.1
                    'UNUSED_VARIABLE': r'^\s*_\s*=', # 1.1
                    'REQUEST_FILES_DIRECT': r'request\.FILES\s*\[', # 1.3
                    'DEBUG_TRUE': r'DEBUG\s*=\s*True', # 3.2
                    'SECRET_KEY_EXPOSED': r'SECRET_KEY\s*=\s*[\'"](?!(django-insecure|os\.environ)).+[\'"]', # 3.1 (refined)
                    'EMAIL_PASSWORD_EXPOSED': r'EMAIL_HOST_PASSWORD\s*=\s*[\'"][^\'"]+[\'"]', # 3.1
                }
                
                # 2.3 URL Typos
                if 'urls.py' in file:
                    checks['URL_TYPO_UPDATE'] = r'udpate'

                # 2.2 Graphene (simpler check on settings.py)
                if file == 'settings.py':
                    checks['GRAPHENE_CONFIG'] = r'GRAPHENE\s*='
                
                check_regex_in_file(file_path, checks, python_errors)

                # 1.2 Context Processor Cart Risk (Specific file check)
                if 'context_processors.py' in file:
                     with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        if 'return ""' in f.read():
                            python_errors.append(f"[BAD_RETURN_TYPE] Context processor returns empty string in {rel_path}")

            # --- 5. Templates Analysis ---
            if file.endswith('.html'):
                checks = {
                    'HARDCODED_LINK_HASH': r'href="#"', # 7.1
                    'HARDCODED_LINK_INDEX': r'href="index\.html"', # 7.2
                    'MISSING_ALT': r'<img(?!.*alt=).*?>', # 5.1
                    'LANG_EN_MISMATCH': r'<html.*lang="en"', # 5.1
                    'BAD_FAVICON_TYPE': r'type="images/x-icon"', # 5.1
                    'UNSAFE_URL_ACCESS': r'\.url\s', # 5.2 (General, needs manual review often, but good to flag)
                    'BRAND_NAME_MISMATCH': r'Beautyhouse', # 5.3
                    'ENGLISH_LABEL_HOME': r'>\s*HOME\s*<', # 5.3
                    'ENGLISH_LABEL_SUBMIT': r'value="Submit"', # 5.3
                }
                # 5.2 Robustness specifics
                checks['UNSAFE_INFOS_ACCESS'] = r'infos\.\w+\.url'
                checks['UNSAFE_CART_COUNT'] = r'cart\.produit_panier\.count'
                
                check_regex_in_file(file_path, checks, template_errors)

            # --- 6. JS/CSS Analysis ---
            if file.endswith('.css'):
                checks = {
                    'FIXED_FONT_SIZE': r'font-size:\s*\d+px', # 6.2
                }
                check_regex_in_file(file_path, checks, js_css_errors)
            
            if file.endswith('.js'):
                 checks = {
                     'AJAX_URL_HARDCODED': r'\$\.ajax', # 6.1 (Just flagging usage)
                 }
                 check_regex_in_file(file_path, checks, js_css_errors)

    # --- 2.1 Django Check ---
    django_errors = run_django_check()

    # --- Reporting ---
    print("\n" + "="*50)
    print("      RAPPORT DE TESTS STATIQUES EXHAUSTIF")
    print("="*50)

    categories = {
        "1. PYTHON (Qualité & Risques)": python_errors,
        "2. DJANGO CONFIGURATION (Manage Check)": django_errors,
        "3. SÉCURITÉ (Secrets & Config)": security_errors, # Merged into python_errors mostly, separating logic if specific list used
        "4. DÉPENDANCES": dependency_errors,
        "5. TEMPLATES (HTML, Robustesse, Marque)": template_errors,
        "6. FRONTEND (JS/CSS)": js_css_errors
    }

    total_issues = 0
    for category, errors in categories.items():
        print(f"\n[{category}]")
        if errors:
            for e in errors:
                print(e)
            total_issues += len(errors)
        else:
            print("Aucun problème détecté (sur la base des règles définies).")

    print(f"\nTotal problèmes trouvés : {total_issues}")


def main():
    root_dir = os.getcwd()
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    scanning_directory(root_dir)

if __name__ == "__main__":
    main()
