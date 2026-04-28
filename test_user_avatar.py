#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify user avatar generation and blockchain storage
"""

from blockchain.chain import Block, Blockchain
from PIL import Image, ImageDraw
import random
import base64
import io
import json

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

# Test avatar generation
print "[TEST] Generating random avatar..."
avatar = generate_random_avatar()
print "[TEST] Avatar generated! Size: {} bytes".format(len(avatar))
print "[TEST] Avatar starts with: {}...".format(avatar[:50])

# Test blockchain with user data
print "\n[TEST] Creating blockchain..."
blockchain = Blockchain()
blockchain.difficulty = 2

# Create user data
user_data = {
    "uid-epita": "daxeel.s",
    "email-epita": "daxeel.s@epita.fr",
    "nom": "Soni",
    "prenom": "Daxeel",
    "avatar": avatar
}

print "[TEST] Adding user block to blockchain..."
block = Block(data=user_data)
blockchain.addBlock(block)

print "[TEST] User block added successfully!"
print "[TEST] Block hash: {}".format(block.hash)

# Check the stored data
print "\n[TEST] Reading chain.txt..."
with open("chain.txt", "r") as f:
    chain_data = json.loads(f.read())

print "[TEST] Number of blocks: {}".format(len(chain_data))
print "[TEST] Last block contains user data:"
last_block = chain_data[-1]
print "  - UID: {}".format(last_block['data']['uid-epita'])
print "  - Email: {}".format(last_block['data']['email-epita'])
print "  - Name: {} {}".format(last_block['data']['prenom'], last_block['data']['nom'])
print "  - Avatar size: {} bytes".format(len(last_block['data']['avatar']))

print "\n[TEST] All tests passed!"
