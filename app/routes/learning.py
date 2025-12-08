"""
Learning Center Routes for SecureTrainer
Handles content management, progress tracking, and learning analytics
"""

from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from app.models.user_model import get_user_by_id, update_user_comprehensive
from app.models.analytics_model import record_user_activity
from app.routes.ai_model import get_achievement_recommendations
import os
import time
from datetime import datetime, timedelta
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

learning_bp = Blueprint('learning', __name__, url_prefix='/api/learning')

# Learning content structure
LEARNING_CONTENT = {
    'intro': {
        'id': 'intro',
        'title': 'Introduction to Cybersecurity Training',
        'description': 'Overview of cybersecurity fundamentals and SecureTrainer platform',
        'difficulty': 'beginner',
        'estimated_time': 30,
        'sections': [
            {
                'id': 'intro_video',
                'title': 'Getting Started Video',
                'type': 'video',
                'video_url': 'https://www.youtube.com/embed/_DVVNOGYtmU',
                'estimated_time': 15
            },
            {
                'id': 'intro_overview',
                'title': 'Platform Overview',
                'type': 'text',
                'content': '''Welcome to SecureTrainer, your gateway to mastering the art of cybersecurity. In an era where digital threats are evolving at an unprecedented pace, understanding the fundamentals of security is no longer just an option—it's a necessity. From individual privacy to national security, the digital realm is the new frontline. This platform is designed to take you from a novice to a security-conscious developer, capable of identifying and mitigating real-world vulnerabilities.

The cybersecurity landscape has shifted dramatically in recent years. We've moved beyond simple viruses and phishing emails to sophisticated, state-sponsored cyberattacks, ransomware-as-a-service gangs, and AI-driven threats. Attackers are leveraging machine learning to automate vulnerability scanning and craft convincing social engineering campaigns. As a defender, you must stay ahead of the curve. SecureTrainer provides a hands-on, interactive environment where you don't just read about vulnerabilities—you exploit them in a controlled setting to understand their mechanics deeply.

Our curriculum is structured to build a solid foundation. You'll start with the basics of web security, understanding how the internet works, the HTTP protocol, and the anatomy of a web request. From there, we dive into specific vulnerability classes like SQL Injection, Cross-Site Scripting (XSS), and Command Injection. Each module combines theoretical knowledge with practical labs, ensuring you gain actionable skills. You'll learn not just how to break systems, but more importantly, how to fix them using industry-standard best practices.

We also emphasize the importance of a 'security-first' mindset. Security isn't a feature you sprinkle on at the end of development; it's a process that begins with the first line of code. You'll explore concepts like the Secure Development Lifecycle (SDLC), the principle of least privilege, and defense in depth. By the end of this training, you'll be equipped with the tools and knowledge to build robust, secure applications that can withstand the modern threat landscape. Get ready to challenge yourself, think like an attacker, and defend like a pro.''',
                'estimated_time': 10
            }
        ],
        'prerequisites': [],
        'learning_objectives': [
            'Understand the SecureTrainer platform',
            'Learn about cybersecurity fundamentals',
            'Prepare for advanced security topics'
        ]
    },
    
    'sql': {
        'id': 'sql',
        'title': 'SQL Injection',
        'description': 'Learn to identify and prevent SQL injection vulnerabilities',
        'difficulty': 'intermediate',
        'estimated_time': 60,
        'sections': [
            {
                'id': 'sql_video',
                'title': 'SQL Injection Tutorial',
                'type': 'video',
                'video_url': 'https://www.youtube.com/embed/2OPVViV-GQk',
                'estimated_time': 25
            },
            {
                'id': 'sql_theory',
                'title': 'SQL Injection Theory',
                'type': 'text',
                'content': '''SQL Injection (SQLi) remains one of the most prevalent and devastating web application vulnerabilities, despite being known for over two decades. At its core, SQLi occurs when an application improperly handles user input, allowing an attacker to interfere with the queries the application makes to its database. This can lead to unauthorized access to sensitive data, such as user passwords, credit card details, or personal information. In severe cases, it can even allow an attacker to modify or delete data, or gain administrative control over the database server.

In the modern web landscape, the impact of SQLi has only grown. With the rise of cloud-native applications and microservices, a single SQLi vulnerability can compromise an entire ecosystem. Attackers use automated tools like SQLMap to scan millions of websites, identifying and exploiting vulnerabilities in minutes. They employ advanced techniques like blind SQL injection, where they infer data based on the application's response time or error messages, even when no data is directly returned.

However, the defense mechanisms have also evolved. The golden standard for preventing SQLi is the use of Parameterized Queries (also known as Prepared Statements). This technique ensures that the database treats user input as data, not as executable code, effectively neutralizing the attack. Modern Object-Relational Mapping (ORM) frameworks like Hibernate, Entity Framework, and Sequelize also provide built-in protection against SQLi, provided they are used correctly.

But relying solely on tools isn't enough. Developers must understand the underlying mechanics. You need to know *why* specific query patterns are dangerous and *how* to fix them. In this module, you will dissect the anatomy of a SQL injection attack. You'll learn about different types of SQLi—In-band, Inferential (Blind), and Out-of-band. You'll practice exploiting these vulnerabilities in our safe labs and then implement robust fixes. Remember, a single unsanitized input is all it takes to breach a fortress. Vigilance is key.''',
                'estimated_time': 20
            },
            {
                'id': 'sql_practice',
                'title': 'Practice SQL Injection',
                'type': 'interactive',
                'content': 'Try SQL injection techniques in our safe environment',
                'challenge_id': 'sql_1',
                'estimated_time': 15
            }
        ],
        'prerequisites': ['intro'],
        'learning_objectives': [
            'Understand SQL injection mechanisms',
            'Learn prevention techniques',
            'Practice safe SQL injection testing'
        ]
    },
    
    'xss': {
        'id': 'xss',
        'title': 'Cross-Site Scripting (XSS)',
        'description': 'Master XSS detection and prevention techniques',
        'difficulty': 'intermediate',
        'estimated_time': 45,
        'sections': [
            {
                'id': 'xss_video',
                'title': 'XSS Attack Demonstration',
                'type': 'video',
                'video_url': 'https://www.youtube.com/embed/ns1LX6mEvyM',
                'estimated_time': 20
            },
            {
                'id': 'xss_theory',
                'title': 'XSS Fundamentals',
                'type': 'text',
                'content': '''Cross-Site Scripting (XSS) is a deceptively simple yet incredibly dangerous vulnerability that targets the users of an application rather than the server itself. It occurs when an application includes untrusted data in a web page without proper validation or escaping. This allows an attacker to execute malicious scripts—usually JavaScript—in the victim's browser. The consequences can be severe: session hijacking, theft of sensitive data, redirection to malicious sites, or even defacement of the website.

In the age of Single Page Applications (SPAs) and heavy client-side rendering with frameworks like React, Vue, and Angular, the nature of XSS has evolved. While these frameworks offer some built-in protection, they also introduce new pitfalls. For example, using `dangerouslySetInnerHTML` in React or `v-html` in Vue can instantly open the door to XSS if not handled with extreme care. Moreover, the complexity of modern JavaScript ecosystems means that a vulnerability in a third-party dependency can introduce XSS risks into your application.

There are three main types of XSS you need to master:
1.  **Reflected XSS**: The malicious script comes from the current HTTP request (e.g., a URL parameter). It's often used in phishing attacks where a user is tricked into clicking a malicious link.
2.  **Stored XSS**: The malicious script is stored in the application's database (e.g., in a comment field) and served to other users later. This is particularly dangerous as it can affect every user who views the compromised page.
3.  **DOM-based XSS**: The vulnerability exists in the client-side code rather than the server-side code. The attack payload is executed by modifying the DOM environment in the victim's browser.

Defending against XSS requires a multi-layered approach. The first line of defense is **Output Encoding**—converting special characters into their HTML entity equivalents before rendering them. However, the most robust defense is a strong **Content Security Policy (CSP)**. A well-configured CSP can prevent the browser from executing unauthorized scripts, effectively mitigating the impact of an XSS vulnerability even if one exists. In this module, you'll learn how to craft payloads to bypass filters and, crucially, how to implement these defenses to secure your applications.''',
                'estimated_time': 15
            },
            {
                'id': 'xss_practice',
                'title': 'XSS Practice Lab',
                'type': 'interactive',
                'content': 'Practice XSS techniques safely',
                'challenge_id': 'xss_1',
                'estimated_time': 10
            }
        ],
        'prerequisites': ['intro'],
        'learning_objectives': [
            'Identify XSS vulnerability types',
            'Learn XSS prevention methods',
            'Practice secure coding techniques'
        ]
    },
    
    'cmd': {
        'id': 'cmd',
        'title': 'Command Injection',
        'description': 'Understand command injection vulnerabilities and prevention',
        'difficulty': 'advanced',
        'estimated_time': 50,
        'sections': [
            {
                'id': 'cmd_video',
                'title': 'Command Injection Examples',
                'type': 'video',
                'video_url': 'https://www.youtube.com/embed/KbWn4L2dcHU',
                'estimated_time': 20
            },
            {
                'id': 'cmd_theory',
                'title': 'Command Injection Basics',
                'type': 'text',
                'content': '''Command Injection (often confused with Code Execution) is a critical vulnerability that allows an attacker to execute arbitrary operating system commands on the server hosting an application. This typically happens when an application passes unsafe user supplied data (forms, cookies, HTTP headers, etc.) to a system shell. In a command injection attack, the attacker-supplied operating system commands are usually executed with the privileges of the vulnerable application.

The implications of a successful command injection attack are catastrophic. An attacker can gain complete control over the server, steal sensitive data, modify system files, or use the compromised server as a launchpad for further attacks within the internal network. This vulnerability is particularly common in legacy applications, administrative interfaces, and IoT devices where direct system interaction is frequent.

Consider a simple feature that allows an administrator to ping a server to check its status. If the application takes the IP address input and directly concatenates it into a shell command like `ping [user_input]`, an attacker could input `127.0.0.1; cat /etc/passwd`. The semicolon acts as a command separator, causing the server to execute the ping command followed immediately by displaying the system's password file.

Preventing command injection requires a strict adherence to the principle of 'never trust user input.' The most effective defense is to avoid calling system commands directly. Most modern programming languages provide built-in libraries to perform common system tasks (like file manipulation or network requests) without invoking a shell. If you *must* use system commands, use parameterized functions (like `subprocess.run` in Python with `shell=False`) that treat arguments as data, not executable code. Input validation is also crucial—ensure that input conforms to a strict allowlist (e.g., only allowing IP address formats) rather than trying to blacklist dangerous characters.''',
                'estimated_time': 20
            },
            {
                'id': 'cmd_practice',
                'title': 'Command Injection Lab',
                'type': 'interactive',
                'content': 'Practice command injection in controlled environment',
                'challenge_id': 'cmd_1',
                'estimated_time': 10
            }
        ],
        'prerequisites': ['intro', 'sql'],
        'learning_objectives': [
            'Understand command injection risks',
            'Learn secure command execution',
            'Practice vulnerability assessment'
        ]
    },
    
    'auth': {
        'id': 'auth',
        'title': 'Secure Authentication',
        'description': 'Learn authentication best practices and QR code security',
        'difficulty': 'intermediate',
        'estimated_time': 40,
        'sections': [
            {
                'id': 'auth_video',
                'title': 'Authentication Best Practices',
                'type': 'video',
                'video_url': 'https://www.youtube.com/embed/UBUNrFtufWo',
                'estimated_time': 20
            },
            {
                'id': 'auth_theory',
                'title': 'Authentication Fundamentals',
                'type': 'text',
                'content': '''Authentication is the gatekeeper of your application. It answers the fundamental question: 'Who are you?' In the past, a simple username and password combination was considered sufficient. Today, however, relying solely on passwords is a recipe for disaster. Credential stuffing attacks, where attackers use billions of leaked username/password pairs to breach accounts, are automated and relentless. If your users reuse passwords (and they do), your application is at risk.

Modern secure authentication has moved towards a multi-layered approach. **Multi-Factor Authentication (MFA)** is no longer an optional feature for serious applications; it's a requirement. Whether it's a Time-based One-Time Password (TOTP) from an authenticator app, a push notification, or a hardware key (FIDO2/WebAuthn), adding a second factor exponentially increases the difficulty for an attacker.

We are also seeing a shift towards passwordless authentication. Technologies like Passkeys (built on WebAuthn) allow users to sign in using the biometric sensors on their devices (FaceID, TouchID) or local PINs, eliminating the need to transmit shared secrets over the network. This not only improves security by removing the target (the password database) but also enhances the user experience.

However, implementing authentication is fraught with pitfalls. A common mistake is rolling your own crypto or session management. Always use established libraries and protocols like OAuth 2.0 and OpenID Connect (OIDC) for handling identity. Ensure that session tokens are stored securely (HttpOnly, Secure cookies), have appropriate expiration times, and are invalidated properly upon logout. In this module, you will learn how to implement robust authentication flows, avoid common bypass techniques, and secure your user's identity against modern threats.''',
                'estimated_time': 15
            },
            {
                'id': 'auth_practice',
                'title': 'Authentication Challenge',
                'type': 'interactive',
                'content': 'Practice authentication bypass techniques',
                'challenge_id': 'auth_1',
                'estimated_time': 5
            }
        ],
        'prerequisites': ['intro'],
        'learning_objectives': [
            'Understand authentication mechanisms',
            'Learn multi-factor authentication',
            'Practice secure authentication implementation'
        ]
    },
    
    'best-practices': {
        'id': 'best-practices',
        'title': 'Security Best Practices',
        'description': 'Industry standards and guidelines for secure development',
        'difficulty': 'beginner',
        'estimated_time': 45,
        'sections': [
            {
                'id': 'bp_video',
                'title': 'OWASP Top 10 Overview',
                'type': 'video',
                'video_url': 'https://www.youtube.com/embed/nrhxNNH5lt0',
                'estimated_time': 20
            },
            {
                'id': 'bp_theory',
                'title': 'Secure Development Lifecycle',
                'type': 'text',
                'content': '''Security is not a destination; it's a journey. It's not a product you buy, but a process you practice. In the fast-paced world of DevOps and CI/CD, traditional security models—where a security team audits code right before deployment—are bottlenecks that no longer work. This has given rise to **DevSecOps**, the philosophy of integrating security practices into the DevOps process. This is often referred to as 'Shifting Left'—moving security earlier in the development lifecycle.

A core component of this is the **Secure Development Lifecycle (SDLC)**. This involves threat modeling during the design phase, secure coding practices during development, and automated security testing (SAST/DAST) during the build process. By catching vulnerabilities early, you save time, money, and reputation.

One of the most critical areas to focus on is **Dependency Management**. Modern applications are built on top of thousands of open-source libraries. A vulnerability in a single dependency (like the infamous Log4Shell) can compromise your entire application. Tools like Software Composition Analysis (SCA) can automatically scan your dependencies for known vulnerabilities and alert you to updates.

Another pillar of best practices is **Secret Management**. Never, ever hardcode API keys, database passwords, or encryption keys in your source code. Use environment variables or dedicated secret management vaults (like HashiCorp Vault or AWS Secrets Manager) to handle sensitive credentials. Finally, remember the **OWASP Top 10**. This list represents the most critical web application security risks. Familiarizing yourself with these vulnerabilities—and how to prevent them—is the baseline for any security-conscious developer. In this module, we will explore these frameworks and provide you with actionable checklists to ensure your applications are secure by design.''',
                'estimated_time': 15
            },
            {
                'id': 'bp_checklist',
                'title': 'Security Checklist',
                'type': 'resource',
                'content': 'Download our comprehensive security checklist',
                'resource_url': '/static/resources/security_checklist.pdf',
                'estimated_time': 10
            }
        ],
        'prerequisites': ['intro'],
        'learning_objectives': [
            'Understand secure development lifecycle',
            'Learn OWASP Top 10',
            'Apply security checklists'
        ]
    },

    'resources': {
        'id': 'resources',
        'title': 'Downloadable Resources',
        'description': 'Cheat sheets, checklists, and reference materials',
        'difficulty': 'beginner',
        'estimated_time': 15,
        'sections': [
            {
                'id': 'res_cheatsheets',
                'title': 'Security Cheat Sheets',
                'type': 'resource',
                'content': 'Quick reference guides for common vulnerabilities',
                'resources': [
                    {'title': 'SQL Injection Cheat Sheet', 'url': '/static/resources/sqli_cheatsheet.pdf', 'icon': 'fas fa-database'},
                    {'title': 'XSS Prevention Cheat Sheet', 'url': '/static/resources/xss_cheatsheet.pdf', 'icon': 'fas fa-code'},
                    {'title': 'Command Injection Guide', 'url': '/static/resources/cmd_injection_guide.pdf', 'icon': 'fas fa-terminal'}
                ],
                'estimated_time': 5
            },
            {
                'id': 'res_checklists',
                'title': 'Security Checklists',
                'type': 'resource',
                'content': 'Comprehensive checklists for security assessments',
                'resources': [
                    {'title': 'Web App Security Checklist', 'url': '/static/resources/webapp_checklist.pdf', 'icon': 'fas fa-clipboard-check'},
                    {'title': 'Secure Code Review Checklist', 'url': '/static/resources/code_review_checklist.pdf', 'icon': 'fas fa-glasses'}
                ],
                'estimated_time': 5
            },
            {
                'id': 'res_tools',
                'title': 'Recommended Tools',
                'type': 'resource',
                'content': 'Essential security tools for your penetration testing toolkit',
                'resources': [
                    {'title': 'Burp Suite Community', 'url': 'https://portswigger.net/burp/communitydownload', 'icon': 'fas fa-bug'},
                    {'title': 'OWASP ZAP', 'url': 'https://www.zaproxy.org/', 'icon': 'fas fa-bolt'},
                    {'title': 'SQLMap', 'url': 'https://sqlmap.org/', 'icon': 'fas fa-database'},
                    {'title': 'Nmap', 'url': 'https://nmap.org/', 'icon': 'fas fa-network-wired'},
                    {'title': 'Wireshark', 'url': 'https://www.wireshark.org/', 'icon': 'fas fa-wave-square'},
                    {'title': 'Metasploit Framework', 'url': 'https://www.metasploit.com/', 'icon': 'fas fa-bomb'}
                ],
                'estimated_time': 5
            }
        ],
        'prerequisites': [],
        'learning_objectives': [
            'Access reference materials',
            'Utilize security checklists',
            'Explore security tools'
        ]
    }
}

