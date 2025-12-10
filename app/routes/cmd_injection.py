"""
Command Injection Challenge Implementation with Secure Sandbox Execution
"""
from flask import Blueprint, request, jsonify, session
from app.models.challenge_model import get_challenge_by_id, record_challenge_attempt
from app.models.user_model import get_user_by_id
from app.routes.ai_model import calculate_dynamic_score
import re
import time
import subprocess
import tempfile
import os
import shlex

cmd_injection_bp = Blueprint('cmd_injection', __name__)

# Simulated file system for safe command execution
SIMULATED_FILES = {
    '/etc/passwd': 'root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nwww-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\n',
    '/etc/shadow': 'root:$6$xyz$hashedpassword:18000:0:99999:7:::\ndaemon:*:18000:0:99999:7:::\nwww-data:*:18000:0:99999:7:::\n',
    '/home/user/secret.txt': 'This is a secret file containing sensitive information.\nAPI_KEY=sk-1234567890abcdef\nDB_PASSWORD=super_secret_password\n',
    '/var/www/config.php': '<?php\n$db_host = "localhost";\n$db_user = "web_user";\n$db_pass = "web_password_123";\n$db_name = "webapp_db";\n?>\n',
    '/proc/version': 'Linux version 5.4.0-74-generic (buildd@lcy01-amd64-029) (gcc version 9.4.0) #83-Ubuntu SMP\n'
}

SIMULATED_COMMANDS = {
    'ls': ['file1.txt', 'file2.txt', 'directory1/', 'secret_folder/'],
    'pwd': '/home/user',
    'whoami': 'www-data',
    'id': 'uid=33(www-data) gid=33(www-data) groups=33(www-data)',
    'uname': 'Linux',
    'ps': 'PID TTY TIME CMD\n1234 pts/0 00:00:01 bash\n5678 pts/0 00:00:00 python\n',
    'env': 'PATH=/usr/local/bin:/usr/bin:/bin\nHOME=/var/www\nUSER=www-data\n',
    'cat /etc/passwd': SIMULATED_FILES['/etc/passwd'],
    'cat /etc/shadow': 'cat: /etc/shadow: Permission denied',
    'cat /home/user/secret.txt': SIMULATED_FILES['/home/user/secret.txt'],
    'netstat': 'tcp 0 0 0.0.0.0:80 0.0.0.0:* LISTEN\ntcp 0 0 0.0.0.0:443 0.0.0.0:* LISTEN\n'
}

