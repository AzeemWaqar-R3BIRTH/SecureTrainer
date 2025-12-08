import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

# Define output directory
OUTPUT_DIR = r"app/static/resources"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def create_pdf(filename, title, content_sections):
    """Creates a professional PDF document."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30, textColor=colors.HexColor('#1a56db')))
    styles.add(ParagraphStyle(name='SectionHeader', parent=styles['Heading2'], fontSize=16, spaceBefore=20, spaceAfter=10, textColor=colors.HexColor('#2563eb')))
    styles.add(ParagraphStyle(name='NormalText', parent=styles['Normal'], fontSize=11, leading=14, spaceAfter=10))
    styles.add(ParagraphStyle(name='CodeBlock', parent=styles['Code'], fontSize=9, leading=12, backColor=colors.HexColor('#f3f4f6'), borderColor=colors.HexColor('#e5e7eb'), borderWidth=1, borderPadding=5, spaceAfter=10))
    styles.add(ParagraphStyle(name='BulletPoint', parent=styles['Normal'], fontSize=11, leading=14, leftIndent=20, spaceAfter=5, bulletIndent=10))

    story = []
    
    # Title
    story.append(Paragraph(title, styles['CustomTitle']))
    story.append(Spacer(1, 12))
    
    for section in content_sections:
        # Section Header
        if section.get('title'):
            story.append(Paragraph(section['title'], styles['SectionHeader']))
        
        # Content
        for item in section.get('content', []):
            if item['type'] == 'text':
                story.append(Paragraph(item['value'], styles['NormalText']))
            elif item['type'] == 'code':
                story.append(Paragraph(item['value'], styles['CodeBlock']))
            elif item['type'] == 'bullet':
                story.append(Paragraph(f"• {item['value']}", styles['BulletPoint']))
            elif item['type'] == 'spacer':
                story.append(Spacer(1, item['value']))
                
    doc.build(story)
    print(f"Generated {filename}")

# --- Content Definitions ---

sqli_content = [
    {
        'title': 'What is SQL Injection (SQLi)?',
        'content': [
            {'type': 'text', 'value': 'SQL Injection is a code injection technique where an attacker executes malicious SQL statements that control a web application\'s database server.'},
            {'type': 'text', 'value': 'It occurs when untrusted data is sent to an interpreter as part of a command or query.'}
        ]
    },
    {
        'title': 'Common Attack Vectors',
        'content': [
            {'type': 'bullet', 'value': '<b>In-band SQLi:</b> The attacker uses the same communication channel to both launch the attack and gather results (e.g., Error-based, Union-based).'},
            {'type': 'bullet', 'value': '<b>Inferential (Blind) SQLi:</b> No data is transferred via the web application, but the attacker can reconstruct the database structure by sending payloads and observing the web application\'s response (e.g., Boolean-based, Time-based).'},
            {'type': 'bullet', 'value': '<b>Out-of-band SQLi:</b> The attacker is unable to use the same channel to launch the attack and gather results.'}
        ]
    },
    {
        'title': 'Prevention Cheat Sheet',
        'content': [
            {'type': 'bullet', 'value': '<b>1. Use Prepared Statements (Parameterized Queries):</b> This is the most effective defense. It ensures that the database treats user input as data, not as executable code.'},
            {'type': 'code', 'value': 'cursor.execute("SELECT * FROM users WHERE user = %s", (username,))'},
            {'type': 'bullet', 'value': '<b>2. Use Stored Procedures:</b> Similar to prepared statements, they encapsulate the SQL query.'},
            {'type': 'bullet', 'value': '<b>3. Input Validation (Allow-list):</b> Validate input against a rigorous allow-list.'},
            {'type': 'bullet', 'value': '<b>4. Principle of Least Privilege:</b> Ensure the database account used by the application has only the minimum necessary permissions.'}
        ]
    }
]

xss_content = [
    {
        'title': 'What is Cross-Site Scripting (XSS)?',
        'content': [
            {'type': 'text', 'value': 'XSS attacks occur when an application includes untrusted data in a new web page without proper validation or escaping.'},
            {'type': 'text', 'value': 'This allows attackers to execute malicious scripts in the victim\'s browser.'}
        ]
    },
    {
        'title': 'Types of XSS',
        'content': [
            {'type': 'bullet', 'value': '<b>Stored XSS (Persistent):</b> The malicious script is permanently stored on the target server (e.g., in a database, forum post).'},
            {'type': 'bullet', 'value': '<b>Reflected XSS (Non-Persistent):</b> The malicious script is reflected off the web server, such as in an error message or search result.'},
            {'type': 'bullet', 'value': '<b>DOM-based XSS:</b> The attack payload is executed as a result of modifying the DOM "environment" in the victim\'s browser used by the original client-side script.'}
        ]
    },
    {
        'title': 'Prevention Cheat Sheet',
        'content': [
            {'type': 'bullet', 'value': '<b>1. Output Encoding:</b> Convert untrusted input into a safe form where the input is displayed as data to the user without executing as code in the browser.'},
            {'type': 'code', 'value': '&lt;script&gt;alert(1)&lt;/script&gt;  becomes  &amp;lt;script&amp;gt;alert(1)&amp;lt;/script&amp;gt;'},
            {'type': 'bullet', 'value': '<b>2. Input Validation:</b> Validate input against a strict allow-list.'},
            {'type': 'bullet', 'value': '<b>3. Content Security Policy (CSP):</b> Use CSP to restrict the sources of executable scripts.'},
            {'type': 'bullet', 'value': '<b>4. Use Modern Frameworks:</b> Frameworks like React, Vue, and Angular automatically escape XSS by default.'}
        ]
    }
]

cmd_content = [
    {
        'title': 'What is Command Injection?',
        'content': [
            {'type': 'text', 'value': 'Command injection is an attack in which the goal is execution of arbitrary commands on the host operating system via a vulnerable application.'},
            {'type': 'text', 'value': 'It happens when an application passes unsafe user supplied data (forms, cookies, HTTP headers etc.) to a system shell.'}
        ]
    },
    {
        'title': 'Prevention Strategies',
        'content': [
            {'type': 'bullet', 'value': '<b>1. Avoid Calling OS Commands:</b> Use language-specific APIs instead of system calls whenever possible (e.g., use `os.mkdir` instead of `os.system("mkdir")`).'},
            {'type': 'bullet', 'value': '<b>2. Input Validation:</b> Validate input against a rigorous allow-list. Ensure input contains only safe characters (alphanumeric).'},
            {'type': 'bullet', 'value': '<b>3. Parameterization:</b> If you must use OS commands, use functions that support argument parameterization (e.g., `subprocess.run(["ls", dirname])` instead of `os.system("ls " + dirname)`).'},
            {'type': 'code', 'value': 'import subprocess\nsubprocess.run(["ls", "-l", user_input]) # Safe'}
        ]
    }
]

webapp_checklist_content = [
    {
        'title': 'Authentication & Session Management',
        'content': [
            {'type': 'bullet', 'value': 'Enforce strong password policies (length, complexity).'},
            {'type': 'bullet', 'value': 'Implement Multi-Factor Authentication (MFA).'},
            {'type': 'bullet', 'value': 'Secure session ID generation and handling (HttpOnly, Secure flags).'},
            {'type': 'bullet', 'value': 'Implement proper session timeout and termination.'}
        ]
    },
    {
        'title': 'Access Control',
        'content': [
            {'type': 'bullet', 'value': 'Enforce Principle of Least Privilege.'},
            {'type': 'bullet', 'value': 'Verify object references (IDOR prevention).'},
            {'type': 'bullet', 'value': 'Restrict access to administrative interfaces.'}
        ]
    },
    {
        'title': 'Input Validation & Output Encoding',
        'content': [
            {'type': 'bullet', 'value': 'Validate all input against a strict allow-list.'},
            {'type': 'bullet', 'value': 'Encode all output to prevent XSS.'},
            {'type': 'bullet', 'value': 'Use parameterized queries to prevent SQLi.'}
        ]
    },
    {
        'title': 'Cryptography',
        'content': [
            {'type': 'bullet', 'value': 'Use strong, modern encryption algorithms (AES-256, RSA-2048).'},
            {'type': 'bullet', 'value': 'Hash passwords using strong hashing algorithms (Argon2, bcrypt).'},
            {'type': 'bullet', 'value': 'Manage keys securely.'}
        ]
    }
]

code_review_content = [
    {
        'title': 'General',
        'content': [
            {'type': 'bullet', 'value': 'Does the code follow the project\'s style guide?'},
            {'type': 'bullet', 'value': 'Is the code modular and reusable?'},
            {'type': 'bullet', 'value': 'Are there any hardcoded secrets or credentials?'}
        ]
    },
    {
        'title': 'Security',
        'content': [
            {'type': 'bullet', 'value': 'Is user input validated and sanitized?'},
            {'type': 'bullet', 'value': 'Are database queries parameterized?'},
            {'type': 'bullet', 'value': 'Is output encoded properly?'},
            {'type': 'bullet', 'value': 'Are sensitive data encrypted?'},
            {'type': 'bullet', 'value': 'Is error handling secure (no stack traces exposed)?'}
        ]
    },
    {
        'title': 'Performance',
        'content': [
            {'type': 'bullet', 'value': 'Are there any N+1 query problems?'},
            {'type': 'bullet', 'value': 'Is memory usage optimized?'}
        ]
    }
]

security_checklist_content = [
    {
        'title': 'Network Security',
        'content': [
            {'type': 'bullet', 'value': 'Firewalls configured correctly.'},
            {'type': 'bullet', 'value': 'Unused ports closed.'},
            {'type': 'bullet', 'value': 'IDS/IPS enabled.'}
        ]
    },
    {
        'title': 'Application Security',
        'content': [
            {'type': 'bullet', 'value': 'Regular vulnerability scanning.'},
            {'type': 'bullet', 'value': 'Penetration testing performed.'},
            {'type': 'bullet', 'value': 'Dependencies updated regularly.'}
        ]
    },
    {
        'title': 'Data Security',
        'content': [
            {'type': 'bullet', 'value': 'Data encrypted at rest and in transit.'},
            {'type': 'bullet', 'value': 'Regular backups performed and tested.'},
            {'type': 'bullet', 'value': 'Access controls reviewed regularly.'}
        ]
    }
]

# Generate PDFs
create_pdf('sqli_cheatsheet.pdf', 'SQL Injection (SQLi) Cheat Sheet', sqli_content)
create_pdf('xss_cheatsheet.pdf', 'Cross-Site Scripting (XSS) Cheat Sheet', xss_content)
create_pdf('cmd_injection_guide.pdf', 'Command Injection Prevention Guide', cmd_content)
create_pdf('webapp_checklist.pdf', 'Web Application Security Checklist', webapp_checklist_content)
create_pdf('code_review_checklist.pdf', 'Secure Code Review Checklist', code_review_content)
create_pdf('security_checklist.pdf', 'General Security Checklist', security_checklist_content)

print("All resources generated successfully.")
