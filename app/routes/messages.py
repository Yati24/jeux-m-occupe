from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.message import Message
from app.models.user import User
from app.models.product import Product
from sqlalchemy import or_, and_

bp = Blueprint('messages', __name__, url_prefix='/api/messages')


@bp.route('', methods=['GET'])
@jwt_required()
def list_conversations():
    """Retourne les conversations de l'utilisateur connecté, groupées par (interlocuteur, produit)."""
    user_id = int(get_jwt_identity())

    # Tous les messages où l'utilisateur est impliqué
    msgs = Message.query.filter(
        or_(Message.sender_id == user_id, Message.recipient_id == user_id)
    ).order_by(Message.created_at.desc()).all()

    # Dédupliquer par clé (other_user_id, product_id) en gardant le message le plus récent
    seen = {}
    for m in msgs:
        other_id = m.recipient_id if m.sender_id == user_id else m.sender_id
        key = (other_id, m.product_id)
        if key not in seen:
            seen[key] = m

    conversations = []
    for (other_id, product_id), m in seen.items():
        other = User.query.get(other_id)
        product = Product.query.get(product_id) if product_id else None
        unread = Message.query.filter_by(recipient_id=user_id, sender_id=other_id, is_read=False, product_id=product_id).count()
        conversations.append({
            'other_user': {'id': other.id, 'username': other.username, 'avatar': other.avatar},
            'product': {'id': product.id, 'title': product.title, 'image_url': product.image_url} if product else None,
            'last_message': {'content': m.content, 'created_at': m.created_at.isoformat(), 'is_mine': m.sender_id == user_id},
            'unread_count': unread,
        })

    # Trier : conversations avec non lus en premier, puis par date
    conversations.sort(key=lambda c: (-(c['unread_count'] > 0), c['last_message']['created_at']), reverse=False)
    conversations.sort(key=lambda c: c['last_message']['created_at'], reverse=True)

    unread_total = Message.query.filter_by(recipient_id=user_id, is_read=False).count()

    return {'conversations': conversations, 'unread_total': unread_total}, 200


@bp.route('/unread-count', methods=['GET'])
@jwt_required()
def unread_count():
    user_id = int(get_jwt_identity())
    count = Message.query.filter_by(recipient_id=user_id, is_read=False).count()
    return {'count': count}, 200


@bp.route('/conversation/<int:other_user_id>', methods=['GET'])
@jwt_required()
def get_conversation(other_user_id):
    """Messages entre l'utilisateur connecté et other_user_id, filtrable par product_id."""
    user_id = int(get_jwt_identity())
    product_id = request.args.get('product_id', type=int)

    query = Message.query.filter(
        or_(
            and_(Message.sender_id == user_id, Message.recipient_id == other_user_id),
            and_(Message.sender_id == other_user_id, Message.recipient_id == user_id),
        )
    )
    if product_id:
        query = query.filter_by(product_id=product_id)

    msgs = query.order_by(Message.created_at.asc()).all()

    # Marquer comme lus
    Message.query.filter_by(sender_id=other_user_id, recipient_id=user_id, is_read=False, product_id=product_id).update({'is_read': True})
    db.session.commit()

    other = User.query.get(other_user_id)
    product = Product.query.get(product_id) if product_id else None

    return {
        'messages': [m.to_dict() for m in msgs],
        'other_user': {'id': other.id, 'username': other.username, 'avatar': other.avatar, 'first_name': other.first_name},
        'product': {'id': product.id, 'title': product.title, 'image_url': product.image_url} if product else None,
    }, 200


@bp.route('', methods=['POST'])
@jwt_required()
def send_message():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    recipient_id = data.get('recipient_id')
    content = (data.get('content') or '').strip()
    product_id = data.get('product_id')

    if not recipient_id or not content:
        return {'error': 'recipient_id et content sont requis'}, 400
    if recipient_id == user_id:
        return {'error': 'Vous ne pouvez pas vous envoyer un message'}, 400
    if not User.query.get(recipient_id):
        return {'error': 'Destinataire introuvable'}, 404

    msg = Message(
        sender_id=user_id,
        recipient_id=recipient_id,
        product_id=product_id or None,
        content=content,
    )
    db.session.add(msg)
    db.session.commit()
    return msg.to_dict(), 201
