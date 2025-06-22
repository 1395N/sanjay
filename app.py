from flask import Flask, render_template, request, redirect, Response
import psycopg2
import os
import csv
import io

app = Flask(__name__)

# ✅ Correct way to get DATABASE_URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

# ✅ Optional fallback for quick local testing (replace with your actual Render DB URL)
if not DATABASE_URL:
    DATABASE_URL = "postgresql://sanjay_iq52_user:iC8iXxvvi5D0tUFE25ejon5dOKgV3w60@dpg-d1bpn4re5dus73erefm0-a.oregon-postgres.render.com/sanjay_iq52"

# ✅ Connect to PostgreSQL with SSL
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

# ✅ Create table if it doesn't exist
cur.execute("""
    CREATE TABLE IF NOT EXISTS applicants (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL
    );
""")
conn.commit()

@app.route('/')
def index():
    return render_template('form.html')  # Make sure form.html exists in 'templates' folder

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']

    cur.execute("INSERT INTO applicants (name, email, phone) VALUES (%s, %s, %s);", (name, email, phone))
    conn.commit()

    return redirect('/success')

@app.route('/success')
def success():
    return "Form submitted successfully! <br><a href='/'>Go back</a>"

@app.route('/data')
def view_data():
    cur.execute("SELECT name, email, phone FROM applicants;")
    rows = cur.fetchall()
    output = "<h2>Submitted Entries</h2><ul>"
    for row in rows:
        output += f"<li>{row[0]} - {row[1]} - {row[2]}</li>"
    output += "</ul><a href='/export'>Download CSV</a>"
    return output

@app.route('/export')
def export_data():
    cur.execute("SELECT name, email, phone FROM applicants;")
    rows = cur.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Email', 'Phone'])
    writer.writerows(rows)

    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=applicants.csv"})

if __name__ == '__main__':
    app.run(debug=True)


