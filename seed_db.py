from app import create_app, db
from app.models.user import User
from app.models.product import Product
from datetime import datetime

app = create_app('development')

with app.app_context():
    db.create_all()

    # Vérifier si les données existent déjà
    if User.query.count() > 0:
        print("Base de données déjà peuplée")
        exit()

    # Créer des utilisateurs test
    seller1 = User(
        username='seller_pro',
        email='seller@example.com',
        first_name='Jean',
        last_name='Vendeur',
        bio='Je vends mes anciens jeux, plus de place!',
        city='Paris',
        seller_rating=4.8
    )
    seller1.set_password('password123')

    seller2 = User(
        username='game_collector',
        email='collector@example.com',
        first_name='Marie',
        last_name='Collectrice',
        bio='Collectionneuse de jeux vintage',
        city='Lyon',
        seller_rating=5.0
    )
    seller2.set_password('password123')

    buyer = User(
        username='happy_buyer',
        email='buyer@example.com',
        first_name='Pierre',
        last_name='Acheteur'
    )
    buyer.set_password('password123')

    db.session.add_all([seller1, seller2, buyer])
    db.session.commit()

    # Créer des produits test
    products = [
        Product(
            title='Catan',
            description='Jeu en très bon état, boîte complète',
            category='Jeux de stratégie',
            condition='Très bon',
            price=25.00,
            seller_id=seller1.id,
            number_of_players='2-4',
            playing_time='60-90 min',
            year=2015
        ),
        Product(
            title='Ticket to Ride',
            description='Édition Europe, tous les éléments présents',
            category='Jeux de société',
            condition='Excellent',
            price=35.00,
            seller_id=seller1.id,
            number_of_players='2-5',
            playing_time='90 min',
            year=2018
        ),
        Product(
            title='Codenames',
            description='Jeux de party complet',
            category='Jeux de party',
            condition='Bon',
            price=12.50,
            seller_id=seller2.id,
            number_of_players='2-8',
            playing_time='15 min',
            year=2020
        ),
        Product(
            title='7 Wonders',
            description='Version française complète avec extensions',
            category='Jeux de stratégie',
            condition='Très bon',
            price=30.00,
            seller_id=seller2.id,
            number_of_players='2-7',
            playing_time='45-60 min',
            year=2017
        ),
        Product(
            title='Splendor',
            description='Jeu de gestion en très bon état',
            category='Jeux de stratégie',
            condition='Très bon',
            price=20.00,
            seller_id=seller1.id,
            number_of_players='2-4',
            playing_time='30 min',
            year=2016
        ),
    ]

    db.session.add_all(products)
    db.session.commit()

    print("✅ Base de données initialisée avec succès!")
    print(f"   - {User.query.count()} utilisateurs créés")
    print(f"   - {Product.query.count()} produits créés")