# User progress tracking
def get_user_learning_progress(user_id):
    """Get user's learning progress across all modules with database resilience."""
    import time
    
    max_attempts = 3
    initial_delay = 0.1  # 100ms
    max_timeout = 5  # 5 seconds total
    
    for attempt in range(max_attempts):
        try:
            from app.models.user_model import get_db
            
            # Get database connection with timeout
            db = get_db()
            if db is None:
                logger.warning(f"Database connection unavailable (attempt {attempt + 1}/{max_attempts})")
                if attempt < max_attempts - 1:
                    time.sleep(initial_delay * (2 ** attempt))  # Exponential backoff
                    continue
                return None
            
            # Verify collection exists
            if 'learning_progress' not in db.list_collection_names():
                logger.warning("learning_progress collection does not exist, initializing...")
                # Collection will be created on first insert
            
            # Query with timeout
            start_time = time.time()
            progress = db.learning_progress.find_one(
                {'user_id': user_id},
                max_time_ms=5000  # 5 second query timeout
            )
            
            query_time = time.time() - start_time
            if query_time > 1.0:
                logger.warning(f"Slow query for user {user_id}: {query_time:.2f}s")
            
            if not progress:
                # Initialize progress for new user
                logger.info(f"Initializing learning progress for user {user_id}")
                progress = {
                    'user_id': user_id,
                    'modules': {},
                    'overall_progress': 0,
                    'last_accessed': datetime.utcnow(),
                    'total_study_time': 0
                }
                try:
                    db.learning_progress.insert_one(progress)
                    logger.info(f"Learning progress initialized for user {user_id}")
                except Exception as insert_error:
                    logger.error(f"Failed to initialize progress for user {user_id}: {insert_error}")
                    # Return the structure even if insert failed
            
            return progress
            
        except Exception as e:
            logger.error(f"Error getting learning progress (attempt {attempt + 1}/{max_attempts}): {e}")
            
            # If not the last attempt, retry with backoff
            if attempt < max_attempts - 1:
                delay = initial_delay * (2 ** attempt)
                logger.info(f"Retrying in {delay:.2f}s...")
                time.sleep(delay)
            else:
                logger.error(f"All retry attempts exhausted for user {user_id}")
                return None
    
    return None

