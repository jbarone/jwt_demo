from flask import (
    Flask,
    make_response,
    render_template,
    request,
    redirect,
    url_for,
)
from utils import (
    create_access_token,
    get_user,
    setup_assets,
    valid_user,
)
import sqlite3
import jwt
from typing import Any
from flask.typing import ResponseReturnValue


app = Flask(__name__)
app.config["SECRET"] = "mysecret"
app.config["ALGORITHMS"] = ["HS256"]
app.config["DEFAULT_ALGORITHM"] = "HS256"
setup_assets(app)


def get_key() -> Any:
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, key FROM keys ORDER BY RANDOM() LIMIT 1;")
        key = cursor.fetchone()
        cursor.close()
    return key


def lookup_key(kid: str) -> str:
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT key FROM keys WHERE id = '{kid}'")
        key = cursor.fetchone()
        cursor.close()
    if not key:
        raise ValueError("Invalid key")
    return str(key[0])


def validate_user() -> str:
    token = request.cookies.get("access_token", "")
    header = jwt.get_unverified_header(token)
    key = lookup_key(header["kid"])
    return get_user(
        token,
        key,
        app.config["ALGORITHMS"],
    )


@app.route("/")
@app.route("/login", methods=["GET"])
def index() -> ResponseReturnValue:
    if "access_token" in request.cookies:
        try:
            validate_user()
        except Exception:
            response = make_response(render_template("index.html"))
            response.delete_cookie("access_token")
            return response
        else:
            return redirect(url_for("protected"))
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login() -> ResponseReturnValue:
    username = request.form["username"]
    password = request.form["password"]

    if valid_user(username, password):
        kid, key = get_key()
        access_token = create_access_token(
            username,
            key,
            algorithm=app.config["DEFAULT_ALGORITHM"],
            kid=kid,
        )
        response = make_response(redirect(url_for("protected")))
        response.set_cookie("access_token", access_token)
        return response
    else:
        return render_template("index.html", error_msg="Invalid credentials")


@app.route("/protected", methods=["GET"])
def protected() -> ResponseReturnValue:
    try:
        current_user = validate_user()
    except Exception:
        response = make_response(redirect(url_for("index")))
        response.delete_cookie("access_token")
        return response
    return render_template("protected.html", username=current_user)


@app.route("/logout")
def logout() -> ResponseReturnValue:
    response = make_response(redirect(url_for("index")))
    response.delete_cookie("access_token")
    return response


if __name__ == "__main__":
    app.run(debug=True)