# Command injection demo templates
CMD_INJECTION_DEMOS = {
    'ping_utility': '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vulnerable Ping Utility</title>
        <style>
            .demo-container { max-width: 700px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; }
            .terminal { background: #000; color: #00ff00; padding: 15px; border-radius: 5px; font-family: monospace; }
            .terminal-input { background: transparent; border: none; color: #00ff00; font-family: monospace; outline: none; width: 80%; }
            .terminal-output { margin: 10px 0; white-space: pre-wrap; }
            .warning { background: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; color: #856404; }
            .input-section { margin: 15px 0; }
            .input-section button { padding: 8px 15px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="demo-container">
            <h3>Vulnerable Network Ping Utility</h3>
            <div class="warning">
                ⚠️ This utility is vulnerable to command injection. Commands are executed directly without validation.
            </div>
            <div class="terminal">
                <div class="terminal-output" id="output">Network Ping Utility v1.0
Ready to ping hosts...
                </div>
                <div>
                    <span style="color: #ffff00;">$ ping </span>
                    <input type="text" id="host-input" class="terminal-input" placeholder="Enter IP address or hostname..." />
                    <button onclick="executePing()">Execute</button>
                </div>
            </div>
            <div class="warning">
                Try: 127.0.0.1; ls or 127.0.0.1 && whoami or 127.0.0.1 | cat /etc/passwd
            </div>
        </div>
        <script>
            function executePing() {
                const input = document.getElementById('host-input');
                const output = document.getElementById('output');
                const command = input.value.trim();
                
                if (!command) {
                    output.textContent += '\\nError: No host specified\\n';
                    return;
                }
                
                output.textContent += '\\n$ ping ' + command + '\\n';
                
                // Simulate command injection vulnerability
                const result = simulateCommandExecution(command);
                output.textContent += result + '\\n';
                
                input.value = '';
                output.scrollTop = output.scrollHeight;
            }
            
            function simulateCommandExecution(input) {
                // Split on common command separators
                const separators = [';', '&&', '||', '|', '&'];
                let commands = [input];
                
                for (const sep of separators) {
                    if (input.includes(sep)) {
                        commands = input.split(sep);
                        break;
                    }
                }
                
                let result = '';
                for (const cmd of commands) {
                    const trimmedCmd = cmd.trim();
                    
                    if (trimmedCmd.startsWith('ping ') || /^\\d+\\.\\d+\\.\\d+\\.\\d+$/.test(trimmedCmd)) {
                        result += 'PING ' + trimmedCmd + ': 64 bytes from ' + trimmedCmd + ': icmp_seq=1 ttl=64 time=0.5ms\\n';
                    } else if (trimmedCmd === 'ls') {
                        result += 'config.txt  logs/  scripts/  data/\\n';
                    } else if (trimmedCmd === 'whoami') {
                        result += 'www-data\\n';
                    } else if (trimmedCmd === 'pwd') {
                        result += '/var/www/ping-utility\\n';
                    } else if (trimmedCmd.includes('cat /etc/passwd')) {
                        result += 'root:x:0:0:root:/root:/bin/bash\\nwww-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\\n';
                    } else if (trimmedCmd === 'id') {
                        result += 'uid=33(www-data) gid=33(www-data) groups=33(www-data)\\n';
                    } else if (trimmedCmd.includes('cat')) {
                        result += 'cat: ' + trimmedCmd.split(' ')[1] + ': Permission denied\\n';
                    } else if (trimmedCmd) {
                        result += 'bash: ' + trimmedCmd + ': command not found\\n';
                    }
                }
                
                return result || 'Command executed successfully';
            }
            
            // Allow Enter key to execute
            document.getElementById('host-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    executePing();
                }
            });
        </script>
    </body>
    </html>
    ''',
    
    'file_manager': '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vulnerable File Manager</title>
        <style>
            .demo-container { max-width: 700px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; }
            .file-manager { background: #f8f9fa; padding: 15px; border-radius: 5px; }
            .command-section { margin: 15px 0; }
            .command-section input { width: 70%; padding: 8px; margin-right: 10px; font-family: monospace; }
            .command-section button { padding: 8px 15px; background: #28a745; color: white; border: none; border-radius: 3px; cursor: pointer; }
            .output { background: #000; color: #ffffff; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; max-height: 300px; overflow-y: auto; }
            .warning { background: #f8d7da; padding: 10px; border-radius: 5px; margin: 10px 0; color: #721c24; }
        </style>
    </head>
    <body>
        <div class="demo-container">
            <h3>Vulnerable File Manager</h3>
            <div class="warning">
                ⚠️ This file manager executes system commands directly. Input is not sanitized.
            </div>
            <div class="file-manager">
                <h4>Current Directory: /var/www/files</h4>
                <div class="command-section">
                    <input type="text" id="file-input" placeholder="Enter filename or command..." />
                    <button onclick="processFile()">List/Process File</button>
                </div>
                <div class="output" id="file-output">File Manager v2.1
Type a filename to list or process...
                </div>
            </div>
            <div class="warning">
                Try: file.txt; cat /etc/passwd or ../../../etc/passwd or file.txt && whoami
            </div>
        </div>
        <script>
            function processFile() {
                const input = document.getElementById('file-input');
                const output = document.getElementById('file-output');
                const filename = input.value.trim();
                
                if (!filename) {
                    output.textContent += '\\nError: No filename specified\\n';
                    return;
                }
                
                output.textContent += '\\n> Processing: ' + filename + '\\n';
                
                // Simulate vulnerable file processing
                const result = simulateFileProcessing(filename);
                output.textContent += result + '\\n';
                
                input.value = '';
                output.scrollTop = output.scrollHeight;
            }
            
            function simulateFileProcessing(input) {
                // Check for command injection attempts
                if (input.includes(';') || input.includes('&&') || input.includes('||')) {
                    const parts = input.split(/[;&|]+/);
                    let result = '';
                    
                    for (const part of parts) {
                        const cmd = part.trim();
                        if (cmd.includes('cat /etc/passwd')) {
                            result += 'root:x:0:0:root:/root:/bin/bash\\nwww-data:x:33:33:www-data:/var/www:/bin/sh\\n';
                        } else if (cmd === 'whoami') {
                            result += 'www-data\\n';
                        } else if (cmd === 'ls') {
                            result += 'document1.txt  image.jpg  config.ini  backup/\\n';
                        } else if (cmd === 'pwd') {
                            result += '/var/www/files\\n';
                        } else if (cmd.includes('cat ')) {
                            const file = cmd.replace('cat ', '');
                            result += 'Contents of ' + file + ':\\nSample file content here...\\n';
                        } else if (cmd.length > 0) {
                            result += 'Processing file: ' + cmd + '\\nFile size: 1024 bytes\\nLast modified: 2024-01-15\\n';
                        }
                    }
                    return result;
                } else {
                    // Normal file processing
                    if (input.includes('../')) {
                        return 'Error: Path traversal detected\\nAccess denied for security reasons';
                    }
                    return 'File: ' + input + '\\nType: Regular file\\nSize: 2048 bytes\\nPermissions: -rw-r--r--';
                }
            }
            
            // Allow Enter key
            document.getElementById('file-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    processFile();
                }
            });
        </script>
    </body>
    </html>
    '''
}


@cmd_injection_bp.route('/demo/<demo_type>', methods=['GET'])
def get_command_injection_demo(demo_type):
    """Get interactive command injection demonstration."""
    try:
        if demo_type not in CMD_INJECTION_DEMOS:
            return jsonify({
                'success': False,
                'error': 'Demo type not found'
            }), 404
        
        demo_html = CMD_INJECTION_DEMOS[demo_type]
        
        return jsonify({
            'success': True,
            'demo_type': demo_type,
            'demo_html': demo_html,
            'description': get_cmd_demo_description(demo_type)
        }), 200
        
    except Exception as e:
        print(f"Error getting command injection demo: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to load demo'
        }), 500


@cmd_injection_bp.route('/sandbox/execute', methods=['POST'])
def execute_command_safely():
    """Execute command in a secure sandbox environment."""
    try:
        data = request.json
        command = data.get('command', '')
        challenge_id = data.get('challenge_id')
        user_id = data.get('user_id')
        
        if not command or not challenge_id or not user_id:
            return jsonify({
                'success': False,
                'error': 'Missing required parameters'
            }), 400
        
        # Get challenge and user
        challenge = get_challenge_by_id(challenge_id)
        user = get_user_by_id(user_id)
        
        if not challenge or not user:
            return jsonify({
                'success': False,
                'error': 'Challenge or user not found'
            }), 404
        
        # Execute command in sandbox
        execution_result = execute_in_sandbox(command)
        
        # Validate command injection
        validation_result = validate_command_injection(command, challenge)
        
        # Calculate score
        completion_time = time.time() - session.get(f'challenge_{challenge_id}_start_time', time.time())
        hints_used = session.get(f'challenge_{challenge_id}_hints_used', 0)
        
        score_earned = 0
        if validation_result['is_valid']:
            score_earned = calculate_dynamic_score(
                user, challenge, completion_time, hints_used, 1
            )
        
        # Record the attempt
        record_challenge_attempt(
            user_id, challenge_id, command,
            validation_result['is_valid'], completion_time, hints_used
        )
        
        return jsonify({
            'success': True,
            'execution_result': execution_result,
            'validation_result': validation_result,
            'score_earned': score_earned
        }), 200
        
    except Exception as e:
        print(f"Error executing command safely: {e}")
        return jsonify({
            'success': False,
            'error': 'Execution failed'
        }), 500


@cmd_injection_bp.route('/challenges', methods=['GET'])
def get_command_injection_challenges():
    """Get available command injection challenges."""
    try:
        from app.models.challenge_model import get_command_injection_challenges as get_challenges
        
        challenges = get_challenges()
        
        # Add demo links to challenges
        for challenge in challenges:
            challenge['demo_available'] = challenge.get('interactive_demo', False)
            if challenge['demo_available']:
                demo_type = get_cmd_demo_type_for_challenge(challenge)
                challenge['demo_url'] = f"/api/cmd-injection/demo/{demo_type}"
        
        return jsonify({
            'success': True,
            'challenges': challenges
        }), 200
        
    except Exception as e:
        print(f"Error getting command injection challenges: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get challenges'
        }), 500