def update_user_learning_progress(user_id, module_id, section_id, completed=True):
    """Update user's progress for a specific section."""
    try:
        from app.models.user_model import get_db
        db = get_db()
        if not db:
            return False
            
        # Get current progress
        progress = get_user_learning_progress(user_id)
        if not progress:
            return False
            
        # Initialize module progress if not exists
        if module_id not in progress['modules']:
            progress['modules'][module_id] = {
                'completed_sections': [],
                'progress_percentage': 0,
                'time_spent': 0,
                'last_accessed': datetime.utcnow()
            }
        
        # Update section completion
        if completed and section_id not in progress['modules'][module_id]['completed_sections']:
            progress['modules'][module_id]['completed_sections'].append(section_id)
        
        # Calculate module progress
        total_sections = len(LEARNING_CONTENT.get(module_id, {}).get('sections', []))
        completed_sections = len(progress['modules'][module_id]['completed_sections'])
        
        if total_sections > 0:
            progress['modules'][module_id]['progress_percentage'] = (completed_sections / total_sections) * 100
        
        # Update last accessed
        progress['modules'][module_id]['last_accessed'] = datetime.utcnow()
        progress['last_accessed'] = datetime.utcnow()
        
        # Calculate overall progress
        total_modules = len(LEARNING_CONTENT)
        overall_progress = sum(mod['progress_percentage'] for mod in progress['modules'].values()) / total_modules
        progress['overall_progress'] = overall_progress
        
        # Update in database
        db.learning_progress.update_one(
            {'user_id': user_id},
            {'$set': progress}
        )
        
        return True
        
    except Exception as e:
        print(f"Error updating learning progress: {e}")
        return False

