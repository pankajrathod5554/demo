import os
import re

directory = r'c:\Users\Admin\Documents\GitHub\demo\templates\user_site'

replacements = [
    (r'>\s*Lorem ipsum dolor sit.*?</', '>Insights and Strategies</'),
    (r'Sed ut perspiciatis unde omnis iste .*?voluptatem\.', ''),
    (r'Sed ut perspiciatis unde omnis iste .*?laudantium\.', '')
]

for root, _, files in os.walk(directory):
    for filename in files:
        if filename.endswith('.html'):
            filepath = os.path.join(root, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            new_content = content
            for old, new in replacements:
                new_content = re.sub(old, new, new_content, flags=re.IGNORECASE | re.DOTALL)

            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Updated text in {filename}')
