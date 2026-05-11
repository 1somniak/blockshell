#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Swap the data of block index 23 and 24 (preserves genesis at index 0).
Remine following blocks to keep chain valid.
"""
from blockchain.chain import Blockchain

def main():
    coin = Blockchain()
    coin.loadFromFile()
    if len(coin.chain) <= 24:
        print('Chain too small (need at least 25 entries including genesis).')
        return
    # swap blocks at indices 23 and 24
    idx1 = 23
    idx2 = 24
    print('Swapping blocks %d and %d...' % (idx1, idx2))
    coin.swapBlocks(idx1, idx2)
    print('Swap complete. chain.txt updated.')

if __name__ == '__main__':
    main()
