import os
import time
from flask import Flask, render_template, request, redirect, url_for, abort, jsonify

from parts_api import bp as parts_bp
import parts_service
import wishlist_service

app = Flask(__name__)
app.register_blueprint(parts_bp)


def get_db_conn():
    # Delegate to the service layer which handles MySQL connections
    try:
        from parts_service import get_conn
    except Exception:
        from app.parts_service import get_conn
    return get_conn()


@app.get("/")
def index():
    parts = parts_service.list_parts(limit=50)
    pending = request.args.get('pending')
    # ensure wishlist cookie and fetch wishlist items
    wid = request.cookies.get('wishlist_id')
    if not wid:
        wid = wishlist_service.new_wishlist_id()
        wishlist = set()
    else:
        try:
            wishlist = wishlist_service.list_favorites(wid)
        except Exception:
            wishlist = set()

    # Fetch part details for items in wishlist to show in sidebar
    wishlist_items = []
    try:
        for pid in wishlist:
            p = parts_service.get_part(int(pid))
            if p:
                wishlist_items.append(p)
    except Exception:
        wishlist_items = []

    resp = render_template("index.html", parts=parts, now=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), pending=pending, wishlist=wishlist, wishlist_items=wishlist_items)
    from flask import make_response
    response = make_response(resp)
    if not request.cookies.get('wishlist_id'):
        response.set_cookie('wishlist_id', wid, max_age=60*60*24*365)
    return response


@app.get('/parts/<int:part_id>/edit')
def edit_part_get(part_id):
    p = parts_service.get_part(part_id)
    if not p:
        abort(404)
    return render_template('edit.html', part=p)


@app.post('/parts/<int:part_id>/edit')
def edit_part_post(part_id):
    data = request.form.to_dict()
    if 'price' in data and data.get('price') not in (None, ''):
        try:
            data['price'] = int(data['price'])
        except Exception:
            return "Price must be integer", 400
    ok = parts_service.update_part(part_id, data)
    if not ok:
        abort(404)
    return redirect(url_for('index'))


@app.get('/healthz')
def healthz():
    conn = get_db_conn()
    db_status = 'connected' if conn else 'unavailable'
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS healthcheck (ts TIMESTAMP DEFAULT NOW())")
            conn.commit()
        except Exception:
            db_status = 'error'
        finally:
            conn.close()
    return jsonify({"status": "ok", "db": db_status})




@app.get('/validate/<token>')
def validate_token_route(token):
    try:
        from parts_service import validate_token
    except Exception:
        from app.parts_service import validate_token
    ok = validate_token(token)
    if not ok:
        return "Invalid or expired validation token", 404
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