@learning_bp.route('/content/<module_id>', methods=['GET'])
def get_learning_content(module_id):
    """Get learning content for a specific module with enhanced error handling."""
    try:
        # Check if user is authenticated
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        user_id = session['user_id']
        
        # Use enhanced content loading system
        try:
            from app.utils.enhanced_learning_system import get_enhanced_learning_content
            
            user_context = {
                'user_id': user_id,
                'session_data': dict(session)
            }
            
            success, content = get_enhanced_learning_content(module_id, user_context)
            
            if success:
                # Record activity
                record_user_activity(user_id, f'learning_content_accessed_{module_id}')
                
                return jsonify({
                    'success': True,
                    'content': content,
                    'enhanced_loading': True
                })
            else:
                # Content loading failed, but we have fallback content
                return jsonify({
                    'success': True,
                    'content': content,
                    'fallback_mode': True,
                    'message': 'Content loaded in fallback mode'
                })
                
        except ImportError:
            # Enhanced system not available, use original logic
            pass
        
        # Original content loading logic as fallback
        # Validate module ID
        if module_id not in LEARNING_CONTENT:
            return jsonify({
                'success': False,
                'error': 'Module not found'
            }), 404
        
        # Get module content
        content = LEARNING_CONTENT[module_id].copy()
        
        # Get user's progress for this specific module (new system)
        from app.models.user_model import get_db
        db = get_db()
        
        module_progress_doc = db.learning_progress.find_one({
            'user_id': user_id,
            'module_id': module_id
        })
        
        if module_progress_doc:
            # Use the new progress document structure
            content['user_progress'] = {
                'is_complete': module_progress_doc.get('is_complete', False),
                'manually_completed': module_progress_doc.get('manually_completed', False),
                'scroll_percentage': module_progress_doc.get('scroll_percentage', 0),
                'time_spent': module_progress_doc.get('time_spent', 0),
                'sections_visited': module_progress_doc.get('sections_visited', []),
                'criteria_met': module_progress_doc.get('criteria_met', {})
            }
        else:
            content['user_progress'] = {
                'is_complete': False,
                'manually_completed': False,
                'scroll_percentage': 0,
                'time_spent': 0,
                'sections_visited': [],
                'criteria_met': {}
            }
        
        # Record activity
        record_user_activity(user_id, f'learning_content_accessed_{module_id}')
        
        return jsonify({
            'success': True,
            'content': content
        })
        
    except Exception as e:
        print(f"Error getting learning content: {e}")
        
        # Generate emergency fallback content
        fallback_content = {
            'id': module_id,
            'title': 'Content Loading Error',
            'description': 'There was an issue loading this content.',
            'sections': [{
                'id': 'error_notice',
                'title': 'Loading Issue',
                'type': 'text',
                'content': 'We\'re experiencing technical difficulties. Please try refreshing the page or contact support.',
                'estimated_time': 1
            }],
            'user_progress': {
                'completed_sections': [],
                'progress_percentage': 0,
                'time_spent': 0
            },
            'error_mode': True
        }
        
        return jsonify({
            'success': True,
            'content': fallback_content,
            'error_mode': True,
            'message': 'Content loaded in emergency fallback mode'
        })

