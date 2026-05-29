# Jeux m'occupe - CLAUDE.md

## 📌 Contexte du projet

Plateforme e-commerce de jeux de société d'occasion basée sur Flask + Tailwind.
Site français, mobile-first, pour permettre aux particuliers d'acheter/vendre des jeux usagés.

## 🏗️ Stack

**Backend:**
- Flask 3.0 avec blueprints modulaires
- SQLAlchemy ORM
- JWT pour authentification
- SQLite (dev) / PostgreSQL (prod)

**Frontend:**
- Tailwind CSS v4 (mobile-first)
- Vanilla JavaScript (fetch API)
- Templates Jinja2

## 📂 Structure

```
app/
├── __init__.py          # Factory et routes
├── models/              # User, Product, Cart, Order, Review
├── routes/              # auth, products, cart, orders, users, selling
├── templates/           # HTML Jinja2
└── static/              # CSS, JS
```

## 🚀 Commandes principales

```bash
npm run dev                    # Lancer le serveur + Tailwind watch
npm run tailwind:build         # Builder CSS pour production
python3 seed_db.py             # Remplir la DB de test
python3 -c "from app import db; db.create_all()"  # Créer les tables
```

## 🔑 Points clés

### Authentification
- JWT tokens en localStorage
- Routes protégées avec `@jwt_required()`
- Tokens valides 30 jours

### Base de données
- Relations Many-to-Many bien définies
- Cascade deletes pour les suppressions
- Indexes sur colonnes fréquemment recherchées

### API REST
- `/api/` pour tous les endpoints
- Pagination avec `?page=1&per_page=12`
- Filtres: `?category=`, `?min_price=`, `?max_price=`

### Frontend
- Pages: accueil, acheter, vendre, panier, compte
- Navigation mobile bottom, desktop top
- Données chargées via fetch() côté client

## ⚡ À faire ensuite

Priority haute:
- [ ] Upload d'images (S3 ou Cloudinary)
- [ ] Intégration paiement (Stripe)
- [ ] Tests unitaires
- [ ] Validation des données côté serveur renforcée

Priority moyenne:
- [ ] Chat acheteur/vendeur en temps réel
- [ ] Système de notation des vendeurs
- [ ] Favoris/Wishlist
- [ ] Notifications par email

Priority basse:
- [ ] Recommandations personnalisées
- [ ] Blog/FAQ
- [ ] Admin dashboard
- [ ] Analytics

## 🛠️ Conventions

**Naming:**
- Variables: `snake_case`
- Classes: `PascalCase`
- Routes API: `/api/resource/action`

**Routes Flask:**
- GET: lire des données
- POST: créer
- PATCH: modifier
- DELETE: supprimer

**Modèles:**
- Tous les modèles ont `created_at`, `updated_at`
- Clés étrangères toujours indexées
- Relationships bidirectionnelles quand pertinent

## 🔒 Sécurité

✅ Mots de passe: bcrypt
✅ CORS configuré
✅ JWT pour API
✅ SQL Injection: SQLAlchemy ORM
❌ TODO: Rate limiting
❌ TODO: Validation complète côté serveur
❌ TODO: HTTPS en production

## 📝 Committing

Commits suivent ce format:
- `feat: ...` - nouvelle fonctionnalité
- `fix: ...` - correction de bug
- `refactor: ...` - refactoring
- `docs: ...` - documentation
- `test: ...` - tests

## 🎯 Vision produit

Platform C2C (consumer-to-consumer) pour jeux de société. Valeur client:
- Pour vendeurs: monétiser leurs jeux inutilisés
- Pour acheteurs: acheter à bas prix avant neuf

Différenciation vs vinted/leboncoin:
- Niche spécialisée jeux
- Interface simple et épurée
- Focus sur qualité des annonces
