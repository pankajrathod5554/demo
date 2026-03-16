import os
import re

directory = r'c:\Users\Admin\Documents\GitHub\demo\templates\user_site'

lorem_pattern = re.compile(r'Lorem ipsum dolor sit amet, consecte.*?([\.\n]|$)', re.IGNORECASE | re.DOTALL)
short_lorem_pattern = re.compile(r'Lorem ipsum dolor sit amet[\w\s,\.]*', re.IGNORECASE)

replacements = [
    # General long lorem replacements
    (r'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua\. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat\.( Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur\.)?( Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt( mollit anim id est laborum\.)?)?',
     'Our team of experts delivers tailored solutions to help your business thrive in the digital age. We focus on scalable, secure, and innovative technology to drive your success.'),
    
    (r'Lorem ipsum dolor sit amet, consecte ctetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore\.',
     'We provide professional IT services and expert consulting to streamline your business operations and securely scale your infrastructure.'),
    
    (r'Lorem ipsum dolor sit amet, consec tetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua it enim ad minim\.  veniam\.',
     "Delivering secure, scalable, and high-performance IT solutions that empower your brand's digital presence and ensure seamless user experiences."),

    (r'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do\.',
     'Enhancing business workflows through dedicated technology solutions.'),

    (r'Lorem ipsum dolor sit amet, conse ctet ur adipisicing elit, sed doing\.',
     'Empowering businesses with modern technology infrastructure.'),

    (r'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore\.',
     'We provide innovative software development and managed IT support.'),

    (r'Lorem ipsum dolor sit amet, consectetur adipisicing elit, se id do eiusmod tempor incididunt ut labore et dolore magna aliqua\. Ut enim ad minim veniam, quis nostrud\.',
     'A highly skilled professional committed to delivering the best results.'),
     
     (r'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua\. Ut enim ad minim veniam, quis nostrud exercitation is enougn for today\.',
      'An experienced writer and technology enthusiast focused on the latest industry trends.')
]

# Specifically replace some titles
titles_to_replace = {
    'Lorem ipsum dolor sit amet, consecte': 'Innovative Technology Solutions'
}

for root, _, files in os.walk(directory):
    for filename in files:
        if filename.endswith('.html'):
            filepath = os.path.join(root, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            new_content = content
            for old, new in replacements:
                new_content = re.sub(old, new, new_content, flags=re.IGNORECASE)

            # Titles
            for old, new in titles_to_replace.items():
                new_content = new_content.replace(old, new)

            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Updated text in {filename}')
