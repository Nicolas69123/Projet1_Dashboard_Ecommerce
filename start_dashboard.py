#!/usr/bin/env python3
"""
Script de lancement du Dashboard E-commerce
Double-cliquez sur ce fichier pour lancer le dashboard !
"""
import os
import sys
import webbrowser
import http.server
import socketserver
import threading

# Se placer dans le bon dossier
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 1. Vérifier si les données existent, sinon les générer
if not os.path.exists('data/transactions.csv'):
    print("📊 Génération des données...")
    exec(open('src/generate_data.py').read())
else:
    print("✅ Données déjà présentes")

# 2. Lancer un serveur web local
PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

# Ouvrir le navigateur après un court délai
def open_browser():
    webbrowser.open(f'http://localhost:{PORT}/dashboard.html')

timer = threading.Timer(1.0, open_browser)
timer.start()

# Démarrer le serveur
print(f"🚀 Dashboard disponible sur http://localhost:{PORT}/dashboard.html")
print("   Appuyez sur Ctrl+C pour arrêter")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Arrêt du serveur")
        sys.exit(0)
