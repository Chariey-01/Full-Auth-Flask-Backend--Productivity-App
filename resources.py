from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from extensions import db
from models import User, Note

auth_bp = Blueprint("auth", __name__)
notes_bp = Blueprint("notes", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Username is already taken"}), 400

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict()), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    return jsonify(user.to_dict()), 200


@notes_bp.route("/notes", methods=["GET"])
@jwt_required()
def get_notes():
    user_id = int(get_jwt_identity())

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = Note.query.filter_by(user_id=user_id).paginate(
        page=page, per_page=per_page, error_out=False
    )

    notes = [note.to_dict() for note in pagination.items]

    return jsonify({
        "notes": notes,
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
    }), 200


@notes_bp.route("/notes", methods=["POST"])
@jwt_required()
def create_note():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    content = data.get("content")

    if not title or not title.strip() or not content or not content.strip():
        return jsonify({"error": "Title and content are required"}), 400

    note = Note(title=title, content=content, user_id=user_id)
    db.session.add(note)
    db.session.commit()

    return jsonify(note.to_dict()), 201


@notes_bp.route("/notes/<int:note_id>", methods=["GET"])
@jwt_required()
def get_note(note_id):
    user_id = int(get_jwt_identity())
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()

    if not note:
        return jsonify({"error": "Note not found"}), 404

    return jsonify(note.to_dict()), 200


@notes_bp.route("/notes/<int:note_id>", methods=["PATCH"])
@jwt_required()
def update_note(note_id):
    user_id = int(get_jwt_identity())
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()

    if not note:
        return jsonify({"error": "Note not found"}), 404

    data = request.get_json(silent=True) or {}

    new_title = data.get("title")
    new_content = data.get("content")

    if new_title is not None:
        if not new_title.strip():
            return jsonify({"error": "Title cannot be empty"}), 400
        note.title = new_title

    if new_content is not None:
        if not new_content.strip():
            return jsonify({"error": "Content cannot be empty"}), 400
        note.content = new_content

    db.session.commit()

    return jsonify(note.to_dict()), 200


@notes_bp.route("/notes/<int:note_id>", methods=["DELETE"])
@jwt_required()
def delete_note(note_id):
    user_id = int(get_jwt_identity())
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()

    if not note:
        return jsonify({"error": "Note not found"}), 404

    db.session.delete(note)
    db.session.commit()

    return jsonify({"message": "Note deleted"}), 200