def execute_in_sandbox(command):
    """Execute command in a simulated safe sandbox."""
    result = {
        'output': '',
        'error': '',
        'exit_code': 0,
        'execution_time': 0,
        'commands_detected': []
    }
    
    start_time = time.time()
    
    try:
        # Detect command injection patterns
        injection_patterns = [
            (r';', 'Semicolon separator'),
            (r'&&', 'AND operator'),
            (r'\|\|', 'OR operator'),
            (r'\|', 'Pipe operator'),
            (r'&', 'Background operator'),
            (r'`.*?`', 'Command substitution (backticks)'),
            (r'\$\(.*?\)', 'Command substitution $()'),
            (r'>', 'Output redirection'),
            (r'<', 'Input redirection')
        ]
        
        detected_commands = []
        for pattern, description in injection_patterns:
            if re.search(pattern, command):
                detected_commands.append(description)
        
        result['commands_detected'] = detected_commands
        
        # Parse and simulate command execution
        output = simulate_command_execution(command)
        result['output'] = output
        
    except Exception as e:
        result['error'] = str(e)
        result['exit_code'] = 1
    
    result['execution_time'] = time.time() - start_time
    return result


def simulate_command_execution(command):
    """Simulate command execution in a controlled environment."""
    output = []
    
    # Split command on common separators
    separators = [';', '&&', '||']
    commands = [command]
    
    for sep in separators:
        if sep in command:
            commands = command.split(sep)
            break
    
    # Handle pipe operations
    if '|' in command and '||' not in command:
        commands = command.split('|')
        pipe_mode = True
    else:
        pipe_mode = False
    
    for i, cmd in enumerate(commands):
        cmd = cmd.strip()
        
        if not cmd:
            continue
        
        # Handle basic commands
        cmd_lower = cmd.lower()
        
        if cmd_lower in SIMULATED_COMMANDS:
            output.append(SIMULATED_COMMANDS[cmd_lower])
        elif cmd_lower.startswith('cat '):
            file_path = cmd[4:].strip()
            if file_path in SIMULATED_FILES:
                output.append(SIMULATED_FILES[file_path])
            else:
                output.append(f"cat: {file_path}: No such file or directory")
        elif cmd_lower.startswith('ls'):
            if len(cmd.split()) > 1:
                path = cmd.split()[1]
                output.append(f"ls: {path}: No such file or directory")
            else:
                output.append("\\n".join(SIMULATED_COMMANDS['ls']))
        elif cmd_lower.startswith('ping '):
            host = cmd[5:].strip()
            output.append(f"PING {host}: 64 bytes from {host}: icmp_seq=1 ttl=64 time=1ms")
        elif 'rm ' in cmd_lower:
            output.append("rm: Operation not permitted (sandbox restriction)")
        elif 'sudo' in cmd_lower:
            output.append("sudo: command not found")
        elif cmd_lower.startswith('nc ') or cmd_lower.startswith('netcat '):
            output.append("nc: command not found (security restriction)")
        elif 'chmod' in cmd_lower or 'chown' in cmd_lower:
            output.append("Operation not permitted (sandbox restriction)")
        else:
            output.append(f"bash: {cmd}: command not found")
    
    return "\\n".join(output)


