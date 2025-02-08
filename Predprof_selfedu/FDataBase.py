import sqlite3
import math
import time

from flask import request


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()


    def add_item(self, item_name, number, condition, owner):
        try:
            self.__cur.execute("INSERT INTO inventory VALUES(NULL, ?, ?, ?, ?, '-', '-', '-')", (item_name, number, condition, owner))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления предмета в БД " + str(e))
            return False
        return True


    def add_plans(self, item_name, number, cost, provider):
        try:
            self.__cur.execute("INSERT INTO plan VALUES(NULL, ?, ?, ?, ?)", (item_name, number, cost, provider))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления плана в БД " + str(e))
            return False
        return True


    def add_wanted(self, user_id, username, item_name, quantity):
        try:
            self.__cur.execute("INSERT INTO wanted VALUES(NULL, ?, ?, ?, ?, ?)", (user_id, username, item_name, quantity, "Создана"))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления заявки в БД " + str(e))
            return False
        return True


    def add_report(self, username, admin_name, item_name, quantity, status, text):
        try:
            self.__cur.execute("INSERT INTO report VALUES(NULL, ?, ?, ?, ?, ?, ?)", (username, admin_name, item_name, quantity, status, text))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления плана в БД " + str(e))
            return False
        return True


    def add_request_item(self, id_item, username, quantity):
        try:
            self.__cur.execute('UPDATE inventory SET request = ?, status = ?, request_quantity = ? WHERE id = ?', (username, "Cоздана", quantity, id_item))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления заявки в БД " + str(e))
            return False
        return True


    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            self.__cur.execute(f"SELECT COUNT() as `countt` FROM users WHERE name LIKE '{name}'")
            ress = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с такой почтой уже существует")
                return False
            if ress['countt'] > 0:
                print("Пользователь с такой почтой уже существует")
                return False

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, ?)", (name, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД " + str(e))
            return False
        return True


    def delete_item(self, id_item):
        try:
            self.__cur.execute(f'DELETE FROM inventory WHERE id = {id_item}')
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка удаления предмета из БД " + str(e))
            return False
        return True


    def delete_plan(self, id_plan):
        try:
            self.__cur.execute(f'DELETE FROM plan WHERE id = {id_plan}')
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка удаления плана из БД " + str(e))
            return False
        return True


    def delete_report(self, id_report):
        try:
            self.__cur.execute(f'DELETE FROM report WHERE id = {id_report}')
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка удаления отчёта из БД " + str(e))
            return False
        return True


    def delete_wanted(self, id_request):
        try:
            self.__cur.execute(f'DELETE FROM wanted WHERE id = {id_request}')
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка удаления заявки из БД " + str(e))
            return False
        return True


    def edit_item(self, id_item, item_name, number, condition, request_status, owner, request_name, request_quantity):
        try:
            self.__cur.execute('UPDATE inventory SET title = ?, text = ?, condition = ?, owner = ?, request = ?, status = ?, request_quantity = ? WHERE id = ?', (item_name, number, condition, owner, request_name, request_status, request_quantity, id_item))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка редактирования предмета из БД " + str(e))
            return False
        return True


    def edit_status(self, id_request, status):
        try:
            self.__cur.execute('UPDATE wanted SET status = ? WHERE id = ?', (status, id_request))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка изменения статуса заявки из БД " + str(e))
            return False
        return True


    def fix_user_item(self, item_id, username):
        try:
            self.__cur.execute('UPDATE inventory SET owner = ? WHERE id = ?', (username, item_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка редактирования предмета из БД " + str(e))
            return False
        return True


    def get_item(self, item_id):
        try:
            self.__cur.execute(f"SELECT title, text FROM inventory WHERE id = {item_id} LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения предмета из БД " + str(e))

        return (False, False)


    def get_item_name(self, item_id):
        try:
            self.__cur.execute(f"SELECT title FROM inventory WHERE id = {item_id} LIMIT 1")
            res = self.__cur.fetchone()[0]
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения названия предмета из БД " + str(e))

        return (False, False)


    def get_request_quantity(self, item_id):
        try:
            self.__cur.execute(f"SELECT request_quantity FROM inventory WHERE id = {item_id} LIMIT 1")
            res = self.__cur.fetchone()[0]
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения количества предметов из БД " + str(e))

        return (False, False)


    def get_request_name(self, item_id):
        try:
            self.__cur.execute(f"SELECT request FROM inventory WHERE id = {item_id} LIMIT 1")
            res = self.__cur.fetchone()[0]
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения названия предмета из БД " + str(e))

        return (False, False)


    def get_item_quantity(self, item_id):
        try:
            self.__cur.execute(f"SELECT text FROM inventory WHERE id = {item_id} LIMIT 1")
            res = self.__cur.fetchone()[0]
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения названия предмета из БД " + str(e))

        return (False, False)


    def get_report(self, item_id):
        try:
            self.__cur.execute(f"SELECT title, text, condition, owner, request, status, request_quantity FROM inventory WHERE id = {item_id} LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения имени заявителя из БД " + str(e))

        return (False, False)


    def get_username(self, user_id):
        try:
            self.__cur.execute(f"SELECT name FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()[0]
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения имени пользователя из БД " + str(e))

        return (False, False)


    def get_email(self, user_id):
        try:
            self.__cur.execute(f"SELECT email FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()[0]
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения имени пользователя из БД " + str(e))

        return (False, False)


    def getPostsAnonce(self):
        try:
            self.__cur.execute(f"SELECT id, title, text, condition, owner, request, status, request_quantity FROM inventory ORDER BY condition")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения пердмета из БД " + str(e))

        return []


    def get_wanted(self, user_id):
        try:
            self.__cur.execute(f"SELECT id, username, item_name, quantity, status FROM wanted WHERE user_id = '{user_id}'")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения информации о заявке из БД " + str(e))
        return []


    def get_wanted_item_info(self, item_id):
        try:
            self.__cur.execute(f"SELECT id, username, item_name, quantity, status FROM wanted WHERE id = '{item_id}' LIMIT 1")
            res = self.__cur.fetchone()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения информации о заявке из БД " + str(e))
        return []


    def get_admin_requests(self):
        try:
            self.__cur.execute(f"SELECT id, user_id, username, item_name, quantity, status FROM wanted ORDER BY STATUS")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения информации о заявке из БД " + str(e))
        return []


    def getMeAnonce(self, username):
        try:
            self.__cur.execute(f"SELECT id, title, request_quantity, condition, owner, request, status FROM inventory WHERE request = '{username}'")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения предмета из БД " + str(e))

        return []


    def getPlanAnonce(self):
        try:
            self.__cur.execute(f"SELECT id, name, quantity, cost, provider FROM plan ORDER BY provider")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения плана из БД " + str(e))

        return []


    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = '{user_id}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False


    def getAllUsers(self):
        try:
            self.__cur.execute(f"SELECT id, name FROM users ORDER BY name DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения пользователей из БД " + str(e))


    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")

            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД" + str(e))

        return False


    def getMyItems(self, username):
        try:
            self.__cur.execute(f"SELECT id, title, text, condition, owner, request, status FROM inventory WHERE owner = '{username}'")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения предмета из БД " + str(e))

        return []


    def getReportAnonce(self):
        try:
            self.__cur.execute(f"SELECT id, username, admin_name, item_name, quantity, status, text FROM report ORDER BY id")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения отчёта из БД " + str(e))

        return []