@learning_bp.route('/progress', methods=['GET'])
def get_learning_progress():
    """Get user's overall learning progress."""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        user_id = session['user_id']
        
        # Get database connection
        from app.models.user_model import get_db
        db = get_db()
        
        # Get all module progress documents for this user (new system)
        module_progress_docs = list(db.learning_progress.find({'user_id': user_id}))
        
        # Build progress data structure
        formatted_progress = {
            'overall': {
                'percentage': 0,
                'total_study_time': 0
            },
            'modules': {}
        }
        
        total_modules = len(LEARNING_CONTENT)
        completed_modules = 0
        total_progress = 0
        
        # Add module-specific progress
        for module_id, module_data in LEARNING_CONTENT.items():
            # Find progress document for this module
            module_doc = next((doc for doc in module_progress_docs if doc.get('module_id') == module_id), None)
            
            if module_doc:
                is_complete = module_doc.get('is_complete', False)
                manually_completed = module_doc.get('manually_completed', False)
                
                # ONLY show 100% if user manually marked it complete via checkbox
                # Otherwise calculate progress based on criteria met
                if is_complete and manually_completed:
                    # User clicked the checkbox - show 100% complete
                    percentage = 100
                    completed_modules += 1
                else:
                    # Calculate percentage based on criteria met (automatic tracking)
                    # This gives partial progress but NOT 100% without checkbox
                    criteria_met = module_doc.get('criteria_met', {})
                    met_count = sum(1 for v in criteria_met.values() if v)
                    total_criteria = len(criteria_met) if criteria_met else 4
                    
                    if total_criteria > 0:
                        # Cap automatic progress at 95% - user must click checkbox for 100%
                        auto_percentage = (met_count / total_criteria * 100)
                        percentage = min(95, auto_percentage)
                    else:
                        percentage = 0
                
                total_progress += percentage
                
                formatted_progress['modules'][module_id] = {
                    'title': module_data['title'],
                    'percentage': round(percentage, 1),
                    'completed_sections': len(module_doc.get('sections_visited', [])),
                    'total_sections': len(module_data['sections']),
                    'time_spent': module_doc.get('time_spent', 0),
                    'last_accessed': module_doc.get('last_updated'),
                    'is_complete': is_complete and manually_completed  # Only true if checkbox clicked
                }
                
                # Add to total study time
                formatted_progress['overall']['total_study_time'] += module_doc.get('time_spent', 0)
            else:
                # No progress yet for this module
                formatted_progress['modules'][module_id] = {
                    'title': module_data['title'],
                    'percentage': 0,
                    'completed_sections': 0,
                    'total_sections': len(module_data['sections']),
                    'time_spent': 0,
                    'last_accessed': None,
                    'is_complete': False
                }
        
        # Calculate overall progress
        if total_modules > 0:
            formatted_progress['overall']['percentage'] = round(total_progress / total_modules, 1)
        
        return jsonify({
            'success': True,
            'progress': formatted_progress
        })
        
    except Exception as e:
        logger.error(f"Error getting learning progress: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to load progress'
        }), 500

