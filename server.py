from flask import Flask, render_template, request, redirect, url_for
import csv
import re

app = Flask(__name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@app.route("/")
def homepage():
    return render_template("index.html")


@app.route("/<string:page_name>")
def html_page(page_name):
    # e.g., /contact.html loads templates/contact.html
    return render_template(page_name)


def write_to_csv(data):
    with open("database.csv", mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",", quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerow([data["email"], data["subject"], data["message"]])


def validate(form):
    """Return (is_valid, errors_dict)."""
    email = (form.get("email") or "").strip()
    subject = (form.get("subject") or "").strip()
    message = (form.get("message") or "").strip()

    errors = {}
    if not email:
        errors["email"] = "Email is required."
    elif not EMAIL_RE.match(email):
        errors["email"] = "Please enter a valid email address."

    if not subject:
        errors["subject"] = "Subject is required."
    elif len(subject) > 200:
        errors["subject"] = "Subject must be 200 characters or fewer."

    if not message:
        errors["message"] = "Message is required."
    elif len(message) > 5000:
        errors["message"] = "Message must be 5000 characters or fewer."

    cleaned = {"email": email, "subject": subject, "message": message}
    return (len(errors) == 0, errors, cleaned)


@app.route("/submit_form", methods=["POST"])
def submit_form():
    is_valid, errors, cleaned = validate(request.form)
    if not is_valid:
        # Re-render the contact page with errors and the previous input
        return render_template("contact.html", errors=errors, form=cleaned), 400

    try:
        write_to_csv(cleaned)
        return redirect(url_for("html_page", page_name="thankyou.html"))
    except Exception as e:
        # Log e in real apps
        return render_template("contact.html",
                               errors={
                                   "__all__": "Could not save your submission. Please try again."},
                               form=cleaned), 500

# $env:FLASK_APP = "server.py"
# $env:FLASK_DEBUG = "1"
# python -m flask run
