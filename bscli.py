# -*- coding: utf-8 -*-
# ===================================================
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
import click
import urllib
import json
from blockchain.chain import Block, Blockchain
from PIL import Image, ImageDraw
import random
import base64
import io

# ==================================================
# ===== SUPPORTED COMMANDS LIST IN BLOCKSHELL ======
# ==================================================
SUPPORTED_COMMANDS = [
    'dotx',
    'adduser',
    'allblocks',
    'getblock',
    'help'
]

# Init blockchain
coin = Blockchain()

# Create group of commands
@click.group()
def cli():
    """
        Create a group of commands for CLI
    """
    pass

# ==================================================
# ============= BLOCKSHELL CLI COMMAND =============
# ==================================================
@cli.command()
@click.option("--difficulty", default=3, help="Define difficulty level of blockchain.")
def init(difficulty):
    """Initialize local blockchain"""
    print("""
  ____    _                  _       _____   _              _   _
 |  _ \  | |                | |     / ____| | |            | | | |
 | |_) | | |   ___     ___  | | __ | (___   | |__     ___  | | | |
 |  _ <  | |  / _ \   / __| | |/ /  \___ \  | '_ \   / _ \ | | | |
 | |_) | | | | (_) | | (__  |   <   ____) | | | | | |  __/ | | | |
 |____/  |_|  \___/   \___| |_|\_\ |_____/  |_| |_|  \___| |_| |_|

 > A command line utility for learning Blockchain concepts.
 > Type 'help' to see supported commands.
 > Project by Daxeel Soni - https://daxeel.github.io

    """)

    # Set difficulty of blockchain
    coin.difficulty = difficulty

    # Start blockshell shell
    while True:
        cmd = raw_input("[BlockShell] $ ")
        processInput(cmd)

# Process input from Blockshell shell
def processInput(cmd):
    """
        Method to process user input from Blockshell CLI.
    """
    userCmd = cmd.split(" ")[0]
    if len(cmd) > 0:
        if userCmd in SUPPORTED_COMMANDS:
            globals()[userCmd](cmd)
        else:
            # error
            msg = "Command not found. Try help command for documentation"
            throwError(msg)


# ==================================================
# =========== BLOCKSHELL COMMAND METHODS ===========
# ==================================================
def dotx(cmd):
    """
        Do Transaction - Method to perform new transaction on blockchain.
    """
    txData = cmd.split("dotx ")[-1]
    if "{" in txData:
        txData = json.loads(txData)
    print("Doing transaction...")
    coin.addBlock(Block(data=txData))

def generate_random_avatar():
    """
        Method to generate a random avatar image and encode it in base64
    """
    width, height = 200, 200
    image = Image.new('RGB', (width, height), color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    draw = ImageDraw.Draw(image)
    
    # Draw random shapes for variation
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.line([x1, y1, x2, y2], fill=color, width=2)
    
    # Draw a circle in the center
    center_x, center_y = width // 2, height // 2
    radius = 40
    draw.ellipse([center_x - radius, center_y - radius, center_x + radius, center_y + radius], 
                 fill=(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
    
    # Encode image to base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_base64

def adduser(cmd):
    """
        Method to add a new user to the blockchain with uid-epita, email-epita, nom, prenom and random avatar image
    """
    parts = cmd.split(" ")
    if len(parts) < 5:
        throwError("Usage: adduser <uid-epita> <email-epita> <nom> <prenom>")
        return
    
    uid_epita = parts[1]
    email_epita = parts[2]
    nom = parts[3]
    prenom = parts[4]
    
    # Generate random avatar
    avatar_base64 = generate_random_avatar()
    
    user_data = {
        "uid-epita": uid_epita,
        "email-epita": email_epita,
        "nom": nom,
        "prenom": prenom,
        "avatar": avatar_base64
    }
    
    print("Adding user to blockchain...")
    coin.addBlock(Block(data=user_data))
    print("User {} {} added successfully!".format(prenom, nom))

def allblocks(cmd):
    """
        Method to list all mined blocks.
    """
    print("")
    for eachBlock in coin.chain:
        print(eachBlock.hash)
    print("")

def getblock(cmd):
    """
        Method to fetch the details of block for given hash.
    """
    blockHash = cmd.split(" ")[-1]
    for eachBlock in coin.chain:
        if eachBlock.hash == blockHash:
            print("")
            print(eachBlock.__dict__)
            print("")

def help(cmd):
    """
        Method to display supported commands in Blockshell
    """
    print("Commands:")
    print("   adduser <uid> <email> <nom> <prenom>  Add a new user with random avatar")
    print("   dotx <transaction data>               Create new transaction")
    print("   allblocks                             Fetch all mined blocks in blockchain")
    print("   getblock <block hash>                 Fetch information about particular block")

def throwError(msg):
    """
        Method to throw an error from Blockshell.
    """
    print("Error : " + msg)
