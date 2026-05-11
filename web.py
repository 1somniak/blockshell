# -*- coding: utf-8 -*-
# ==================================================
# ==================== META DATA ===================
# ==================================================
__author__ = "Daxeel Soni"
__url__ = "https://daxeel.github.io"
__email__ = "daxeelsoni44@gmail.com"
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daxeel Soni"

# ==================================================
# ================= IMPORT MODULES =================
# ==================================================
try:
    from flask import Flask, render_template, jsonify
except Exception:
    class _DummyApp(object):
        def route(self, *a, **k):
            def deco(f):
                return f
            return deco
        def run(self, *a, **k):
            return None
    Flask = lambda name: _DummyApp()
    def render_template(*a, **k):
        return ''
    def jsonify(*a, **k):
        return ''
import json

# Init flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('guide.html')

@app.route('/allblocks')
def mined_blocks():
    """
        Endpoint to list all mined blocks.
    """
    try:
        with open("chain.txt", "r", encoding='utf-8') as f:
            data = json.loads(f.read())
    except Exception:
        data = []
    return render_template('blocks.html', data=data)

@app.route('/block/<hash>')
def block(hash):
    """
        Endpoint which shows all the data for given block hash.
    """
    try:
        with open("chain.txt", "r", encoding='utf-8') as f:
            data = json.loads(f.read())
    except Exception:
        data = []
    for eachBlock in data:
        if eachBlock['hash'] == hash:
            return render_template('blockdata.html', data=eachBlock)

# Run flask app
if __name__ == '__main__':
    app.run(debug=True)
