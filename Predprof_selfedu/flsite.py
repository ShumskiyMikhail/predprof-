import sqlite3
import os
from tkinter.font import names

from flask import Flask, render_template, request, flash, redirect, session, url_for, abort, g
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin


DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
EMAIL = "111@111"
now_email = ""
now_role = -1




app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, "flsite.db")))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"






@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, "link_db"):
        g.link_db = connect_db()
    return g.link_db



dbase = None
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


def check_role():
    global now_role, EMAIL
    now_email = dbase.get_email(current_user.get_id())
    if now_email == EMAIL:
        now_role =  1
    else:
        now_role = 0



@app.route("/auth", methods=["POST", "GET"])
def login():
    global now_email, now_role, EMAIL
    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            now_email = request.form['email']
            if now_email == EMAIL:
                now_role = 1
            else:
                now_role = 0
            return redirect(request.args.get("next") or url_for("all_items"))

        flash("Неверная пара логин/пароль", "error")

    return render_template("auth.html", title="Авторизация")


@app.route("/reg", methods=["POST", "GET"])
def reg():
    global now_role, now_email, EMAIL
    if request.method == "POST":
        session.pop('_flashes', None)
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                if request.form['email'] == EMAIL:
                    now_role = 1
                else:
                    now_role = 0
                now_email = request.form['email']
                return redirect("/auth")
            else:
                flash("Аккаунт с такой почтой/логином уже существует", "error")
        else:
            flash("Неверно заполнены поля", "error")
            if len(request.form['name']) < 4:
                flash("Имя должно содержать не менее 4 символов", "error")
            if request.form['psw'] != request.form['psw2']:
                flash("Пароли должны совпадать", "error")
            if len(request.form['psw']) < 4:
                flash("Пароль должен содержать не менее 4 символов", "error")

    return render_template("reg.html", title="Регистрация")


@app.route('/logout')
@login_required
def logout():
    global now_role, now_email
    now_role = -1
    now_email = ""
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect("/index")


@app.route('/profile')
@login_required
def profile():
    check_role()
    username = dbase.get_username(current_user.get_id())
    now_email = dbase.get_email(current_user.get_id())
    if now_role == 1:
        return render_template('profile.html', title="Профиль", id=current_user.get_id(), role2="Администратор", username=username, email=now_email, role=now_role)
    else:
        return render_template('profile.html', title="Профиль", id=current_user.get_id(), role2="Пользователь", username=username, email=now_email, role=now_role)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "link_db"):
        g.link_db.close()


@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    global  now_role
    return render_template('index.html', title="Home page", role=now_role)


@app.route("/add_item", methods=["POST", "GET"])
@login_required
def add_item():
    check_role()
    if now_role == 0:
        flash("У вас нет прав доступа к этой функции.")
        return redirect("/index")
    if request.method == "POST":
        if len(request.form["name"]) >= 2 and int(request.form["quantity"]) > 0:
            email =  dbase.get_username(current_user.get_id())
            res = dbase.add_item(request.form["name"], request.form["quantity"], request.form["drone"], email)
            if not res:
                flash("Ошибка добавления предмета")
            else:
                flash('Успешное добаление предмета')
                return redirect("/all_items")
        else:
            flash("Ошибка добавления предмета")
            if len(request.form["name"]) < 2:
                flash("Название предмета должно содержать больше двух символов")
            if int(request.form["quantity"]) <= 0:
                flash("Количество предметов должно быть положительным")
    return render_template("add_item.html", title="Добавление предметов", role=now_role)


@app.route("/add_plan", methods=["POST", "GET"])
@login_required
def add_plan():
    check_role()
    if now_role == 0:
        flash("У вас нет прав доступа к этой вкладке.")
        return redirect("/index")
    if request.method == "POST":
        if len(request.form["name"]) >= 2 and int(request.form["quantity"]) > 0 and int(request.form["cost"]) > 0 and len(request.form["provider"]) >= 2:
            res = dbase.add_plans(request.form["name"], request.form["quantity"], request.form["cost"], request.form["provider"])
            if not res:
                flash("Ошибка добавления предмета")
            else:
                flash('Успешное добаление предмета')
                return redirect("/plans")
        else:
            flash("Ошибка добавления предмета")
            if len(request.form["name"]) < 2:
                flash("Название предмета должно содержать больше двух символов")
            if int(request.form["quantity"]) <= 0:
                flash("Количество предметов должно быть положительным")
            if int(request.form["cost"]) <= 0:
                flash("Стоимость предмета должна быть положительной")
            if len(request.form["name"]) < 2:
                flash("Имя поставщика должно содержать больше двух символов")
    return render_template('add_plan.html',  title="Добавить план закупки", role=now_role)