@learning_bp.route('/progress/<module_id>/<section_id>', methods=['POST'])
def update_section_progress(module_id, section_id):
    """Update progress for a specific section."""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        user_id = session['user_id']
        data = request.get_json() or {}
        
        # Validate module and section
        if module_id not in LEARNING_CONTENT:
            return jsonify({
                'success': False,
                'error': 'Module not found'
            }), 404
        
        module = LEARNING_CONTENT[module_id]
        section_exists = any(s['id'] == section_id for s in module['sections'])
        
        if not section_exists:
            return jsonify({
                'success': False,
                'error': 'Section not found'
            }), 404
        
        # Update progress
        completed = data.get('completed', True)
        time_spent = data.get('time_spent', 0)
        
        success = update_user_learning_progress(user_id, module_id, section_id, completed)
        
        if success:
            # Record activity
            record_user_activity(user_id, f'learning_section_completed_{module_id}_{section_id}')
            
            return jsonify({
                'success': True,
                'message': 'Progress updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update progress'
            }), 500
            
    except Exception as e:
        print(f"Error updating section progress: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update progress'
        }), 500

@learning_bp.route('/search', methods=['GET'])
def search_content():
    """Search learning content."""
    try:
        query = request.args.get('q', '').strip()
        
        if len(query) < 2:
            return jsonify({
                'success': True,
                'results': []
            })
        
        results = []
        
        # Search through all content
        for module_id, module_data in LEARNING_CONTENT.items():
            # Search in module title and description
            if (query.lower() in module_data['title'].lower() or 
                query.lower() in module_data['description'].lower()):
                results.append({
                    'type': 'module',
                    'module_id': module_id,
                    'title': module_data['title'],
                    'description': module_data['description'],
                    'match_type': 'title_or_description'
                })
            
            # Search in sections
            for section in module_data['sections']:
                if (query.lower() in section['title'].lower() or 
                    query.lower() in section.get('content', '').lower()):
                    results.append({
                        'type': 'section',
                        'module_id': module_id,
                        'section_id': section['id'],
                        'title': section['title'],
                        'module_title': module_data['title'],
                        'match_type': 'section_content'
                    })
        
        # Limit results
        results = results[:10]
        
        # Record search activity
        if 'user_id' in session:
            record_user_activity(session['user_id'], f'learning_search_{query}')
        
        return jsonify({
            'success': True,
            'results': results,
            'query': query
        })
        
    except Exception as e:
        print(f"Error searching content: {e}")
        return jsonify({
            'success': False,
            'error': 'Search failed'
        }), 500

