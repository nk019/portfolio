import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'super_secret_key_nikhilesh'  # Change this in production

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS projects 
                 (id INTEGER PRIMARY KEY, title TEXT, description TEXT, stack TEXT, link TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS skills 
                 (id INTEGER PRIMARY KEY, name TEXT, category TEXT)''')
    
    # Check if empty, then populate from RESUME [cite: 1, 15, 11]
    c.execute('SELECT count(*) FROM projects')
    if c.fetchone()[0] == 0:
        # Pre-seeding data from your Resume [cite: 16, 22, 26]
        projects = [
            ("Sales Forecasting w/ Time Series", "Collected multi-year sales data, performed EDA, and trained ARIMA/Prophet models for future predictions.", "Python, Pandas, ARIMA, Prophet", "#"),
            ("Product Length Prediction (Amazon ML)", "Amazon ML Challenge 2023. Engineered TF-IDF encoding and used Keras Neural Networks. Top 252/4000 Rank.", "Deep Learning, NLP, Keras", "#"),
            ("Customer Churn Prediction", "Identified customers likely to leave telecom service using Logistic Regression & Random Forest with 85%+ accuracy.", "Scikit-Learn, Seaborn, SMOTE", "#")
        ]
        c.executemany('INSERT INTO projects (title, description, stack, link) VALUES (?,?,?,?)', projects)

        # Pre-seeding skills [cite: 12, 13, 14]
        skills = [
            ("Python", "Code"), ("Machine Learning", "AI"), ("Deep Learning", "AI"),
            ("SQL", "Data"), ("Data Structures", "CS"), ("Flask/Web", "Dev"),
            ("Linear Algebra", "Math"), ("Probability", "Math")
        ]
        c.executemany('INSERT INTO skills (name, category) VALUES (?,?)', skills)
        
        conn.commit()
        print("Database initialized with Resume Data.")
    
    conn.close()

# --- Routes ---
@app.route('/')
def index():
    conn = sqlite3.connect('portfolio.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    projects = c.execute('SELECT * FROM projects').fetchall()
    skills = c.execute('SELECT * FROM skills').fetchall()
    conn.close()
    
    # Static data from Resume [cite: 1, 6, 31]
    profile = {
        "name": "Nikhilesh Mewara",
        "title": "Data Science & AI Practitioner",
        "about": "B.Tech graduate from MITS Gwalior. Passionate about solving complex problems using Mathematics, Machine Learning, and Python. Ranked Top 2% in JEE Mains and Top 250 in Amazon ML Challenge.",
        "email": "iamnk019@gmail.com",
        "github": "github.com/nk019",
        "linkedin": "linkedin.com/in/nikhilesh-mewara"
    }
    return render_template('index.html', projects=projects, skills=skills, profile=profile)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('portfolio.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if request.method == 'POST':
        if 'add_project' in request.form:
            c.execute('INSERT INTO projects (title, description, stack, link) VALUES (?,?,?,?)',
                      (request.form['title'], request.form['desc'], request.form['stack'], '#'))
        elif 'delete_project' in request.form:
            c.execute('DELETE FROM projects WHERE id = ?', (request.form['id'],))
        elif 'add_skill' in request.form:
            c.execute('INSERT INTO skills (name, category) VALUES (?,?)',
                      (request.form['name'], 'General'))
        elif 'delete_skill' in request.form:
            c.execute('DELETE FROM skills WHERE id = ?', (request.form['id'],))
        conn.commit()
        return redirect(url_for('admin'))

    projects = c.execute('SELECT * FROM projects').fetchall()
    skills = c.execute('SELECT * FROM skills').fetchall()
    conn.close()
    return render_template('admin.html', projects=projects, skills=skills)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == 'admin123': # Simple password
            session['user'] = 'admin'
            return redirect(url_for('admin'))
        else:
            flash("Wrong password!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)