"""
Security routes for handling CSP violations, suspicious activities, and security monitoring
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import json
import re
from app.models.security import SecurityIncident, CSPViolation
from app import db

security_bp = Blueprint('security', __name__, url_prefix='/security')

@security_bp.route('/csp-violation', methods=['POST'])
def handle_csp_violation():
    """Handle Content Security Policy violation reports"""
    try:
        data = request.get_json()
        
        # Log CSP violation
        violation = CSPViolation(
            directive=data.get('directive'),
            blocked_uri=data.get('blockedURI'),
            document_uri=data.get('documentURI'),
            user_agent=data.get('userAgent', request.headers.get('User-Agent')),
            timestamp=datetime.utcnow(),
            ip_address=request.remote_addr
        )
        
        db.session.add(violation)
        db.session.commit()
        
        # Log to application logs
        current_app.logger.warning(f"CSP Violation: {data.get('directive')} - {data.get('blockedURI')}")
        
        # Check if this is a serious violation that requires immediate attention
        if is_serious_csp_violation(data):
            current_app.logger.error(f"SERIOUS CSP VIOLATION: {data}")
            # Could trigger alerts here
        
        return jsonify({'status': 'recorded'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error handling CSP violation: {e}")
        return jsonify({'error': 'Failed to record violation'}), 500

@security_bp.route('/suspicious-activity', methods=['POST'])
def handle_suspicious_activity():
    """Handle reports of suspicious user activity"""
    try:
        data = request.get_json()
        
        # Create security incident record
        incident = SecurityIncident(
            incident_type=data.get('type'),
            details=json.dumps(data.get('details', {})),
            user_agent=data.get('userAgent', request.headers.get('User-Agent')),
            ip_address=request.remote_addr,
            url=data.get('url'),
            timestamp=datetime.utcnow(),
            severity=determine_severity(data.get('type'))
        )
        
        db.session.add(incident)
        db.session.commit()
        
        # Log based on severity
        severity = incident.severity
        if severity == 'high':
            current_app.logger.error(f"HIGH SEVERITY: {data.get('type')} - {data.get('details')}")
        elif severity == 'medium':
            current_app.logger.warning(f"MEDIUM SEVERITY: {data.get('type')} - {data.get('details')}")
        else:
            current_app.logger.info(f"LOW SEVERITY: {data.get('type')} - {data.get('details')}")
        
        # Check if immediate action is required
        if should_trigger_alert(data):
            trigger_security_alert(incident)
        
        return jsonify({'status': 'recorded', 'incident_id': incident.id}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error handling suspicious activity: {e}")
        return jsonify({'error': 'Failed to record incident'}), 500

@security_bp.route('/validate-input', methods=['POST'])
def validate_input():
    """Validate user input for security issues"""
    try:
        data = request.get_json()
        input_text = data.get('input', '')
        
        # Perform security validation
        validation_result = {
            'is_safe': True,
            'issues': [],
            'sanitized': input_text
        }
        
        # Check for XSS patterns
        xss_patterns = [
            r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',
            r'javascript:',
            r'on\w+\s*=',
            r'expression\s*\(',
            r'<iframe\b[^>]*>',
            r'<object\b[^>]*>',
            r'<embed\b[^>]*>'
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                validation_result['is_safe'] = False
                validation_result['issues'].append('Potential XSS detected')
                break
        
        # Check for SQL injection patterns
        sql_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)',
            r'(\b(UNION|OR|AND)\b.*\b(SELECT|INSERT|UPDATE|DELETE)\b)',
            r'[\'";].*(-{2}|\/\*)',
            r'\b(exec|execute|sp_)\w*\s*\('
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                validation_result['is_safe'] = False
                validation_result['issues'].append('Potential SQL injection detected')
                break
        
        # Check for command injection patterns
        cmd_patterns = [
            r'[;&|`$]',
            r'\b(cat|ls|pwd|whoami|id|ps|netstat|wget|curl)\b',
            r'(\.\.\/|\.\.\\)',
            r'\$\{.*\}',
            r'`.*`'
        ]
        
        for pattern in cmd_patterns:
            if re.search(pattern, input_text):
                validation_result['is_safe'] = False
                validation_result['issues'].append('Potential command injection detected')
                break
        
        # Sanitize input if issues found
        if not validation_result['is_safe']:
            validation_result['sanitized'] = sanitize_input(input_text)
        
        return jsonify(validation_result), 200
        
    except Exception as e:
        current_app.logger.error(f"Error validating input: {e}")
        return jsonify({'error': 'Validation failed'}), 500

@security_bp.route('/security-headers', methods=['GET'])
def get_security_headers():
    """Get recommended security headers for the application"""
    headers = {
        'Content-Security-Policy': generate_csp_policy(),
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'camera=(), microphone=(), geolocation=()'
    }
    
    return jsonify({'headers': headers}), 200

@security_bp.route('/security-report', methods=['GET'])
def get_security_report():
    """Get security incident summary report"""
    try:
        # Get recent incidents (last 24 hours)
        from datetime import datetime, timedelta
        since = datetime.utcnow() - timedelta(days=1)
        
        incidents = SecurityIncident.query.filter(
            SecurityIncident.timestamp >= since
        ).all()
        
        violations = CSPViolation.query.filter(
            CSPViolation.timestamp >= since
        ).all()
        
        # Summarize incidents by type
        incident_summary = {}
        for incident in incidents:
            incident_type = incident.incident_type
            if incident_type not in incident_summary:
                incident_summary[incident_type] = {
                    'count': 0,
                    'high_severity': 0,
                    'medium_severity': 0,
                    'low_severity': 0
                }
            
            incident_summary[incident_type]['count'] += 1
            incident_summary[incident_type][f"{incident.severity}_severity"] += 1
        
        # Summarize CSP violations
        violation_summary = {}
        for violation in violations:
            directive = violation.directive
            if directive not in violation_summary:
                violation_summary[directive] = 0
            violation_summary[directive] += 1
        
        report = {
            'period': '24 hours',
            'total_incidents': len(incidents),
            'total_violations': len(violations),
            'incident_breakdown': incident_summary,
            'violation_breakdown': violation_summary,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify(report), 200
        
    except Exception as e:
        current_app.logger.error(f"Error generating security report: {e}")
        return jsonify({'error': 'Failed to generate report'}), 500

# Helper functions

def is_serious_csp_violation(violation_data):
    """Determine if a CSP violation is serious and requires immediate attention"""
    serious_patterns = [
        'script-src',
        'unsafe-eval',
        'unsafe-inline',
        'data:',
        'blob:'
    ]
    
    blocked_uri = violation_data.get('blockedURI', '').lower()
    directive = violation_data.get('directive', '').lower()
    
    return any(pattern in blocked_uri or pattern in directive for pattern in serious_patterns)

def determine_severity(incident_type):
    """Determine the severity level of a security incident"""
    high_severity = [
        'sql_injection_attempt',
        'xss_attempt',
        'command_injection_attempt',
        'suspicious_file_access',
        'brute_force_attack'
    ]
    
    medium_severity = [
        'rapid_form_submission',
        'excessive_input',
        'suspicious_url_request',
        'failed_authentication'
    ]
    
    if incident_type in high_severity:
        return 'high'
    elif incident_type in medium_severity:
        return 'medium'
    else:
        return 'low'

def should_trigger_alert(incident_data):
    """Determine if an incident should trigger an immediate alert"""
    incident_type = incident_data.get('type')
    
    # Trigger alerts for high-severity incidents
    alert_triggers = [
        'sql_injection_attempt',
        'xss_attempt',
        'command_injection_attempt',
        'brute_force_attack'
    ]
    
    return incident_type in alert_triggers

def trigger_security_alert(incident):
    """Trigger a security alert for serious incidents"""
    # In a real application, this would send notifications to security team
    current_app.logger.critical(f"SECURITY ALERT: {incident.incident_type} - Incident ID: {incident.id}")
    
    # Could integrate with:
    # - Email alerts
    # - Slack notifications
    # - SIEM systems
    # - Incident response tools
    
    print(f"🚨 SECURITY ALERT: {incident.incident_type}")

def sanitize_input(input_text):
    """Sanitize potentially dangerous input"""
    # Remove script tags
    input_text = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', input_text, flags=re.IGNORECASE)
    
    # Remove javascript: URLs
    input_text = re.sub(r'javascript:', '', input_text, flags=re.IGNORECASE)
    
    # Remove event handlers
    input_text = re.sub(r'on\w+\s*=', '', input_text, flags=re.IGNORECASE)
    
    # Remove dangerous HTML tags
    dangerous_tags = ['iframe', 'object', 'embed', 'form', 'input', 'button']
    for tag in dangerous_tags:
        input_text = re.sub(f'<{tag}\\b[^>]*>', '', input_text, flags=re.IGNORECASE)
        input_text = re.sub(f'</{tag}>', '', input_text, flags=re.IGNORECASE)
    
    return input_text

def generate_csp_policy():
    """Generate a Content Security Policy for the application"""
    return (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https:; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "connect-src 'self' ws: wss:; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "object-src 'none'"
    )

# Error handlers
@security_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@security_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500