@learning_bp.route('/recommendations', methods=['GET'])
def get_learning_recommendations():
    """Get personalized learning recommendations."""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        user_id = session['user_id']
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Get user's progress
        progress = get_user_learning_progress(user_id)
        
        recommendations = []
        
        # Recommend next modules based on prerequisites and progress
        for module_id, module_data in LEARNING_CONTENT.items():
            module_progress = progress['modules'].get(module_id, {}) if progress else {}
            completion_percentage = module_progress.get('progress_percentage', 0)
            
            # Check if prerequisites are met
            prerequisites_met = True
            for prereq in module_data.get('prerequisites', []):
                prereq_progress = progress['modules'].get(prereq, {}) if progress else {}
                if prereq_progress.get('progress_percentage', 0) < 100:
                    prerequisites_met = False
                    break
            
            # Recommend based on completion status and prerequisites
            if completion_percentage < 100 and prerequisites_met:
                recommendations.append({
                    'module_id': module_id,
                    'title': module_data['title'],
                    'description': module_data['description'],
                    'difficulty': module_data['difficulty'],
                    'estimated_time': module_data['estimated_time'],
                    'progress_percentage': completion_percentage,
                    'priority': _calculate_recommendation_priority(module_data, completion_percentage, user)
                })
        
        # Sort by priority
        recommendations.sort(key=lambda x: x['priority'], reverse=True)
        
        # Limit to top 5 recommendations
        recommendations = recommendations[:5]
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
        
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get recommendations'
        }), 500

def _calculate_recommendation_priority(module_data, completion_percentage, user):
    """Calculate recommendation priority based on various factors."""
    priority = 0
    
    # Higher priority for partially completed modules
    if 0 < completion_percentage < 100:
        priority += 50
    
    # Priority based on user level and module difficulty
    user_level = user.get('level', 1)
    difficulty_map = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
    module_difficulty = difficulty_map.get(module_data['difficulty'], 1)
    
    if abs(user_level - module_difficulty) <= 1:
        priority += 30
    
    # Bonus for shorter modules (easier to complete)
    if module_data['estimated_time'] <= 30:
        priority += 10
    
    return priority

@learning_bp.route('/certificates', methods=['GET'])
def get_certificates():
    """Get user's learning certificates."""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        user_id = session['user_id']
        progress = get_user_learning_progress(user_id)
        
        certificates = []
        
        if progress:
            for module_id, module_progress in progress['modules'].items():
                if module_progress.get('progress_percentage', 0) >= 100:
                    module_data = LEARNING_CONTENT.get(module_id, {})
                    certificates.append({
                        'module_id': module_id,
                        'title': module_data.get('title', 'Unknown Module'),
                        'completion_date': module_progress.get('last_accessed'),
                        'certificate_id': f"ST_{user_id}_{module_id}_{int(time.time())}"
                    })
        
        return jsonify({
            'success': True,
            'certificates': certificates
        })
        
    except Exception as e:
        print(f"Error getting certificates: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get certificates'
        }), 500

