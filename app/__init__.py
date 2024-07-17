# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 13:59:24 2024

@author: anggi
"""

# app/__init__.py
from flask import Flask

app = Flask(__name__)

from app import server
