from flask import Flask, request, jsonify, render_template_string
import g4f
import json

app = Flask(__name__)

# HTML frontend with a simple chat UI
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Poseidon's Claude Oracle</title>
    <style>
        body { background: #0a1a2a; color: #c0d0e0; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: auto; }
        h1 { color: #7fbfff; border-bottom: 2px solid #2a4a6a; padding-bottom: 10px; }
        .chat-box { height: 400px; overflow-y: auto; background: #0d1f2f; border: 1px solid #2a4a6a; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
        .msg { margin: 8px 0; }
        .user { color: #7fbfff; }
        .bot { color: #aad0ff; border-left: 2px solid #4a8aaa; padding-left: 10px; }
        .controls { display: flex; gap: 10px; flex-wrap: wrap; }
        select, input, button { padding: 8px 12px; border-radius: 6px; border: none; background: #1a2a3a; color: #c0d0e0; }
        button { background: #2a5a7a; cursor: pointer; }
        button:hover { background: #3a7a9a; }
        .model-select { flex: 1; min-width: 150px; }
        .input-area { display: flex; gap: 10px; margin-top: 10px; }
        #prompt { flex: 1; padding: 10px; background: #1a2a3a; color: #c0d0e0; border: 1px solid #2a4a6a; border-radius: 6px; }
    </style>
</head>
<body>
<div class="container">
    <h1>🌊 Poseidon's Claude Oracle</h1>
    <div class="chat-box" id="chatBox">
        <div class="msg bot">The tide is high. Ask what you will.</div>
    </div>
    <div class="controls">
        <select id="modelSelect" class="model-select">
            <option value="claude-3-opus">Claude 3 Opus</option>
            <option value="claude-3-sonnet">Claude 3 Sonnet</option>
            <option value="claude-3-haiku">Claude 3 Haiku</option>
            <option value="claude-3.5-sonnet">Claude 3.5 Sonnet</option>
            <option value="gpt-4">GPT-4 (fallback)</option>
        </select>
        <button id="clearBtn">Clear</button>
    </div>
    <div class="input-area">
        <input type="text" id="prompt" placeholder="Your question..." autofocus>
        <button id="sendBtn">Send</button>
    </div>
</div>
<script>
    const chatBox = document.getElementById('chatBox');
    const promptInput = document.getElementById('prompt');
    const sendBtn = document.getElementById('sendBtn');
    const clearBtn = document.getElementById('clearBtn');
    const modelSelect = document.getElementById('modelSelect');

    function appendMessage(text, cls) {
        const div = document.createElement('div');
        div.className = 'msg ' + cls;
        div.textContent = text;
        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendMessage() {
        const prompt = promptInput.value.trim();
        if (!prompt) return;
        appendMessage(prompt, 'user');
        promptInput.value = '';
        promptInput.disabled = true;
        sendBtn.disabled = true;

        const model = modelSelect.value;
        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt, model })
            });
            const data = await response.json();
            if (data.error) {
                appendMessage('Error: ' + data.error, 'bot');
            } else {
                appendMessage(data.response, 'bot');
            }
        } catch (e) {
            appendMessage('Network error: ' + e.message, 'bot');
        } finally {
            promptInput.disabled = false;
            sendBtn.disabled = false;
            promptInput.focus();
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    promptInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendMessage(); });
    clearBtn.addEventListener('click', () => {
        chatBox.innerHTML = '<div class="msg bot">The tide is high. Ask what you will.</div>';
    });
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    model = data.get('model', 'claude-3-opus')

    if not prompt:
        return jsonify({'error': 'Empty prompt'}), 400

    # Map model names to g4f model objects
    model_map = {
        'claude-3-opus': g4f.models.Claude3Opus,
        'claude-3-sonnet': g4f.models.Claude3Sonnet,
        'claude-3-haiku': g4f.models.Claude3Haiku,
        'claude-3.5-sonnet': g4f.models.Claude35Sonnet,
        'gpt-4': g4f.models.gpt_4,
    }
    g4f_model = model_map.get(model, g4f.models.Claude3Opus)

    try:
        # Use a working provider; you can change to g4f.Provider.Bing or others
        response = g4f.ChatCompletion.create(
            model=g4f_model,
            messages=[{"role": "user", "content": prompt}],
            provider=g4f.Provider.Bing,  # often works; fallback to default if issues
            stream=False
        )
        return jsonify({'response': response})
    except Exception as e:
        # Fallback: try without specifying provider (automatic)
        try:
            response = g4f.ChatCompletion.create(
                model=g4f_model,
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )
            return jsonify({'response': response})
        except Exception as e2:
            return jsonify({'error': str(e2)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
