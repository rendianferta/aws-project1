from flask import Flask, render_template, request , flash, redirect, url_for, session
from database import SQL
import datetime


def dictify(data, table):
    if not data:
        return []
    
    result = []
    if table == "Car":
        for id, name, type, capacity, steering, gasoline, price, status, description, image  in data:
            result.append({
                "id" : id,
                "name": name,
                "type": type,   
                "capacity":capacity,
                "steering": steering,
                "gasoline": gasoline,
                "price": price,
                "status" : status,
                "description": description,
                "image" : image
            })
    elif table == "Booking":
        for id, user_id, car_id, start_date, end_date, status in data:
            result.append({
                "id" : id,
                "nama_member": sql.select_id(user_id, "Account")[1], 
                "model_mobil": sql.select_id(car_id, "Car")[1],   
                "tanggal_rental": start_date,
                "tanggal_kembali": end_date,
                "status": status
            })
    elif table == "Account":
        for id, nama, email, password, role  in data:
            result.append({
                "id": id,
                "nama": nama,
                "email" : email,
                "password": password, 
                "role": role
            })
    return result 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aslkfdjsafasafd'

@app.route("/")
def home():
    return render_template("HomePage.html")

@app.route("/search", methods = ["GET", "POST"])
def search():
    data = request.json
    search_query = data.get("query", "").strip()
    result = sql.search_like(search_query, "name", "Car")
    if result:
        flash(f"Founded result!")
        return render_template("Cars.html", cars = dictify(result, "Car"))
    else :
        flash(f"No car '{search_query}' founded")
        return render_template("Cars.html", cars = dictify(sql.search_all("Car"), "Car"))

@app.route("/explore", methods = ["GET", "POST"])
def explore():
    return render_template("Cars.html", cars = dictify(sql.search_all("Car"), "Car"))

@app.route('/rental/<int:car_id>', methods=['GET', 'POST'])
def rental_car(car_id):
    
    selected_car = dictify(sql.select_id(car_id, "Car"), "Car")[0]
    print(selected_car)

    if "user_id" not in session:
        flash("Login First to rent a car")
        return redirect(url_for("detail", car_id = car_id))
    
    if not selected_car:
        return "Car not found Error", 404

    if request.method == 'POST':
        
        if selected_car["status"] == "Available":
            car_id = car_id
            user = session.get('user_id')
            sql.book(user, car_id, datetime.date.today(), datetime.date.today() + datetime.timedelta(days=7), selected_car["price"] * 7, "Waiting Approval")
            flash(f"{selected_car["name"]} rental submission posted, waiting for approval")
            return redirect(url_for("detail", car_id = car_id))
        else:
            flash(f"{selected_car["name"]} is already rented")
            return redirect(url_for("detail", car_id = car_id))
    return "404 error"

@app.route('/detail/<int:car_id>', methods=['GET', 'POST'])
def detail(car_id):
    return render_template("CarDetail.html", car = dictify(sql.select_id(car_id, "Car"), "Car")[0])
    
@app.route("/account")
def account():
    if "user_id" not in session:
        flash("Login first to check account page")
        return redirect(url_for('explore'))

    account = dictify(sql.select_id(session["user_id"], "Account"), "Account")[0]
    if account["role"] == "member":
        rentals = sql.search(session["user_id"], "user_id", "Booking")
        rental_data = []

        for id, user_id, car_id, start_date, end_date, price, status in rentals:
            rental_data.append({
                "id" : id,
                "nama_member": sql.select_id(user_id, "Account")[0][1], 
                "model_mobil": sql.select_id(car_id, "Car")[0][1],   
                "tanggal_rental": start_date,
                "tanggal_kembali": end_date,
                "status": status
            })
        return render_template("Rental_History.html", rentals = rental_data)
    elif account["role"] == "admin":
        rentals = sql.search("Waiting Approval", "status", "Booking")
        rental_data = []
        for id, user_id, car_id, start_date, end_date, price, status in rentals:
            rental_data.append({
                "id" : id,
                "nama_member": sql.select_id(user_id, "Account")[0][1], 
                "model_mobil": sql.select_id(car_id, "Car")[0][1],   
                "tanggal_rental": start_date,
                "tanggal_kembali": end_date,
                "status": status
            })
        return render_template("Rent_Approval.html", rentals = rental_data)

@app.route("/account/accept/<int:rental_id>", methods = ["POST"])
def accept(rental_id):
    sql.update_status("Booking", rental_id, "status", "Approved")
    flash(f"Succesfully approved rental request of {sql.select_id(rental_id, "Booking")[0][1]}")
    return redirect(url_for("account" ))

@app.route("/account/reject/<int:rental_id>'", methods = ["POST"])
def reject(rental_id):
    sql.update_status("Booking", rental_id, "status", "Rejected")
    flash(f"Succesfully rejected rental request of {sql.select_id(rental_id, "Booking")[0][1]}")
    return redirect(url_for("account" ))

@app.route("/logout")
def logout():
    if "user_id" not in session:
        flash("You are not logged in to any account")
        return redirect(url_for("explore"))
    flash("Successfully logged out")
    session.pop("user_id", None)
    return redirect(url_for("explore"))

@app.route("/register", methods = ['GET', "POST"])
def register():
    if request.method == "POST":
        nama = request.form.get("Nama")
        email = request.form.get("Email")
        password1 = request.form.get("Password1")
        password2 = request.form.get("Password2")

        account = sql.search(email, "email", "Account")
        if account:
            flash("Email sudah digunakan", category='error')
        elif len(nama) < 2:
            flash("Nama harus diatas 1 huruf", category='error')
        elif len(email) < 4:
            flash("Email harus diatas 3 huruf", category='error')
        elif len(password1) <3:
            flash("Password harus diatas 2 karakter", category='error') 
        elif password1 != password2:
            flash("Konfirmasi password salah", category='error')
        else:
            sql.register(nama, email, password1, "member")
            session["user_id"] = sql.search(email, "email", "Account")[0][0]
            return redirect(url_for("explore"))

    return render_template("Register.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password=request.form.get("password")

        account = dictify(sql.search(email, "email", "Account"), "Account")
        if account: 
            if password == account[0]["password"]:
                session["user_id"] = account[0]["id"]
                flash(f"Succesfully logged in as {account[0]["nama"]}", category="success")
                return redirect(url_for("explore"))
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            flash("Email tidak terdaftar", category="error")
    return render_template("Login.html")

if __name__ == "__main__":
    sql = SQL()
    app.run()
    session["last_page"] = "HomePage" 

