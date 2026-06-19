"""
Modifier les photos d'une annonce existante.

Lister les annonces et leurs photos :
    python set_product_images.py --list

Définir la galerie d'une annonce (remplace les photos existantes).
Les sources peuvent être des URLs OU des chemins de fichiers locaux
(les fichiers locaux sont copiés dans app/static/uploads/) :

    python set_product_images.py 1 https://exemple.com/catan1.jpg https://exemple.com/catan2.jpg
    python set_product_images.py 1 "C:/Users/mathi/Desktop/catan.jpg"

La 1ère photo de la liste devient l'image principale de l'annonce.
"""
import os
import sys
import shutil
import uuid

from app import create_app, db
from app.models.product import Product

ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def list_products():
    for p in Product.query.order_by(Product.id).all():
        imgs = p.image_list
        print(f"#{p.id:<3} {p.title:<20} {len(imgs)} photo(s)")
        for u in imgs:
            print(f"       - {u}")


def resolve_source(src, upload_dir):
    """URL -> renvoyée telle quelle. Fichier local -> copié dans uploads/."""
    if src.startswith(('http://', 'https://', '/static/')):
        return src

    if not os.path.isfile(src):
        print(f"[ERREUR] Fichier introuvable : {src}")
        sys.exit(1)

    ext = src.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED:
        print(f"[ERREUR] Format non supporté : {src}")
        sys.exit(1)

    os.makedirs(upload_dir, exist_ok=True)
    name = f"{uuid.uuid4().hex}.{ext}"
    shutil.copy(src, os.path.join(upload_dir, name))
    return f"/static/uploads/{name}"


def set_images(product_id, sources):
    product = Product.query.get(product_id)
    if not product:
        print(f"[ERREUR] Aucune annonce avec l'id {product_id}")
        sys.exit(1)

    upload_dir = os.path.join(os.path.dirname(__file__), 'app', 'static', 'uploads')
    urls = [resolve_source(s, upload_dir) for s in sources]

    product.image_list = urls
    db.session.commit()
    print(f"[OK] Annonce #{product.id} ('{product.title}') mise à jour avec {len(urls)} photo(s) :")
    for u in urls:
        print(f"     - {u}")
    print(f"     Image principale : {product.image_url}")


if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        if len(sys.argv) >= 2 and sys.argv[1] == '--list':
            list_products()
        elif len(sys.argv) >= 3:
            set_images(int(sys.argv[1]), sys.argv[2:])
        else:
            print(__doc__)
