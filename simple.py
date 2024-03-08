from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    make_response,
)
from utils import create_access_token, setup_assets, get_user, valid_user
from typing import Any
from flask.typing import ResponseReturnValue


app = Flask(__name__)
app.config["SECRET"] = "mysecret"
app.config["ALGORITHMS"] = ["none", "HS256"]
app.config["DEFAULT_ALGORITHM"] = "HS256"
setup_assets(app)

def validate_user() -> Any:
    return get_user(
        request.cookies.get("access_token", ""),
        app.config["SECRET"],
        app.config["ALGORITHMS"],
    )


@app.route("/")
@app.route("/login", methods=["GET"])
def index() -> ResponseReturnValue:
    token = request.cookies.get("access_token")
    if token:
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
        access_token = create_access_token(
            username, app.config["SECRET"], algorithm=app.config["DEFAULT_ALGORITHM"]
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
