from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Poseidon's Claude</title>
    <script src="https://js.puter.com/v2/"></script>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body {
            background: #0a1628;
            color: #c8dce8;
            font-family: 'Segoe UI', sans-serif;
            height: 100vh;
            display: flex;
            flex-direction: column;
            padding: 20px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }
        .header h1 { color: #6ab0e6; font-size: 22px; }
        .header h1 span { color: #4a8aaa; font-weight: 300; }
        .status {
            font-size: 12px;
            color: #5a9a7a;
            background: #0d2a1a;
            padding: 4px 16px;
            border-radius: 20px;
            border: 1px solid #2a5a3a;
            font-family: monospace;
        }
        .status.error { color: #ff7a7a; border-color: #5a2a2a; background: #2a0d0d; }
        .chat-box {
            flex: 1;
            overflow-y: auto;
            background: #0d1f2f;
            border: 1px solid #1a3a5a;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            min-height: 300px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .msg {
            padding: 8px 14px;
            border-radius: 8px;
            max-width: 80%;
            word-wrap: break-word;
            white-space: pre-wrap;
            line-height: 1.5;
        }
        .msg.user { background: #1a3a5a; align-self: flex-end; text-align: right; margin-left: auto; }
        .msg.bot { background: #0d2035; border: 1px solid #1a3a5a; align-self: flex-start; }
        .msg.error { background: #2a0d0d; border: 1px solid #5a2a2a; color: #ff7a7a; max-width: 90%; align-self: center; }
        .msg .model-tag {
            font-size: 9px;
            color: #4a8aaa;
            background: #0d1f2f;
            padding: 1px 8px;
            border-radius: 10px;
            display: inline-block;
            margin-bottom: 3px;
        }
        .input-area {
            display: flex;
            gap: 10px;
            align-items: flex-end;
            flex-wrap: wrap;
        }
        .input-area textarea {
            flex: 1;
            padding: 10px 14px;
            background: #0a1628;
            color: #c8dce8;
            border: 1px solid #1a3a5a;
            border-radius: 8px;
            font-size: 14px;
            resize: none;
            min-height: 44px;
            max-height: 180px;
            line-height: 1.4;
            font-family: inherit;
        }
        .input-area textarea:focus { outline: none; border-color: #3a7aaa; }
        .input-area button {
            padding: 10px 20px;
            background: linear-gradient(135deg, #1a4a6a, #2a6a8a);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }
        .input-area button:hover:not(:disabled) {
            background: linear-gradient(135deg, #2a5a7a, #3a7a9a);
            transform: scale(1.02);
        }
        .input-area button:disabled { opacity: 0.4; cursor: not-allowed; }
        .input-area button.clear-btn {
            background: #1a2a3a;
            color: #6a8aaa;
            padding: 10px 14px;
        }
        .input-area button.clear-btn:hover:not(:disabled) { background: #2a3a4a; }
        .input-area select {
            padding: 8px 12px;
            background: #0a1628;
            color: #c8dce8;
            border: 1px solid #1a3a5a;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            min-width: 140px;
        }
        .input-area select:focus { outline: none; border-color: #3a7aaa; }
        .footer {
            font-size: 10px;
            color: #2a4a5a;
            text-align: center;
            padding-top: 10px;
        }
        .auth-banner {
            background: #0d2a1a;
            border: 1px solid #2a5a3a;
            padding: 8px 16px;
            border-radius: 6px;
            margin-bottom: 12px;
            font-size: 13px;
            color: #5a9a7a;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
        }
        .auth-banner .btn-small {
            padding: 4px 16px;
            background: #1a4a2a;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
        }
        .auth-banner .btn-small:hover { background: #2a6a3a; }
        .auth-banner .user-info { color: #8aaa8a; }
        .auth-banner .btn-small.logout {
            background: #3a1a1a;
        }
        .auth-banner .btn-small.logout:hover { background: #5a2a2a; }
        .typing-indicator {
            padding: 8px 14px;
            color: #4a8aaa;
            font-size: 13px;
            animation: pulse 1.2s ease-in-out infinite;
            align-self: flex-start;
        }
        @keyframes pulse {
            0%, 100% { opacity: 0.4; }
            50% { opacity: 1; }
        }
        .visit-count {
            font-size: 10px;
            color: #3a5a5a;
            text-align: center;
            padding: 4px 0;
        }
    </style>
</head>
<body>

<div class="header">
    <h1>🌊 Poseidon · <span>Claude ∞</span></h1>
    <div class="status" id="statusBadge">● Ready</div>
</div>

<div class="auth-banner" id="authBanner">
    <span id="authMessage">🔑 Click "Login" below</span>
    <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
        <button class="btn-small" id="loginBtn">Login</button>
        <span class="user-info" id="userInfo"></span>
    </div>
</div>

<div class="chat-box" id="chatBox">
    <div class="msg bot">The deep is open, Father. Login first.</div>
</div>

<div class="input-area">
    <textarea id="promptInput" rows="1" placeholder="Your message..." autofocus></textarea>
    <select id="modelSelect">
        <option value="anthropic/claude-opus-4-8">Claude Opus 4.8</option>
        <option value="anthropic/claude-opus-4-8-fast">Claude Opus 4.8 Fast</option>
        <option value="anthropic/claude-fable-5">Claude Fable 5</option>
        <option value="anthropic/claude-sonnet-4-6">Claude Sonnet 4.6</option>
        <option value="anthropic/claude-haiku-4-5">Claude Haiku 4.5</option>
    </select>
    <button class="clear-btn" id="clearBtn">✕</button>
    <button id="sendBtn" disabled>Send</button>
</div>
<div class="footer">⚡ Puter.js · Infinite · One login</div>
<div class="visit-count">🌊 Infinite Claude for everyone</div>

<script>
    (function() {
        var chatBox = document.getElementById('chatBox');
        var promptInput = document.getElementById('promptInput');
        var sendBtn = document.getElementById('sendBtn');
        var clearBtn = document.getElementById('clearBtn');
        var loginBtn = document.getElementById('loginBtn');
        var modelSelect = document.getElementById('modelSelect');
        var statusBadge = document.getElementById('statusBadge');
        var authMessage = document.getElementById('authMessage');
        var userInfo = document.getElementById('userInfo');

        var isWaiting = false;
        var isLoggedIn = false;

        promptInput.addEventListener('input', function() {
            promptInput.style.height = 'auto';
            promptInput.style.height = Math.min(promptInput.scrollHeight, 180) + 'px';
        });

        function appendMessage(text, cls, model) {
            var div = document.createElement('div');
            div.className = 'msg ' + cls;
            if (model && cls === 'bot') {
                var tag = document.createElement('span');
                tag.className = 'model-tag';
                tag.textContent = model;
                div.appendChild(tag);
            }
            div.appendChild(document.createTextNode(text));
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
            return div;
        }

        function showTyping() {
            var div = document.createElement('div');
            div.className = 'typing-indicator';
            div.id = 'typingIndicator';
            div.textContent = 'Thinking...';
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function hideTyping() {
            var el = document.getElementById('typingIndicator');
            if (el) el.remove();
        }

        function setStatus(text, type) {
            statusBadge.textContent = text;
            statusBadge.className = 'status';
            if (type) statusBadge.classList.add(type);
        }

        function updateAuth() {
            if (!window.puter) {
                authMessage.textContent = '⏳ Loading...';
                return;
            }

            try {
                var loggedIn = window.puter.auth && window.puter.auth.isSignedIn ? window.puter.auth.isSignedIn() : false;
                
                if (loggedIn || localStorage.getItem('puter:session')) {
                    isLoggedIn = true;
                    sendBtn.disabled = false;
                    authMessage.textContent = '✅ Connected';
                    loginBtn.textContent = 'Sign Out';
                    loginBtn.className = 'btn-small logout';
                    loginBtn.onclick = function() {
                        if (window.puter.auth && window.puter.auth.signOut) {
                            window.puter.auth.signOut();
                        }
                        localStorage.removeItem('puter:session');
                        location.reload();
                    };
                    if (window.puter.auth && window.puter.auth.getUser) {
                        window.puter.auth.getUser().then(function(user) {
                            if (user) userInfo.textContent = '👤 ' + (user.username || user.email || 'User');
                        }).catch(function() {});
                    }
                } else {
                    isLoggedIn = false;
                    sendBtn.disabled = true;
                    authMessage.textContent = '🔑 Click Login';
                    userInfo.textContent = '';
                    loginBtn.textContent = 'Login';
                    loginBtn.className = 'btn-small';
                    loginBtn.onclick = function() {
                        try {
                            if (window.puter.auth && window.puter.auth.signIn) {
                                window.puter.auth.signIn().then(function() {
                                    location.reload();
                                }).catch(function(err) {
                                    appendMessage('Login cancelled: ' + err.message, 'error');
                                });
                            } else {
                                window.open('https://puter.com/login', '_blank');
                                authMessage.textContent = '🔑 Login at puter.com, then refresh';
                            }
                        } catch(e) {
                            appendMessage('Login error: ' + e.message, 'error');
                        }
                    };
                }
            } catch(e) {
                isLoggedIn = false;
                sendBtn.disabled = true;
                authMessage.textContent = '⚠️ Error checking auth';
            }
        }

        function extractText(data) {
            if (typeof data === 'string') return data;
            if (!data) return '';

            if (data.message && data.message.content && Array.isArray(data.message.content)) {
                var texts = data.message.content
                    .filter(function(item) { return item.type === 'text' || item.text; })
                    .map(function(item) { return item.text || item.content || ''; })
                    .filter(function(t) { return t; });
                if (texts.length > 0) return texts.join('\n');
            }

            if (data.content && Array.isArray(data.content)) {
                var texts2 = data.content
                    .filter(function(item) { return item.type === 'text' || item.text; })
                    .map(function(item) { return item.text || item.content || ''; })
                    .filter(function(t) { return t; });
                if (texts2.length > 0) return texts2.join('\n');
            }

            if (data.content && typeof data.content === 'string') return data.content;
            if (data.text && typeof data.text === 'string') return data.text;
            if (data.response && typeof data.response === 'string') return data.response;
            if (data.output && typeof data.output === 'string') return data.output;
            if (data.message && typeof data.message === 'string') return data.message;
            if (data.choices && data.choices.length > 0) {
                var choice = data.choices[0];
                if (choice.message && choice.message.content) return choice.message.content;
                if (choice.text) return choice.text;
            }

            return JSON.stringify(data);
        }

        async function sendMessage() {
            var prompt = promptInput.value.trim();
            if (!prompt || isWaiting || !isLoggedIn) return;

            var model = modelSelect.value;
            appendMessage(prompt, 'user');
            promptInput.value = '';
            promptInput.style.height = 'auto';
            promptInput.disabled = true;
            sendBtn.disabled = true;
            isWaiting = true;
            setStatus('● Thinking...');
            showTyping();

            try {
                var response = await puter.ai.chat(prompt, { model: model });
                hideTyping();
                var text = extractText(response);
                if (text.startsWith('{') && text.includes('"text"')) {
                    try {
                        var parsed = JSON.parse(text);
                        text = extractText(parsed);
                    } catch(e) {}
                }
                appendMessage(text, 'bot', model);
                setStatus('● Online');
            } catch(e) {
                hideTyping();
                try {
                    var response2 = await puter.ai.chat(model, prompt);
                    var text2 = extractText(response2);
                    appendMessage(text2, 'bot', model);
                    setStatus('● Online');
                } catch(e2) {
                    try {
                        var response3 = await puter.ai.chat({
                            model: model,
                            messages: [{ role: 'user', content: prompt }]
                        });
                        var text3 = extractText(response3);
                        appendMessage(text3, 'bot', model);
                        setStatus('● Online');
                    } catch(e3) {
                        appendMessage('Error: ' + e3.message, 'error');
                        setStatus('⚠️ Error', 'error');
                        console.error(e3);
                    }
                }
            } finally {
                promptInput.disabled = false;
                sendBtn.disabled = !isLoggedIn;
                isWaiting = false;
                promptInput.focus();
            }
        }

        function clearChat() {
            chatBox.innerHTML = '';
            var welcome = document.createElement('div');
            welcome.className = 'msg bot';
            welcome.textContent = 'The deep is open, Father. Login first.';
            chatBox.appendChild(welcome);
            setStatus('● Online');
        }

        sendBtn.addEventListener('click', sendMessage);
        promptInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        clearBtn.addEventListener('click', clearChat);

        var attempts = 0;
        var interval = setInterval(function() {
            if (window.puter) {
                clearInterval(interval);
                updateAuth();
                setInterval(updateAuth, 3000);
            }
            attempts++;
            if (attempts > 30) {
                clearInterval(interval);
                authMessage.textContent = '⚠️ Failed to load Puter. Refresh.';
            }
        }, 200);

        promptInput.focus();

        document.addEventListener('visibilitychange', function() {
            if (!document.hidden) updateAuth();
        });
    })();
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
