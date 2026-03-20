import os
import re

filepath = r'c:\Users\Admin\Documents\GitHub\demo\templates\user_site\blog-single.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's extract title
title_match = re.search(r'<title>(.*?)</title>', content)
title = title_match.group(1) if title_match else 'CodeCraften'

header_end_match = re.search(r"{% include 'user_site/_header.html' %}", content)
            
# Find the start of footer section
footer_start_match = re.search(r'<!-- Start of footer section\s*============================================= -->', content)

if header_end_match and footer_start_match:
    top_part = f"""{{% extends 'user_site/base.html' %}}
{{% load static %}}
{{% block title %}}{title}{{% endblock %}}
{{% block content %}}
"""
    
    # Extract extra js scripts that are not in base.html
    footer_part = content[footer_start_match.start():]
    extra_js = []
    js_scripts = re.finditer(r'<script src="(.*?)"></script>', footer_part)
    base_js = ['jquery.min.js', 'bootstrap.min.js', 'popper.min.js', 'owl.carousel.min.js', 'jquery.magnific-popup.min.js', 'appear.js', 'wow.min.js', 'parallax-scroll.js', 'circle-progress.js', 'isotope.pkgd.min.js', 'masonry.pkgd.min.js', 'imagesloaded.pkgd.min.js', 'jquery.easeScroll.min.js', 'typer-new.js', 'script.js']
    
    for match in js_scripts:
        script_path = match.group(1)
        script_name = script_path.split('/')[-1]
        if script_name not in base_js and 'maps.google.com' not in script_path:
            extra_js.append(script_path)
    
    bottom_part = "\n{% endblock %}\n"
    if extra_js:
        bottom_part += "{% block extra_js %}\n"
        for js in extra_js:
            bottom_part += f'\t<script src="{js}"></script>\n'
        bottom_part += "{% endblock %}\n"
        
    new_content = top_part + content[header_end_match.end():footer_start_match.start()] + bottom_part
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Updated blog-single.html')
else:
    print(f'Skipped blog-single.html - could not find header or footer markers')
