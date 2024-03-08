from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    make_response,
)
from utils import create_access_token, setup_assets, get_user, valid_user
from flask.typing import ResponseReturnValue


app = Flask(__name__)
app.config["PRIVATE_KEY"] = b"""-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAvD7wildoFUqmzJv+rFby8HEMAX0qR7DuVZwXSV4gRLkXCV5w
IezqCT6/cIw8bBocLOKiY0W1usDvbHDOKZSn93DV6KBawZiAjgQYR2mGepLaBJOS
GrgghWkh79QnxIVGjs8W93vESHuTjoOt/O2+C/UGVsatAspSxMNithRhBrZkd0Wt
n9Vaz8475bFfzeWrvpEsSCbbsVSWw1iVh2uFHLsf0QtpNY45C89QuVAS5lcgPx3J
SodV3Pc+5bjotI5z/1j8o2oWeUOgTeajgDlpp34IbHbQcd+namTn1kXPWrisl9jg
xX0xxQ0DoR4hvoTzdskJoATlWoUoItJbjDjhhQIDAQABAoIBAAaGuuMo8mhU9rrY
QhH3T714EqqVWTTNrjpuMQmvoQT3UvrVrD1Y3KizMelOfor6GsKQA7Sj+Y/YcyFU
Bdzy+1T8s5KfLWMepn8fjQUiZCTcWE4Mg0yFPq3K/jMcEvOt8f5iF2s/SyF++0rx
E/du+WxDs4ao2HdLMwE0WITa6J3WMyMJ3ZLV0ww1NbXv9AFxZugeTTChlhkhRVG7
2BFfX0ARlPhWvi7cyOk2ygG4O2lrkeKDZMsEywyqePGotYcanSZWy82ct7zpsZTK
WEyBTe2L6pN4f5z451x+6DmkOYquaBI9YmSPKAXzPUtHSaVlmdLTfL4eoee2xjYx
Zvgj4kECgYEA4zWr398DI7zFJiGo5ndKmueESj771jlCiUQIz944oSg3nyfqC/Yp
lZ/VuycYA/DQ7D3P4jcmrlaMhTWXs+BBVwKLsc+akMeui4wlzYpOGvqdt33V7h1+
7sFMMsg9GZvQzrfHksOyXImvnYXDPWKci4+xBiEgNS62iaDAUroYrGUCgYEA1BlX
2D4oHhSM0WcjzZr/CILoGEtmF21Ney6e5p2IZ73uoxz3TTmmiAr3EcGapGCqTWoR
fNkVRQ4dkSr91yRN5Vg08egLRB2bmvvVD7uT5LPP0YwzrH+nIxEyZ7khdzZr+pnm
qpKaWkArOK/nFf4MKlYP9hCDIn5F/cZy75PkPqECgYAaH36eY7apsjd8ldwke0yx
mLLGEo3D6Jt0ysS0mZkrNkOG4gDv1SKc2F6rgOgq89Ihh03SdYLWAo9vdWT2wm7g
wSMsk3Dy+nJgCwIBqsgmI/BkO2yQTwXcD49iO1GDEz4jtk+U2Tk1mIL/enSjJyZW
iXPR/5cDZlaIZloWaN0TXQKBgQCigkCCWS2XzpsOnv4ZvRaHSPXYF31DmeXx6giq
Hi2zfx1nMPxy2Sc1uWEQ48w/Aim6Yvi/Nf1MCcKxxcT0oMZmYS0/5FEtgZoGJ8pZ
4ZkxdGxY3BmDo9NF1RlPy9NOag5V1rGcI/PMDrqPFofym9JqZcKZAJHZTfMGvJS3
6BLLwQKBgQCjeyITDT/c/Q7F8O3fmM59WE7FPgs2Ucw9KOf+12vWC4wIGwahciiR
lDgPOF0v5Dw9H1GOqAMJAMXdt9S5oJlTrW6jdQnY1g+5LzYWVwJXR42ZYSqXm/CV
BMBb6qbNMttpQGZEaLd74/aOOHeVvcYsOVUW4nBpw9GJIlIeQjZjhQ==
-----END RSA PRIVATE KEY-----"""
app.config["PUBLIC_KEY"] = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvD7wildoFUqmzJv+rFby
8HEMAX0qR7DuVZwXSV4gRLkXCV5wIezqCT6/cIw8bBocLOKiY0W1usDvbHDOKZSn
93DV6KBawZiAjgQYR2mGepLaBJOSGrgghWkh79QnxIVGjs8W93vESHuTjoOt/O2+
C/UGVsatAspSxMNithRhBrZkd0Wtn9Vaz8475bFfzeWrvpEsSCbbsVSWw1iVh2uF
HLsf0QtpNY45C89QuVAS5lcgPx3JSodV3Pc+5bjotI5z/1j8o2oWeUOgTeajgDlp
p34IbHbQcd+namTn1kXPWrisl9jgxX0xxQ0DoR4hvoTzdskJoATlWoUoItJbjDjh
hQIDAQAB
-----END PUBLIC KEY-----"""
app.config["ALGORITHMS"] = ["HS256", "RS256"]
app.config["DEFAULT_ALGORITHM"] = "RS256"
setup_assets(app)


def validate_user() -> str:
    return get_user(
        request.cookies.get("access_token", ""),
        app.config["PUBLIC_KEY"],
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
            username,
            app.config["PRIVATE_KEY"],
            algorithm=app.config["DEFAULT_ALGORITHM"],
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
