from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contact.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Contact(db.Model):
    contact_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(250), nullable=False)
    last_name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    phone_number = db.Column(db.String(250), nullable=False)
    image_url = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/all")
def get_all_contacts():
    contacts = db.session.query(Contact).all()
    return jsonify(contacts=[contact.to_dict() for contact in contacts])


@app.route('/search')
def find_contact():
    first_name = request.args.get('name')
    contact = db.session.query(Contact).filter_by(first_name=first_name).first()
    if contact:
        return jsonify(contact.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, you don't have this name in your contacts list"})


def make_bool(val: int) -> bool:
    return bool(int(val))


@app.route('/add', methods=["POST"])
def add_contact():
    new_contact = Contact(
        first_name=request.form.get("first_name"),
        last_name=request.form.get("last_name"),
        email=request.form.get("email"),
        phone_number=request.form.get("phone_number"),
        image_url=request.form.get("image_url")
    )
    db.session.add(new_contact)
    db.session.commit()
    return jsonify(response={"success": "Successfully added your new contact."})


@app.route('/update-contact/<contact_id>', methods=["PATCH"])
def update_number(contact_id):
    new_number = request.args.get("new_number")
    contact = db.session.query(Contact).get(contact_id)
    if contact:
        contact.coffee_price = new_number
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the contact number."}), 200
    else:
        return jsonify(error={"Not found": "Sorry we couldn't find this contact number"}), 404


@app.route('/delete/<contact_id>', methods=["DELETE"])
def delete_contact(contact_id):
    api_key = request.args.get("api-key")
    if api_key == "ContactsAPIKey":
        contact = db.session.query(Contact).get(contact_id)
        if contact:
            db.session.delete(contact)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the contact from the database."}), 200
        else:
            return jsonify(error={"Not found": "Sorry we couldn't this contact"}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=True)