@app.route("/all_items/<int:id_item>/request", methods=["POST", "GET"])
@login_required
def request_item(id_item):
    check_role()
    if now_role == 1:
        flash("Заявку может создать только обычный пользователь.")
        return redirect("/all_items")
    if len(dbase.get_request_name(id_item)) > 3:
        flash("Этот предмет уже кто-то добавил в свою заявку")
        return redirect("/all_items")
    if request.method == "POST":
        if int(request.form["quantity"]) > int(dbase.get_item_quantity(id_item)):
            flash('У нас нету столько предметов такого типа')
            return redirect("/all_items")
        if int(request.form["quantity"]) <= 0:
            flash('Количество предметов не может быть меньше 1')
            return redirect("/all_items")
        if int(request.form["quantity"]) > 0:
            res = dbase.add_request_item(id_item, dbase.get_username(current_user.get_id()), request.form["quantity"])
            if not res:
                flash("Ошибка добавления заявки")
            else:
                flash('Успешное добаление заявки')
                return redirect("/all_items")
    return render_template('request.html', item_name=dbase.get_item_name(id_item), item_quantity=dbase.get_item_quantity(id_item), title="Подать заявку", id_item=id_item, role=now_role)



@app.route("/all_items")
@login_required
def all_items():
    check_role()
    return render_template('all_items.html', title="Список предметов", inventory=dbase.getPostsAnonce(), role=now_role, user_id=current_user.get_id())


@app.route("/all_items/<int:id_item>/delete")
@login_required
def delete(id_item):
    res = dbase.delete_item(id_item)
    if not res:
        flash("Ошибка удаления предмета")
    else:
        flash('Успешное удаление предмета')
        return redirect("/all_items")



@app.route("/all_items/<int:id_item>/edit", methods=["POST", "GET"])
@login_required
def edit_item(id_item):
    check_role()
    if now_role == 0:
        flash("У вас нет прав доступа к этой функции.")
        return redirect("/index")
    item_name = dbase.get_item_name(id_item)
    item_quantity = dbase.get_item_quantity(id_item)
    request_name = dbase.get_request_name(id_item)
    if request.method == "POST":
        if len(request.form["namik"]) > 3 and int(request.form["postik"]) > 0:
            n = dbase.get_username(current_user.get_id())
            if request.form["drone2"] == "Отклонена":
                res = dbase.edit_item(id_item, request.form["namik"], request.form["postik"], request.form["drone"], request.form["drone2"], n, request_name, "-")
            else:
                res = dbase.edit_item(id_item, request.form["namik"], request.form["postik"], request.form["drone"], request.form["drone2"], n, dbase.get_request_name(id_item), dbase.get_request_quantity(id_item))
            if not res:
                flash("Ошибка редактирования предмета")
            else:
                flash('Успешное редактирование предмета')
                return redirect("/all_items")
        else:
            flash("Ошибка редактирования предмета")

    return render_template("edit_item.html", title="Редактирование предметов", id_item=id_item, item_name=item_name, item_quantity=item_quantity, role=now_role)


@app.route("/all_items/<int:id_item>/fix_user")
@login_required
def fix_user(id_item):
    check_role()
    return render_template("fix_user.html", id_item=id_item, all_users=dbase.getAllUsers(), role=now_role)


@app.route("/all_items/<int:id_item>/<int:id_user>/fix")
@login_required
def fix(id_item, id_user):
    res = dbase.fix_user_item(id_item, dbase.get_username(id_user))
    if not res:
        flash("Ошибка закрепления предмета")
        return redirect("/all_items")
    else:
        flash('Успешное закрепление предмета')
        return redirect("/all_items")


@app.route("/my_requests")
@login_required
def my_requests():
    check_role()
    if now_role != 0:
        flash("У вас нет прав доступа к этой вкладке.")
        return redirect("/index")
    name = dbase.get_username(current_user.get_id())
    return render_template('my_requests.html', role=now_role, title="Мои заявки", inventory=dbase.getMeAnonce(name), name=name)


@app.route("/plans")
@login_required
def plans():
    check_role()
    if now_role == 0:
        flash("У вас нет прав доступа к этой вкладке.")
        return redirect("/index")
    return render_template('plans.html',  title="План закупок", role=now_role, plan=dbase.getPlanAnonce())


@app.route("/plans/<int:id_plan>/delete_plan")
@login_required
def delete_plan(id_plan):
    res = dbase.delete_plan(id_plan)
    if not res:
        flash("Ошибка удаления плана")
    else:
        flash('Успешное удаление плана')
        return redirect("/plans")


