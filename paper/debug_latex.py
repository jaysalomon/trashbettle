"""
LaTeX Debug Helper - Identifies common compilation issues
"""

import os
import re
from pathlib import Path

def check_files():
    """Check all referenced files exist."""
    print("=" * 60)
    print("CHECKING FILE REFERENCES")
    print("=" * 60)
    
    issues = []
    
    # Check main.tex exists
    if not os.path.exists("main.tex"):
        print("❌ ERROR: main.tex not found!")
        return
    
    # Read main.tex
    with open("main.tex", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for \input{} and \include{} commands
    input_pattern = r'\\(?:input|include)\{([^}]+)\}'
    inputs = re.findall(input_pattern, content)
    
    for inp in inputs:
        # Add .tex extension if not present
        if not inp.endswith('.tex'):
            inp = inp + '.tex'
        
        if not os.path.exists(inp):
            issues.append(f"Missing file: {inp}")
            print(f"  ❌ Missing: {inp}")
        else:
            print(f"  ✓ Found: {inp}")
    
    # Check for \includegraphics commands
    graphics_pattern = r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}'
    graphics = re.findall(graphics_pattern, content)
    
    # Also check in section files
    for section_file in Path("sections").glob("*.tex"):
        with open(section_file, 'r', encoding='utf-8') as f:
            section_content = f.read()
            graphics.extend(re.findall(graphics_pattern, section_content))
    
    print("\n" + "=" * 60)
    print("CHECKING GRAPHICS FILES")
    print("=" * 60)
    
    for graphic in graphics:
        # Check common extensions
        found = False
        for ext in ['', '.png', '.pdf', '.jpg', '.eps']:
            if os.path.exists(graphic + ext):
                print(f"  ✓ Found: {graphic + ext}")
                found = True
                break
        if not found:
            issues.append(f"Missing graphic: {graphic}")
            print(f"  ❌ Missing: {graphic}")
    
    return issues

def check_syntax():
    """Check for common LaTeX syntax issues."""
    print("\n" + "=" * 60)
    print("CHECKING SYNTAX ISSUES")
    print("=" * 60)
    
    issues = []
    
    # Check all .tex files
    tex_files = ["main.tex"] + list(Path("sections").glob("*.tex"))
    
    for tex_file in tex_files:
        with open(tex_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Check for unescaped underscores outside math mode
        for i, line in enumerate(lines, 1):
            # Skip comments
            if '%' in line:
                line = line[:line.index('%')]
            
            # Count $ signs to track math mode
            dollar_count = 0
            in_math = False
            
            for j, char in enumerate(line):
                if char == '$' and (j == 0 or line[j-1] != '\\'):
                    dollar_count += 1
                    in_math = (dollar_count % 2 == 1)
                elif char == '_' and not in_math and (j == 0 or line[j-1] != '\\'):
                    issues.append(f"{tex_file}:{i} - Unescaped underscore")
                    print(f"  ⚠ {tex_file}:{i} - Unescaped underscore: ...{line[max(0,j-10):min(len(line),j+10)]}...")
    
    # Check for mismatched braces
    for tex_file in tex_files:
        with open(tex_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        open_braces = content.count('{') - content.count('\\{')
        close_braces = content.count('}') - content.count('\\}')
        
        if open_braces != close_braces:
            issues.append(f"{tex_file} - Mismatched braces ({open_braces} open, {close_braces} close)")
            print(f"  ⚠ {tex_file} - Mismatched braces ({open_braces} open, {close_braces} close)")
    
    if not issues:
        print("  ✓ No obvious syntax issues found")
    
    return issues

def check_packages():
    """Check for potentially missing packages."""
    print("\n" + "=" * 60)
    print("CHECKING PACKAGE REQUIREMENTS")
    print("=" * 60)
    
    with open("main.tex", 'r', encoding='utf-8') as f:
        content = f.read()
    
    packages = re.findall(r'\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}', content)
    
    print("Required packages:")
    for pkg in packages:
        print(f"  • {pkg}")
    
    print("\nMake sure you have a complete LaTeX distribution installed:")
    print("  - Windows: MiKTeX or TeX Live")
    print("  - Mac: MacTeX")
    print("  - Linux: texlive-full")

def main():
    """Run all checks."""
    print("LaTeX Document Debug Report")
    print("=" * 60)
    
    os.chdir(Path(__file__).parent)
    
    all_issues = []
    
    # Check files
    file_issues = check_files()
    if file_issues:
        all_issues.extend(file_issues)
    
    # Check syntax
    syntax_issues = check_syntax()
    if syntax_issues:
        all_issues.extend(syntax_issues)
    
    # Check packages
    check_packages()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if all_issues:
        print(f"Found {len(all_issues)} potential issues:")
        for issue in all_issues:
            print(f"  • {issue}")
        print("\nFix these issues and try compiling again.")
    else:
        print("✓ No obvious issues found!")
        print("\nIf compilation still fails, check:")
        print("  1. LaTeX distribution is installed")
        print("  2. All packages are available")
        print("  3. Check main.log for specific errors")
    
    print("\nTo compile, run:")
    print("  pdflatex main.tex")
    print("  bibtex main")
    print("  pdflatex main.tex")
    print("  pdflatex main.tex")

if __name__ == "__main__":
    main()