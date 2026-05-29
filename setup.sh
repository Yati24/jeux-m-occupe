#!/bin/bash

echo "🎮 Jeux m'occupe - Démarrage du projet"
echo ""

echo "📦 Installation des dépendances Python..."
pip3 install -q -r requirements.txt

echo "📦 Installation des dépendances Node.js..."
npm install --silent

echo "🗄️ Création de la base de données..."
python3 seed_db.py

echo ""
echo "✅ Projet initialisé avec succès!"
echo ""
echo "Pour démarrer le serveur, exécutez:"
echo "  npm run dev"
echo ""
echo "Accédez à l'application sur http://localhost:5000"
echo ""
echo "Comptes de test:"
echo "  - Vendeur 1: seller@example.com / password123"
echo "  - Vendeur 2: collector@example.com / password123"
echo "  - Acheteur: buyer@example.com / password123"
