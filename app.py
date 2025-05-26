# app.py
from flask import Flask, render_template, request, jsonify
import sqlite3
import datetime
import random
import requests
import json

app = Flask(__name__)

# Configuración básica
app.config['SECRET_KEY'] = 'clave-secreta-para-examen'

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)