@learning_bp.route('/progress/<module_id>', methods=['POST'])
def track_module_progress(module_id):
    """Track detailed user progress through a learning module"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_id = session['user_id']
        data = request.json
        
        scroll_percentage = data.get('scroll_percentage', 0)
        time_spent = data.get('time_spent', 0)
        sections_visited = data.get('sections_visited', [])
        videos_watched = data.get('videos_watched', {})
        
        module = LEARNING_CONTENT.get(module_id)
        if not module:
            return jsonify({'error': 'Module not found'}), 404
        
        estimated_time = module.get('estimated_time', 30) * 60
        min_time_required = estimated_time * 0.7
        
        criteria_met = {
            'scroll_depth': scroll_percentage >= 90,
            'time_spent': time_spent >= min_time_required,
            'sections_visited': len(sections_visited) >= len(module.get('sections', [])),
            'videos_watched': all(pct >= 50 for pct in videos_watched.values()) if videos_watched else True
        }
        
        is_complete = all(criteria_met.values())
        
        from app.models.user_model import get_db
        db = get_db()
        
        progress_data = {
            'user_id': user_id,
            'module_id': module_id,
            'scroll_percentage': scroll_percentage,
            'time_spent': time_spent,
            'sections_visited': sections_visited,
            'videos_watched': videos_watched,
            'criteria_met': criteria_met,
            'is_complete': is_complete,
            'last_updated': datetime.now()
        }
        
        db.learning_progress.update_one(
            {'user_id': user_id, 'module_id': module_id},
            {'$set': progress_data},
            upsert=True
        )
        
        total_criteria = len(criteria_met)
        met_criteria = sum(1 for met in criteria_met.values() if met)
        progress_percentage = int((met_criteria / total_criteria) * 100)
        
        return jsonify({
            'success': True,
            'is_complete': is_complete,
            'criteria_met': criteria_met,
            'progress_percentage': progress_percentage,
            'time_remaining': max(0, min_time_required - time_spent)
        })
        
    except Exception as e:
        logger.error(f'Error tracking module progress: {e}')
        return jsonify({'error': 'Failed to track progress'}), 500

@learning_bp.route('/progress/<module_id>', methods=['GET'])
def get_module_progress(module_id):
    """Get user's progress for a specific module"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_id = session['user_id']
        
        from app.models.user_model import get_db
        db = get_db()
        
        progress = db.learning_progress.find_one({
            'user_id': user_id,
            'module_id': module_id
        })
        
        if not progress:
            module = LEARNING_CONTENT.get(module_id, {})
            return jsonify({
                'module_id': module_id,
                'is_complete': False,
                'scroll_percentage': 0,
                'time_spent': 0,
                'sections_visited': [],
                'videos_watched': {},
                'criteria_met': {
                    'scroll_depth': False,
                    'time_spent': False,
                    'sections_visited': False,
                    'videos_watched': True
                },
                'progress_percentage': 0,
                'estimated_time': module.get('estimated_time', 30) * 60
            })
        
        progress['_id'] = str(progress['_id'])
        module = LEARNING_CONTENT.get(module_id, {})
        progress['estimated_time'] = module.get('estimated_time', 30) * 60
        
        return jsonify(progress)
        
    except Exception as e:
        logger.error(f'Error getting module progress: {e}')
        return jsonify({'error': 'Failed to get progress'}), 500


@learning_bp.route('/module/<module_id>/complete', methods=['POST'])
def mark_module_complete(module_id):
    """Mark a module as complete or incomplete"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_id = session['user_id']
        data = request.json
        completed = data.get('completed', True)
        
        # Validate module exists
        if module_id not in LEARNING_CONTENT:
            return jsonify({'error': 'Module not found'}), 404
        
        from app.models.user_model import get_db
        db = get_db()
        
        # Update or create progress record
        if completed:
            # Mark as 100% complete
            progress_data = {
                'user_id': user_id,
                'module_id': module_id,
                'scroll_percentage': 100,
                'time_spent': LEARNING_CONTENT[module_id].get('estimated_time', 30) * 60,
                'sections_visited': [s['id'] for s in LEARNING_CONTENT[module_id].get('sections', [])],
                'videos_watched': {},
                'criteria_met': {
                    'scroll_depth': True,
                    'time_spent': True,
                    'sections_visited': True,
                    'videos_watched': True
                },
                'is_complete': True,
                'manually_completed': True,
                'last_updated': datetime.now()
            }
        else:
            # Mark as incomplete
            progress_data = {
                'user_id': user_id,
                'module_id': module_id,
                'scroll_percentage': 0,
                'time_spent': 0,
                'sections_visited': [],
                'videos_watched': {},
                'criteria_met': {
                    'scroll_depth': False,
                    'time_spent': False,
                    'sections_visited': False,
                    'videos_watched': False
                },
                'is_complete': False,
                'manually_completed': False,
                'last_updated': datetime.now()
            }
        
        db.learning_progress.update_one(
            {'user_id': user_id, 'module_id': module_id},
            {'$set': progress_data},
            upsert=True
        )
        
        return jsonify({
            'success': True,
            'message': f'Module marked as {"complete" if completed else "incomplete"}',
            'is_complete': completed
        })
        
    except Exception as e:
        logger.error(f'Error marking module complete: {e}')
        return jsonify({'error': 'Failed to update completion status'}), 500


# Error handlers
@learning_bp.errorhandler(404)
def learning_not_found(error):
    return jsonify({
        'success': False,
        'error': 'Learning resource not found'
    }), 404

@learning_bp.errorhandler(500)
def learning_internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Learning system error'
    }), 500