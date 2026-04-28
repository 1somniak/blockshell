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
from flask import Flask, render_template, jsonify
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
        with open("chain.txt", "r") as f:
            data = json.loads(f.read())
    except:
        data = []
    return render_template('blocks.html', data=data)

@app.route('/block/<hash>')
def block(hash):
    """
        Endpoint which shows all the data for given block hash.
    """
    try:
        with open("chain.txt", "r") as f:
            data = json.loads(f.read())
    except:
        data = []
    
    for eachBlock in data:
        if eachBlock['hash'] == hash:
            return render_template('blockdata.html', data=eachBlock)
    
    return "Block not found", 404

# Run flask app
if __name__ == '__main__':
    app.run(debug=True)