@app.route("/my_items")
@login_required
def my_items():
    name = dbase.get_username(current_user.get_id())
    return render_template('my_items.html', role=now_role, title="Мои предметы", inventory=dbase.getMyItems(name), name=name)


@app.route("/add_report/<int:id_item>", methods=["POST", "GET"])
@login_required
def add_report(id_item):
    item_info = dbase.get_report(id_item)
    if request.method == "POST":
        if len(request.form["report_text"]) > 5:
            res = dbase.add_report(item_info[4], item_info[3], item_info[0], item_info[1], request.form["report_text"], request.form["status"])
            if not res:
                flash("Ошибка добавления отчёта")
            else:
                flash('Успешное добаление отчёта')
                return redirect("/report")
        else:
            flash("Ошибка добавления отчёта")
            if len(request.form["name"]) < 6:
                flash("Текст отчёта должен содержать больше двух символов")
    return render_template('add_report.html', id_item=id_item, title="Добавление отчёта", role=now_role, owner=item_info[3], request=item_info[4], item_name=item_info[0], quantity=item_info[1])



@app.route("/report")
@login_required
def report():
    check_role()
    return render_template('report.html', title="Отчёты", role=now_role, report=dbase.getReportAnonce())



@app.route("/report/<int:id_item>/delete_report")
@login_required
def delete_report(id_item):
    res = dbase.delete_report(id_item)
    if not res:
        flash("Ошибка удаления отчёта")
    else:
        flash('Успешное удаление отчёта')
        return redirect("/report")


@app.route("/my_add_requests")
@login_required
def my_add_requests():
    check_role()
    return render_template('my_add_requests.html', title="Заявки на добавление", role=now_role, add_requests=dbase.get_wanted(current_user.get_id()))


@app.route("/add_wanted", methods=["POST", "GET"])
@login_required
def add_wanted():
    check_role()
    if now_role == 1:
        flash("У вас нет прав доступа к этой вкладке.")
        return redirect("/index")
    if request.method == "POST":
        if len(request.form["name"]) >= 2 and int(request.form["quantity"]) > 0:
            res = dbase.add_wanted(current_user.get_id(), dbase.get_username(current_user.get_id()), request.form["name"], request.form["quantity"])
            if not res:
                flash("Ошибка добавления заявки")
            else:
                flash('Успешное добаление заявки')
                return redirect("/my_add_requests")
        else:
            flash("Ошибка добавления заявки")
            if len(request.form["name"]) < 2:
                flash("Название предмета должно содержать больше двух символов")
            if int(request.form["quantity"]) <= 0:
                flash("Количество предметов должно быть положительным")
    return render_template('add_wanted.html',  title="Добавить заявку на добавление предмета", role=now_role)



@app.route("/my_add_requests/<int:id_request>/delete")
@login_required
def delete_wanted(id_request):
    res = dbase.delete_wanted(id_request)
    if not res:
        flash("Ошибка удаления заявки")
    else:
        flash('Успешное удаление заявки')
        return redirect("/my_add_requests")


@app.route("/admin_requests")
@login_required
def admin_requests():
    check_role()
    return render_template('admin_requests.html', title="Полученные заявки", role=now_role, admin_requests=dbase.get_admin_requests())


@app.route("/admin_requests/<int:id_request>/edit_request", methods=["POST", "GET"])
@login_required
def edit_request_status(id_request):
    check_role()
    if now_role == 0:
        flash("У вас нет прав доступа к этой функции.")
        return redirect("/index")
    item_info = dbase.get_wanted_item_info(id_request)
    print(*item_info)
    request_username = item_info[1]
    item_name = item_info[2]
    item_quantity = item_info[3]
    print(request.method)
    if request.method == "POST":
        res = dbase.edit_status(id_request, request.form["status"])
        if not res:
            flash("Ошибка изменения статуса заявки")
            return redirect("/admin_requests")
        else:
            if request.form["status"] == "Одобрена":
                rest = dbase.add_item(item_name, item_quantity, "Новый", dbase.get_username(current_user.get_id())) #request_username
                if not rest:
                    flash("Ошибка добавления заявки")
                else:
                    flash("Успешное изменеие статуса заявки")
                    flash("Предмет успешно добавлен в общий список")
                    return redirect("/admin_requests")
            if res:
                flash('Успешное изменение статуса заявки')
                return redirect("/admin_requests")
            else:
                flash('Ошибка изменения статуса заявки')
    return render_template("edit_status.html", title="Изменение статуса заявки", item_name=item_name, item_quantity=item_quantity, request_username=request_username, role=now_role, id_request=id_request)



if __name__ == "__main__":
    app.run(debug=True)