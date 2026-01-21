#!/usr/bin/env python3
"""Generate HTML preview from README.md with custom CSS"""

import re
import os

def read_markdown(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def markdown_to_html(markdown_text):
    """Simple markdown to HTML converter with per-section list numbering"""
    lines = markdown_text.split('\n')
    processed_lines = []
    list_counter = 1
    in_list = False
    
    for i, line in enumerate(lines):
        # h2の場合、リストカウンターをリセット
        if line.startswith('## '):
            if in_list:
                processed_lines[-1] += '</ol>'
                in_list = False
            list_counter = 1
            processed_lines.append(re.sub(r'^## (.*?)$', r'<h2>\1</h2>', line))
            continue
        
        # h1
        if line.startswith('# '):
            if in_list:
                processed_lines[-1] += '</ol>'
                in_list = False
            processed_lines.append(re.sub(r'^# (.*?)$', r'<h1>\1</h1>', line))
            continue
        
        # h3
        if line.startswith('### '):
            processed_lines.append(re.sub(r'^### (.*?)$', r'<h3>\1</h3>', line))
            continue
        
        # Handle numbered list items (1. 2. 3. etc)
        if re.match(r'^\d+\.\s+', line):
            if not in_list:
                in_list = True
            
            # 番号をリセット済みのカウンターに置き換え
            item_content = re.sub(r'^\d+\.\s+', '', line)
            
            # リンク変換
            item_content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', item_content)
            
            # Bold and italic
            item_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', item_content)
            item_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', item_content)
            
            processed_lines.append(f'<li>{item_content}</li>')
            list_counter += 1
            continue
        
        # Handle bullet lists
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_list:
                in_list = True
            item_content = re.sub(r'^[-*]\s+', '', line)
            item_content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', item_content)
            processed_lines.append(f'<li>{item_content}</li>')
            continue
        
        # Close list if we hit non-list content
        if in_list and line.strip() and not re.match(r'^\d+\.\s+', line) and not re.match(r'^[-*]\s+', line) and not line.startswith('#'):
            processed_lines[-1] += '</ol>'
            in_list = False
        
        # Handle empty lines
        if not line.strip():
            if in_list and processed_lines and not processed_lines[-1].endswith('</li>'):
                processed_lines[-1] += '</ol>'
                in_list = False
            processed_lines.append('')
            continue
        
        # Regular paragraphs
        if line.strip() and not line.startswith('#'):
            # Links and formatting
            line = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', line)
            line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            line = re.sub(r'\*(.*?)\*', r'<em>\1</em>', line)
            
            if not in_list:
                processed_lines.append(f'<p>{line}</p>')
            else:
                processed_lines.append(line)
            continue
        
        processed_lines.append(line)
    
    # Close any open list at the end
    if in_list:
        for i in range(len(processed_lines)-1, -1, -1):
            if processed_lines[i].strip().endswith('</li>'):
                processed_lines[i] += '</ol>'
                break
    
    # Wrap consecutive list items in <ol> tags
    result = []
    i = 0
    while i < len(processed_lines):
        if processed_lines[i].startswith('<li>'):
            # Collect all consecutive list items
            list_items = []
            while i < len(processed_lines) and processed_lines[i].startswith('<li>'):
                list_items.append(processed_lines[i])
                i += 1
            result.append('<ol>' + '\n'.join(list_items) + '</ol>')
        else:
            result.append(processed_lines[i])
            i += 1
    
    return '\n'.join(result)

def generate_html_preview(readme_path, css_path, output_path):
    """Generate HTML preview file"""
    
    readme_content = read_markdown(readme_path)
    
    # Read CSS
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
    except FileNotFoundError:
        css_content = ""
    
    # Convert markdown to HTML
    body_html = markdown_to_html(readme_content)
    
    # Generate complete HTML
    html_template = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>鷹森ツヅル歌枠一覧</title>
    <style>
{css_content}
    </style>
</head>
<body>
    <div class="container">
{body_html}
    </div>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✓ Preview generated: {output_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    readme_path = os.path.join(script_dir, "README.md")
    css_path = os.path.join(script_dir, "assets/css/style.css")
    output_path = os.path.join(script_dir, "preview.html")
    
    generate_html_preview(readme_path, css_path, output_path)
