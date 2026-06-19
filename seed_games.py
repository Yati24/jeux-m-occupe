"""
Remplit le catalogue avec de nombreux jeux répartis dans 4 catégories.

    python seed_games.py

- Reclasse les produits existants dans les catégories canoniques.
- Ajoute les jeux manquants (idempotent : ignore ceux déjà présents par titre).
- Donne à chaque jeu une galerie de 3 images.
"""
import re
from app import create_app, db
from app.models.user import User
from app.models.product import Product

# Catégories canoniques (= cartes de la page d'accueil)
POUR_LES_PETITS = "Pour les petits"
EN_FAMILLE = "En famille"
JEUX_EXPERTS = "Jeux Experts"
AMBIANCE = "Ambiance & Soirée"

# Reclassement des produits déjà présents
RECLASSIFY = {
    "Catan": EN_FAMILLE,
    "Ticket to Ride": EN_FAMILLE,
    "Codenames": AMBIANCE,
    "7 Wonders": JEUX_EXPERTS,
    "Splendor": JEUX_EXPERTS,
}

CONDITIONS = ["Comme neuf", "Très bon état", "Bon état", "Acceptable"]

# (titre, éditeur, catégorie, joueurs, durée, âge min, année, prix)
GAMES = [
    # Pour les petits
    ("Le Verger", "Haba", POUR_LES_PETITS, "2-8", "15 min", 3, 2012, 18.0),
    ("Croque-Carotte", "Hasbro", POUR_LES_PETITS, "2-4", "20 min", 4, 2015, 14.0),
    ("Bata-Waf", "Djeco", POUR_LES_PETITS, "2", "10 min", 3, 2016, 9.0),
    ("Pique Plume", "Gigamic", POUR_LES_PETITS, "2-4", "20 min", 4, 2014, 22.0),
    ("Petits Robots", "Le Scorpion Masqué", POUR_LES_PETITS, "2-4", "15 min", 5, 2019, 16.0),
    ("Monza", "Haba", POUR_LES_PETITS, "2-6", "20 min", 5, 2013, 17.0),
    # En famille
    ("Carcassonne", "Z-Man Games", EN_FAMILLE, "2-5", "35 min", 7, 2015, 19.0),
    ("Azul", "Plan B Games", EN_FAMILLE, "2-4", "45 min", 8, 2017, 28.0),
    ("Kingdomino", "Blue Orange", EN_FAMILLE, "2-4", "20 min", 8, 2016, 15.0),
    ("Dixit", "Libellud", EN_FAMILLE, "3-6", "30 min", 8, 2014, 24.0),
    ("Qwirkle", "Iello", EN_FAMILLE, "2-4", "45 min", 6, 2011, 21.0),
    ("Les Aventuriers du Rail Europe", "Days of Wonder", EN_FAMILLE, "2-5", "60 min", 8, 2017, 34.0),
    # Jeux Experts
    ("Terraforming Mars", "Intrafin", JEUX_EXPERTS, "1-5", "120 min", 12, 2017, 45.0),
    ("Wingspan", "Stonemaier Games", JEUX_EXPERTS, "1-5", "70 min", 10, 2019, 42.0),
    ("Agricola", "Lookout Games", JEUX_EXPERTS, "1-4", "120 min", 12, 2016, 38.0),
    ("Scythe", "Stonemaier Games", JEUX_EXPERTS, "1-5", "115 min", 14, 2018, 55.0),
    ("Pandemic", "Z-Man Games", JEUX_EXPERTS, "2-4", "45 min", 8, 2013, 25.0),
    ("Brass Birmingham", "Roxley", JEUX_EXPERTS, "2-4", "120 min", 14, 2018, 52.0),
    # Ambiance & Soirée
    ("Time's Up", "Repos Production", AMBIANCE, "4-12", "60 min", 12, 2012, 16.0),
    ("Loup-Garou de Thiercelieux", "Lui-même", AMBIANCE, "8-18", "30 min", 10, 2010, 11.0),
    ("Dobble", "Asmodee", AMBIANCE, "2-8", "15 min", 6, 2015, 9.0),
    ("Jungle Speed", "Asmodee", AMBIANCE, "2-10", "15 min", 7, 2014, 12.0),
    ("Skull King", "Matagot", AMBIANCE, "2-6", "30 min", 8, 2018, 14.0),
    ("Concept", "Repos Production", AMBIANCE, "4-12", "40 min", 10, 2013, 23.0),
]


def slugify(title):
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')


def gallery(title):
    s = slugify(title)
    return [f"https://picsum.photos/seed/{s}-{n}/600/450" for n in range(1, 4)]


app = create_app('development')
with app.app_context():
    # Vendeurs disponibles
    sellers = User.query.filter_by(is_admin=False, is_banned=False).all()
    pref = [u for u in sellers if u.username in ('seller_pro', 'game_collector')]
    sellers = pref or sellers
    if not sellers:
        print("[ERREUR] Aucun vendeur disponible. Lancez d'abord seed_db.py")
        raise SystemExit(1)

    # 1) Reclasser les produits existants
    reclassed = 0
    for title, cat in RECLASSIFY.items():
        p = Product.query.filter_by(title=title).first()
        if p and p.category != cat:
            p.category = cat
            reclassed += 1
    db.session.commit()

    # 2) Ajouter les jeux manquants
    added = 0
    for i, (title, pub, cat, players, time, age, year, price) in enumerate(GAMES):
        if Product.query.filter_by(title=title).first():
            continue
        p = Product(
            title=title,
            description=f"{title} — jeu de société d'occasion vérifié et complet, prêt à jouer.",
            publisher=pub,
            category=cat,
            condition=CONDITIONS[i % len(CONDITIONS)],
            price=price,
            stock=(i % 4) + 1,
            status='available',
            seller_id=sellers[i % len(sellers)].id,
            number_of_players=players,
            playing_time=time,
            min_age=age,
            year=year,
        )
        p.image_list = gallery(title)
        db.session.add(p)
        added += 1
    db.session.commit()

    # 3) S'assurer que les anciens produits ont aussi une galerie
    for p in Product.query.all():
        if not p.image_list:
            p.image_list = gallery(p.title)
    db.session.commit()

    print(f"[OK] {reclassed} produit(s) reclassé(s), {added} jeu(x) ajouté(s).")
    print(f"     Total catalogue : {Product.query.count()} produits")
    for cat in (POUR_LES_PETITS, EN_FAMILLE, JEUX_EXPERTS, AMBIANCE):
        print(f"       - {cat} : {Product.query.filter_by(category=cat).count()}")
