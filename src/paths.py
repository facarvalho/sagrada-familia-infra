#!/usr/bin/env python3
"""Caminhos de saida do projeto. Os scripts ficam em src/ e escrevem em docs/ (GitHub Pages)."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")
IMG = os.path.join(DOCS, "img")
for _d in (DOCS, IMG):
    os.makedirs(_d, exist_ok=True)

def docs(name):
    return os.path.join(DOCS, name)

def img(name):
    return os.path.join(IMG, name)

def data(name):
    return os.path.join(DATA, name)
