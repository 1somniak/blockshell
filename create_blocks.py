#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create and append 60 student blocks to chain.txt using `students` file.
Python 2 compatible.
"""
import os
import sys
import base64
from blockchain.chain import Block, Blockchain

STUDENTS_FILE = os.path.join(os.path.dirname(__file__), 'students')

def read_students(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        return [l.strip() for l in f if l.strip()]

def make_person_record(name, idx):
    # name like first.last
    first = 'Student'
    last = str(idx)
    if '.' in name:
        parts = name.split('.')
        first = parts[0]
        last = parts[-1]
    elif ' ' in name:
        parts = name.split()
        first = parts[0]
        last = parts[-1]
    else:
        first = name
        last = 'Etudiant'

    uid = 'uid-epita-%03d' % (idx,)
    email = '%s.%s@epita.fr' % (first, last)
    image_b64 = base64.b64encode(os.urandom(128)).decode('ascii')
    return {
        'uid-epita': uid,
        'email-epita': email,
        'nom': last.capitalize(),
        'prenom': first.capitalize(),
        'image': image_b64,
    }

def main():
    students = read_students(STUDENTS_FILE)
    coin = Blockchain()
    # load existing chain if present
    coin.loadFromFile()

    target = 60
    existing = len(coin.chain) - 1  # excluding genesis
    to_create = target - existing
    if to_create <= 0:
        print('Chain already has %d blocks (excluding genesis).' % existing)
        return

    print('Creating %d blocks (from %d to %d)...' % (to_create, existing+1, target))
    for i in range(existing, target):
        # i is count of existing blocks (0-based excluding genesis)
        idx = i + 1
        if i < len(students):
            name = students[i]
        else:
            name = 'student%02d' % idx
        data = make_person_record(name, idx)
        coin.addBlock(Block(data=data))

    print('Done. Chain length now: %d (including genesis).' % len(coin.chain))

if __name__ == '__main__':
    main()
