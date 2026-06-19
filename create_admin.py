"""
Script de gestion des administrateurs.

Usage :
    python create_admin.py                      # crée l'admin par défaut
    python create_admin.py <email> <password> [username]

Ce script :
  1. S'assure que tous les clients existants ont bien is_admin = 0 (backfill défensif).
  2. Crée (ou promeut) un compte administrateur avec is_admin = 1.
"""
import sys
from app import create_app, db
from app.models.user import User

# Identifiants admin par défaut (à changer en production !)
DEFAULT_EMAIL = 'admin@jeuxmoccupe.fr'
DEFAULT_PASSWORD = 'Admin1234!'
DEFAULT_USERNAME = 'admin'


def ensure_clients_not_admin():
    """Backfill : tout utilisateur dont is_admin est NULL repasse à False (0)."""
    fixed = User.query.filter(User.is_admin.is_(None)).update(
        {User.is_admin: False}, synchronize_session=False
    )
    if fixed:
        db.session.commit()
        print(f"[OK] {fixed} utilisateur(s) corrigé(s) -> is_admin = 0")


def create_admin(email, password, username):
    user = User.query.filter_by(email=email).first()

    if user:
        # Le compte existe : on le promeut admin
        user.is_admin = True
        db.session.commit()
        print(f"[OK] Utilisateur existant '{user.username}' promu administrateur (is_admin = 1)")
        return

    if User.query.filter_by(username=username).first():
        print(f"[ERREUR] Le nom d'utilisateur '{username}' est déjà pris. Choisissez-en un autre.")
        sys.exit(1)

    admin = User(
        username=username,
        email=email,
        first_name='Admin',
        last_name='JeuxMoccupe',
        is_admin=True,
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print(f"[OK] Compte administrateur créé : {email} (is_admin = 1)")
    print(f"   Mot de passe : {password}")


if __name__ == '__main__':
    email = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_EMAIL
    password = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_PASSWORD
    username = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_USERNAME

    app = create_app('development')
    with app.app_context():
        db.create_all()
        ensure_clients_not_admin()
        create_admin(email, password, username)
