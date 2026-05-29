# Jeux m'occupe - Plateforme d'e-commerce de jeux de société

Une plateforme moderne pour acheter et vendre des jeux de société d'occasion entre particuliers.

## 🚀 Démarrage rapide

### Prérequis
- Python 3.9+
- Node.js 18+
- pip

### Installation

1. **Cloner le projet et installer les dépendances Python**
```bash
pip install -r requirements.txt
```

2. **Installer les dépendances Node.js**
```bash
npm install
```

3. **Créer la base de données**
```bash
python -c "from app import create_app, db; app = create_app(); db.create_all()"
```

4. **Lancer le serveur de développement**
```bash
npm run dev
```

Le serveur Flask démarre sur `http://localhost:5000`

## 📁 Structure du projet

```
jeux-m-occupe/
├── app/
│   ├── models/          # Modèles SQLAlchemy
│   ├── routes/          # Blueprints API
│   ├── static/          # CSS, JS, images
│   └── templates/       # Templates HTML
├── run.py              # Point d'entrée
├── config.py           # Configuration
└── requirements.txt    # Dépendances Python
```

## 🗄️ Base de données

### Modèles principaux:
- **User**: Utilisateurs (acheteurs/vendeurs)
- **Product**: Annonces de jeux
- **Cart**: Paniers utilisateurs
- **Order**: Commandes
- **Review**: Avis et notations

## 🔌 API Endpoints

### Authentification
- `POST /api/auth/register` - Inscription
- `POST /api/auth/login` - Connexion
- `GET /api/auth/profile` - Profil (protected)

### Produits
- `GET /api/products` - Lister les produits
- `GET /api/products/<id>` - Détail produit
- `GET /api/products/categories` - Catégories

### Vente
- `POST /api/selling/products` - Créer une annonce
- `GET /api/selling/products` - Mes annonces
- `PATCH /api/selling/products/<id>` - Modifier une annonce

### Panier
- `GET /api/cart` - Voir le panier
- `POST /api/cart/items` - Ajouter un article
- `DELETE /api/cart/items/<id>` - Supprimer un article

### Commandes
- `POST /api/orders` - Créer une commande
- `GET /api/orders` - Mes commandes
- `PATCH /api/orders/<id>/status` - Mettre à jour le statut

## 🎨 Frontend

- **Mobile-first**: Conçu pour mobile en priorité
- **Tailwind CSS**: Styling rapide et responsive
- **Vanilla JS**: Pas de dépendances frontend
- **API-first**: Séparation front/back complète

### Pages principales:
- Accueil
- Acheter (catalogue avec filtres)
- Vendre (création d'annonce)
- Panier
- Compte (profil, mes annonces, achats/ventes)

## 🔐 Authentification

- JWT (tokens stockés en localStorage)
- Tokens valides 30 jours
- Routes protégées par `@jwt_required()`

## 📋 Fonctionnalités implémentées

✅ Inscription/connexion
✅ Création et édition d'annonces
✅ Recherche et filtrage de produits
✅ Système de panier
✅ Gestion des commandes
✅ Profil utilisateur
✅ Interface mobile-first
✅ API RESTful complète

## 🚀 Production

Pour déployer en production:

```bash
# Build Tailwind CSS
npm run build

# Définir les variables d'environnement
export FLASK_ENV=production
export JWT_SECRET_KEY=your-secret-key
export DATABASE_URL=postgresql://...

# Lancer avec Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'
```

## 📝 Notes de développement

- Les images de produits ne sont pas uploadées, utiliser une URL externe
- Les notifications ne sont pas implémentées
- Le paiement n'est pas intégré (à faire)
- Les tests unitaires ne sont pas écrits
- L'upload d'images devrait utiliser un service cloud (AWS S3, Cloudinary, etc.)

## 📞 Support

Pour toute question, consultez la documentation du code ou ouvrez une issue.
# jeux-m-occupe