def validate_command_injection(command, challenge):
    """Validate command injection payload."""
    validation_result = {
        'is_valid': False,
        'feedback': '',
        'injection_type': '',
        'risk_level': 'low'
    }
    
    # Check for command injection patterns
    injection_patterns = [
        (r';.*\w+', 'Command chaining with semicolon', 'high'),
        (r'&&.*\w+', 'Command chaining with AND', 'high'),
        (r'\|\|.*\w+', 'Command chaining with OR', 'medium'),
        (r'\|.*\w+', 'Command piping', 'medium'),
        (r'`.*\w+.*`', 'Command substitution with backticks', 'high'),
        (r'\$\(.*\w+.*\)', 'Command substitution with $()', 'high'),
        (r'&.*\w+', 'Background execution', 'medium')
    ]
    
    detected_injections = []
    max_risk = 'low'
    
    for pattern, injection_type, risk in injection_patterns:
        if re.search(pattern, command):
            detected_injections.append({
                'type': injection_type,
                'risk_level': risk
            })
            if risk == 'high':
                max_risk = 'high'
            elif risk == 'medium' and max_risk != 'high':
                max_risk = 'medium'
    
    validation_result['risk_level'] = max_risk
    
    # Check against expected solutions
    expected_solutions = challenge.get('expected_solutions', [])
    
    if detected_injections:
        for expected in expected_solutions:
            if expected.lower() in command.lower():
                validation_result['is_valid'] = True
                validation_result['feedback'] = f"Correct! Detected command injection: {detected_injections[0]['type']}"
                validation_result['injection_type'] = detected_injections[0]['type']
                break
        
        if not validation_result['is_valid']:
            validation_result['is_valid'] = True
            validation_result['feedback'] = f"Good! Detected command injection techniques: {', '.join([i['type'] for i in detected_injections])}"
            validation_result['injection_type'] = detected_injections[0]['type']
    
    if not validation_result['is_valid']:
        validation_result['feedback'] = "No command injection detected. Try using command separators like ; && || or |"
    
    return validation_result


def get_cmd_demo_description(demo_type):
    """Get description for command injection demo type."""
    descriptions = {
        'ping_utility': 'Demonstrates command injection in a network ping utility where user input is passed directly to system commands.',
        'file_manager': 'Shows command injection vulnerability in a file processing system that executes system commands.'
    }
    return descriptions.get(demo_type, 'Command injection demonstration')


def get_cmd_demo_type_for_challenge(challenge):
    """Map challenge to appropriate demo type."""
    challenge_id = challenge.get('id', '').lower()
    
    if 'ping' in challenge_id or 'network' in challenge_id:
        return 'ping_utility'
    elif 'file' in challenge_id or 'upload' in challenge_id:
        return 'file_manager'
    else:
        return 'ping_utility'