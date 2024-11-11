from flask import Flask, request, render_template
import psycopg2
from psycopg2 import sql, OperationalError
import urllib.parse

app = Flask(__name__)

EXTERNAL_DATABASE_URL = 'postgresql://ticketing_deb_user:ZWdTZM7geLwxdSmnqmQk0882V2GNvdPO@dpg-csegpcbtq21c738bkjog-a.oregon-postgres.render.com/ticketing_deb'

url = urllib.parse.urlparse(EXTERNAL_DATABASE_URL)

DB_CONFIG = {
    'host': url.hostname,
    'database': url.path[1:],  # Uklonite početni '/'
    'user': url.username,
    'password': url.password,
    'port': url.port or 5432  # Postavite na 5432 ako port nije specificiran
}

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port'],
            sslmode='require'  # Dodajte ovu liniju za SSL
        )
        return conn
    except OperationalError as e:
        print(f"Greška prilikom povezivanja s bazom podataka: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def login():
    message = ''
    is_vulnerable = False  

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_vulnerable = 'vulnerable' in request.form

        conn = get_db_connection()
        if conn is None:
            message = 'Neuspješno povezivanje s bazom podataka.'
            return render_template('login.html', message=message, is_vulnerable=is_vulnerable)

        try:
            with conn:
                with conn.cursor() as cursor:
                    if is_vulnerable:
                        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
                        cursor.execute(query)
                        result = cursor.fetchone()
                        if result:
                            message = 'Uspješno ste prijavljeni! (Ranjivi način)'
                        else:
                            message = 'Neispravno korisničko ime ili lozinka.'
                    else:
                        query = "SELECT * FROM users WHERE username = %s AND password = %s"
                        print(f"Siguran Upit: {query} | Parametri: ({username}, {password})")  # Debug linija
                        cursor.execute(query, (username, password))
                        result = cursor.fetchone()
                        print(f"Rezultat: {result}")  # Debug linija
                        if result:
                            message = 'Uspješno ste prijavljeni! (Siguran način)'
                        else:
                            message = 'Neispravno korisničko ime ili lozinka.'
        except Exception as e:
            message = f'Greška u izvršavanju upita: {e}'
        finally:
            conn.close()

    return render_template('login.html', message=message, is_vulnerable=is_vulnerable)

if __name__ == '__main__':
    app.run(debug=True)
