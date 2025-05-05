from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todolist.db'
db = SQLAlchemy(app)

# Defining the todo model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False, index=True)
    # completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.String(200), nullable=False, index=True)
    status = db.Column(db.String(200), default="Not Started", index=True)

    def __repr__(self):
        return '<Task %r>' % self.id

# Route for sorting and filtering (ORM Method)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        task_due_date = request.form['DueDate']
        new_task = Todo(content=task_content, due_date=task_due_date)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue adding your task"
    
    # Ensure sort_option and filter_option are always assigned
    sort_option = request.args.get('sort', 'date_created')
    filter_option = request.args.get('filter', 'all')

    valid_sort_fields = {
        'date_created': Todo.date_created,
        'due_date': Todo.due_date,
        'status': Todo.status
    }
    sort_field = valid_sort_fields.get(sort_option, Todo.date_created)

    # Filtering Logic
    today = datetime.now().date()
    upcoming_date = today + timedelta(days=7)

    query = Todo.query
    if filter_option == 'upcoming':
        query = query.filter(
            db.func.date(Todo.due_date) <= upcoming_date,
            db.func.date(Todo.due_date) >= today
        )
    elif filter_option == 'completed':
        query = query.filter(Todo.status == 'Complete')
    elif filter_option == 'not_started':
        query = query.filter(Todo.status == 'Not Started')
    elif filter_option == 'in_progress':
        query = query.filter(Todo.status == 'In Progress')

    tasks = query.order_by(sort_field).all()

    return render_template('index.html', tasks=tasks, sort_option=sort_option, filter_option=filter_option)


# Delete Route (Prepared Statement Method)
@app.route('/delete/<int:id>')
def delete(id):
    # task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.execute(
            text("DELETE FROM todo WHERE id = :id"),
            {"id": id}
        )
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting the task'

# Update Route (ORM Method)
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        task.due_date = request.form['DueDate']
        task.status = request.form['Status']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a problem updating the task'
    return render_template('update.html', task=task)


# Daily Leetcode Button (Prepared Statement Method)
@app.route('/add_daily_leetcode', methods=['POST'])
def add_daily_leetcode():
    try:
        db.session.execute(
            text("""
                INSERT INTO todo (content, date_created, due_date, status)
                VALUES ('Daily LeetCode', CURRENT_TIMESTAMP, CURRENT_DATE, 'Not Started')
            """)
        )
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f"There was an issue adding the Daily LeetCode task: {str(e)}"


if __name__ == "__main__":
    app.run(debug=True)
