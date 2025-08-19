from flask import Blueprint, jsonify, request, abort, redirect, url_for
import parts_service
import wishlist_service

bp = Blueprint('parts_api', __name__)


@bp.route('/parts', methods=['GET'])
def parts_list():
    parts = parts_service.list_parts()
    return jsonify(parts)


@bp.route('/parts/<int:part_id>', methods=['GET'])
def parts_get(part_id):
    p = parts_service.get_part(part_id)
    if not p:
        abort(404)
    return jsonify(p)


@bp.route('/parts', methods=['POST'])
def parts_create():
    if request.content_type and request.content_type.startswith('application/json'):
        data = request.get_json() or {}
    else:
        # request.form is an ImmutableMultiDict; convert to mutable dict
        data = request.form.to_dict() if request.form else {}
    # normalize price
    if 'price' in data and data.get('price') not in (None, ''):
        try:
            data['price'] = int(data['price'])
        except Exception:
            return jsonify({'error': 'price must be integer'}), 400

    # generate a validation token and mark as not validated
    import uuid
    token = uuid.uuid4().hex
    data['validation_token'] = token
    data['is_validated'] = False

    new_id = parts_service.create_part(data)
    if new_id is None:
        abort(503)
    # enqueue validation email if contact_email provided
    email = data.get('contact_email')
    if email:
        try:
            from tasks import send_validation_email
            send_validation_email.delay(email, new_id, data.get('title', ''), token)
        except Exception:
            # best effort; don't fail creation if broker is not ready
            pass
    # If the request was a form submission from the HTML UI, redirect back to index
    if not (request.content_type and request.content_type.startswith('application/json')):
        return redirect(url_for('index', pending=1))
    return jsonify({'id': new_id}), 201


@bp.route('/parts/<int:part_id>', methods=['PUT', 'PATCH'])
def parts_update(part_id):
    if request.content_type and request.content_type.startswith('application/json'):
        data = request.get_json() or {}
    else:
        data = request.form.to_dict() if request.form else {}
    if 'price' in data and data.get('price') not in (None, ''):
        try:
            data['price'] = int(data['price'])
        except Exception:
            return jsonify({'error': 'price must be integer'}), 400
    ok = parts_service.update_part(part_id, data)
    if not ok:
        abort(404)
    return jsonify({'updated': part_id})


@bp.route('/parts/<int:part_id>', methods=['DELETE'])
def parts_delete(part_id):
    ok = parts_service.delete_part(part_id)
    if not ok:
        abort(404)
    return jsonify({'deleted': part_id})


@bp.route('/parts/<int:part_id>/favourite', methods=['POST'])
def parts_favourite(part_id):
    # Ensure wishlist id
    wid = request.cookies.get('wishlist_id')
    created = False
    if not wid:
        wid = wishlist_service.new_wishlist_id()
        created = True
    ok = wishlist_service.add_favorite(wid, part_id)
    resp = jsonify({'id': part_id, 'favorited': True})
    if created:
        resp.set_cookie('wishlist_id', wid, max_age=60*60*24*365)
    return resp


@bp.route('/parts/<int:part_id>/favourite', methods=['DELETE'])
def parts_unfavourite(part_id):
    wid = request.cookies.get('wishlist_id')
    if not wid:
        return jsonify({'id': part_id, 'favorited': False}), 200
    ok = wishlist_service.remove_favorite(wid, part_id)
    return jsonify({'id': part_id, 'favorited': False})


@bp.route('/wishlist', methods=['GET'])
def get_wishlist():
    wid = request.cookies.get('wishlist_id')
    if not wid:
        return jsonify([])
    vals = list(wishlist_service.list_favorites(wid))
    return jsonify(vals)
