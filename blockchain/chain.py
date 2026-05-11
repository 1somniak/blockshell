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
import hashlib
import datetime
import json
try:
    from colorama import Fore, Back, Style
except Exception:
    Fore = Back = Style = ''
import time
import sys
import os

# ==================================================
# =================== BLOCK CLASS ==================
# ==================================================
class Block:
    """
        Create a new block in chain with metadata
    """
    def __init__(self, data, index=0):
        self.index = index
        self.previousHash = ""
        self.data = data
        self.timestamp = str(datetime.datetime.now())
        self.nonce = 0
        self.hash = self.calculateHash()

    def calculateHash(self):
        """
            Method to calculate hash from metadata
        """
        hashData = str(self.index) + str(self.data) + self.timestamp + self.previousHash + str(self.nonce)
        if isinstance(hashData, str):
            hashData = hashData.encode('utf-8')
        return hashlib.sha256(hashData).hexdigest()

    def mineBlock(self, difficulty):
        """
            Method for Proof of Work
        """
        print(Back.RED + "\n[Status] Mining block (" + str(self.index) + ") with PoW ...")
        startTime = time.time()

        while self.hash[:difficulty] != "0"*difficulty:
            self.nonce += 1
            self.hash = self.calculateHash()

        endTime = time.time()
        print(Back.BLUE + "[ Info ] Time Elapsed : " + str(endTime - startTime) + " seconds.")
        print(Back.BLUE + "[ Info ] Mined Hash : " + self.hash)
        print(Style.RESET_ALL)

# ==================================================
# ================ BLOCKCHAIN CLASS ================
# ==================================================
class Blockchain:
    """
        Initialize blockchain
    """
    def __init__(self):
        self.chain = [self.createGenesisBlock()]
        self.difficulty = 3

    def createGenesisBlock(self):
        """
            Method create genesis block
        """
        return Block("Genesis Block")

    def addBlock(self, newBlock):
        """
            Method to add new block from Block class
        """
        newBlock.index = len(self.chain)
        newBlock.previousHash = self.chain[-1].hash
        newBlock.mineBlock(self.difficulty)
        self.chain.append(newBlock)
        self.writeBlocks()

    def writeBlocks(self):
        """
            Method to write new mined block to blockchain
        """
        def _to_serializable(obj):
            if isinstance(obj, bytes):
                try:
                    return obj.decode('utf-8')
                except Exception:
                    return obj.decode('latin-1')
            if isinstance(obj, dict):
                return dict((k, _to_serializable(v)) for k, v in obj.items())
            if isinstance(obj, list):
                return [_to_serializable(v) for v in obj]
            return obj

        chainData = []
        for eachBlock in self.chain:
            chainData.append(_to_serializable(eachBlock.__dict__))

        with open("chain.txt", "w", encoding='utf-8') as dataFile:
            dataFile.write(json.dumps(chainData, indent=4))

    def loadFromFile(self, filename="chain.txt"):
        """
            Load blockchain from a json file (chain.txt)
        """
        if not os.path.exists(filename):
            return
        f = open(filename, "r")
        try:
            data = json.loads(f.read())
        except Exception:
            f.close()
            return
        f.close()

        loaded = []
        for b in data:
            # Recreate Block object but preserve stored metadata
            blk = Block(b.get('data'), index=b.get('index', 0))
            blk.timestamp = b.get('timestamp', blk.timestamp)
            blk.nonce = b.get('nonce', blk.nonce)
            blk.previousHash = b.get('previousHash', blk.previousHash)
            blk.hash = b.get('hash', blk.hash)
            loaded.append(blk)

        self.chain = loaded

    def reMineFrom(self, start_index):
        """
            Re-mine blocks starting from start_index (inclusive) to restore chain validity
        """
        if start_index <= 0:
            start_index = 1
        for i in range(start_index, len(self.chain)):
            # ensure previousHash is correct
            self.chain[i].previousHash = self.chain[i-1].hash
            # reset nonce and re-mine
            self.chain[i].nonce = 0
            self.chain[i].hash = self.chain[i].calculateHash()
            self.chain[i].mineBlock(self.difficulty)
        # persist changes
        self.writeBlocks()

    def updateBlock(self, index, newData):
        """
            Update data of block at given index and re-mine following blocks.
        """
        if index <= 0 or index >= len(self.chain):
            raise IndexError("Block index out of range")
        self.chain[index].data = newData
        # re-mine this and following blocks
        self.reMineFrom(index)

    def swapBlocks(self, idx1, idx2):
        """
            Swap the `data` field of two blocks identified by their indices and re-mine from the
            smaller of the two indices.
        """
        if idx1 <= 0 or idx2 <= 0 or idx1 >= len(self.chain) or idx2 >= len(self.chain):
            raise IndexError("Block index out of range")
        self.chain[idx1].data, self.chain[idx2].data = self.chain[idx2].data, self.chain[idx1].data
        self.reMineFrom(min(idx1, idx2))
