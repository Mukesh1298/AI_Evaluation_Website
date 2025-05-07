import pymysql
pymysql.install_as_MySQLdb()
from evaluate import evaluate_answer

from flask import Flask, render_template, request, jsonify, redirect, url_for,session
from flask_sqlalchemy import SQLAlchemy
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
from model import get_connection
from mysql.connector import IntegrityError
# Initialize Flask App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/evaluation_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = 'your_secret_key'
# BERT model setup
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1)

@app.route('/')
def home():
    return render_template("landing.html")

@app.route('/teacher')
def teacher():
    return render_template("teacher.html")



@app.route('/add_question', methods=['GET','POST'])
def add_question():
    if request.method == 'POST':
        data = request.get_json()
        question = data['question']
        answer = data['answer']
        marks = data['marks']
        con = get_connection()
        cursor = con.cursor()
        cursor.execute("INSERT INTO questions (question, answer, marks) VALUES (%s, %s, %s)", (question, answer, marks))
        con.commit()
        con.close()
    else:
        return render_template("teacher.html")
    return jsonify({'status': 'success'})
data_student=[]
# Get questions from teacher one by one
@app.route('/get_questions', methods=['GET'])
def get_questions():
    try:
        con = get_connection()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT id, question, marks FROM questions")
        questions = cursor.fetchall()
        con.close()

        print("DEBUG: Returning questions JSON:", questions)
        return jsonify(questions)

    except Exception as e:
        print("ERROR in /get_questions:", e)
        return jsonify({'error': 'Server error', 'message': str(e)}), 500


@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    data = request.json
    con = get_connection()
    cursor = con.cursor(dictionary=True)

    # Get correct answer and marks from DB
    cursor.execute("SELECT answer, marks FROM questions WHERE id = %s", (data['question_id'],))
    question = cursor.fetchone()
    correct_answer = question['answer']
    teacher_marks = question['marks']

    # **Evaluate the answer using BERT-based evaluation**
    similarity_score = float(evaluate_answer(data['answer'], correct_answer))
    
    # Use the similarity score to calculate the student marks based on the teacher's max marks
    student_marks = (similarity_score * teacher_marks)/10 # Normalize the score back into the range of teacher_marks

    # Store the student's answer and calculated marks
    cursor.execute(
        "INSERT INTO student_answers (question_id, student_answer, marks) VALUES (%s, %s, %s)",
        (data['question_id'], data['answer'], round(student_marks,1))
    )

    con.commit()
    con.close()
    data_student.append(student_marks)
    return jsonify({'marks': round(student_marks,1)})


total_student_marks=0
def calculate_total_student_marks():
    # You must already have a way to compute `data_student` list
    # Example: data_student = [5, 3, 2] from evaluation system
    total = sum(data_student)  # You must ensure data_student is defined before this is called
    return round(total, 0)


@app.route('/get_result', methods=['GET'])
def get_result():
    con = get_connection()
    cursor = con.cursor()

    # Get the total marks the teacher provided (from the questions)
    cursor.execute("SELECT SUM(marks) FROM questions")
    total_teacher_marks = cursor.fetchone()[0] or 0
    con.close()
    
    # con.close()
    total_student_marks = calculate_total_student_marks()
    
    return jsonify({
        'total_teacher_marks': round(total_teacher_marks, 2),
        'total_student_marks': round(total_student_marks, 0)
    })

 #retrive student data
@app.route('/studentdatabase', methods=['POST'])
def studentdatabase():
    data = request.get_json()
    id = data['sid']
    name = data['sname']
    
    total_student_marks = calculate_total_student_marks()
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    # Check if student already exists
    cursor.execute("SELECT * FROM studentdatabase WHERE student_id = %s", (id,))
    existing_student = cursor.fetchone()

    if existing_student:
        con.close()
        return jsonify({'message': 'Student with this ID already exists'}), 409  # 409 Conflict
    # Insert if not duplicate

    
    cursor.execute("""
        INSERT INTO studentdatabase (student_id, student_name, student_marks)
        VALUES (%s, %s, %s)
    """, (id, name, total_student_marks))

    con.commit()
    con.close()

    return jsonify({'message': 'Student added to database'})



#handleQuestions panel

@app.route('/studentData')
def student_pageData():
    return render_template("handleq.html")

@app.route('/api/questions', methods=['GET'])
def get_questionsH():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM questions")
    data = cur.fetchall()
    cur.close()
    questions = [{'id': row[0], 'question': row[1], 'answer': row[2]} for row in data]
    return jsonify(questions)

@app.route('/api/questions', methods=['POST'])
def add_questionH():
    data = request.get_json()
    question = data['question']
    answer = data['answer']
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO questions (question, answer) VALUES (%s, %s)", (question, answer))
    con.commit()
    cur.close()
    return jsonify({'status': 'success'})

@app.route('/api/questions/<int:id>', methods=['PUT'])
def update_questionH(id):
    data = request.get_json()
    question = data['question']
    answer = data['answer']
    con = get_connection()
    cur = con.cursor()
    cur.execute("UPDATE questions SET question=%s, answer=%s WHERE id=%s", (question, answer, id))
    con.commit()
    cur.close()
    return jsonify({'status': 'updated'})

@app.route('/api/questions/<int:id>', methods=['DELETE'])
def delete_questionH(id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM questions WHERE id=%s", (id,))
    con.commit()
    cur.close()
    return jsonify({'status': 'deleted'})


#singhup and login for admin to teacher
@app.route('/adminlogin')
def adminhome():
    return render_template('adminlogin.html')


@app.route('/login', methods=['POST'])
def adminlogin():
    if request.is_json:
        data = request.get_json()
        username = data['username']
        password = data['password']
    else:
        username = request.form['username']
        password = request.form['password']
        
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
    admin = cursor.fetchone()
    
    if admin:
        session['admin'] = admin['username']
        if request.is_json:
            return jsonify({'success': True})
        return redirect(url_for('dashboard'))

    if request.is_json:
        return jsonify({'success': False})
    return "Login Failed"


@app.route('/teachersinghup')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('adminhome'))
    return render_template('admin-dashboard.html')

@app.route('/teacherenter')
def teacherenter():
    return render_template("teachersinghup.html")
   

@app.route('/add_teacher', methods=['POST'])
def add_teacher():
    if 'admin' not in session:
        return redirect(url_for('adminhome'))
    
    tid = request.form['tid']
    tuser = request.form['tuser']
    tpass = request.form['tpass']
    subject = request.form['subject']
    
    con = get_connection()
    cursor = con.cursor()

    try:
        cursor.execute("INSERT INTO teacher (id, username, password, subject) VALUES (%s, %s, %s, %s)", 
                       (tid, tuser, tpass, subject))
        con.commit()
        return render_template("landing.html")  # Success page
    except IntegrityError as e:
        if "1062" in str(e):
            # Duplicate key error
            return render_template("teachersinghup.html", error="Duplicate entry found. Please use a unique ID or username.")
        else:
            return "Database error occurred", 500


# code for adding student by teachers


@app.route('/studentlogin', methods=['GET', 'POST'])
def studentlogin():
    if request.method == 'POST':
        tid = request.form['tid']
        tuser = request.form['tuser']
        tpass = request.form['tpass']
        subject = request.form['subject']
        
        con = get_connection()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM teacher WHERE id=%s AND username=%s AND password=%s AND subject=%s",
                       (tid, tuser, tpass, subject))
        teacher = cursor.fetchone()
        con.close()

        if teacher:
            session['teacher'] = teacher['username']
            return redirect(url_for('teacher_panel'))
        
    
        return "Login Failed. Please check your credentials."

    return render_template('teacherlogin.html')



@app.route('/add_student', methods=['GET','POST'])
def add_student():
    if request.method =='POST':
        data = request.get_json()
        student_id = data['studentId']
        student_name = data['studentName']
        student_username = data['studentUsername']
        student_password = data['studentPassword']

        con = get_connection()
        cur=con.cursor()
        cur.execute("INSERT INTO student_info (student_id, student_name, student_username, student_pass) VALUES (%s, %s, %s, %s)",
                (student_id, student_name, student_username, student_password))
        con.commit()
        cur.close()

        return jsonify({"message": "Student added successfully!"}), 200
    return render_template("studentsinghup.html")



@app.route('/teacherpanel')
def teacher_panel():
    if 'teacher' not in session:
        return redirect(url_for('studentlogin'))
    return render_template('teacherpanel.html')  # This is your custom teacher panel

@app.route('/logout')
def logout():
    session.pop('teacher', None)
    return redirect(url_for('studentlogin'))

#student login and take quiz
@app.route('/student_register',methods =['GET','POST'])
def student_register():
    if request.method == 'POST':
        data = request.get_json()
        id = data['sid']
        name = data['sname']
        username = data['susername']
        password = data['spassword']
        
        con = get_connection()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student_info WHERE student_id=%s AND student_name=%s AND student_username=%s AND student_pass=%s",
                       (id, name, username, password))
        
        
        student = cursor.fetchone()
        con.close()

        if student:
            session['student'] = student['student_username']
            return jsonify({'message': 'Registration successful'}) 


        return jsonify({'message': 'Invalid credentials or user not found'})
       

    return render_template('studentlogin.html')

@app.route('/student')
def student_page():
     if 'student' not in session:
         return redirect(url_for('student_register'))
     return render_template("student.html")



@app.route('/students')
def show_students():
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM studentdatabase")
    students = cursor.fetchall()
    con.close()
    return render_template('studentdata.html', students=students)

@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("DELETE FROM studentdatabase WHERE student_id = %s", (student_id,))
    con.commit()
    con.close()
    return redirect(url_for('show_students'))


#handlestudent database

@app.route('/studentDataManage')
def student_pageDataManage():
    return render_template("studentdatamanage.html")

@app.route('/api/studentManage', methods=['GET'])
def get_studentsDataManage():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM student_info")  # Query for the student_info table
    data = cur.fetchall()
    cur.close()
    students = [{'student_id': row[0], 'student_name': row[1], 'student_username': row[2], 'student_pass': row[3]} for row in data]
    return jsonify(students)

@app.route('/api/studentManage', methods=['POST'])
def add_studentDataManage():
    data = request.get_json()
    student_name = data['student_name']
    student_username = data['student_username']
    student_pass = data['student_pass']
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO student_info (student_name, student_username, student_pass) VALUES (%s, %s, %s)", 
                (student_name, student_username, student_pass))
    con.commit()
    cur.close()
    return jsonify({'status': 'success'})

@app.route('/api/studentManage/<int:id>', methods=['PUT'])
def update_studentDataManage(id):
    data = request.get_json()
    student_name = data['student_name']
    student_username = data['student_username']
    student_pass = data['student_pass']
    con = get_connection()
    cur = con.cursor()
    cur.execute("UPDATE student_info SET student_name=%s, student_username=%s, student_pass=%s WHERE student_id=%s", 
                (student_name, student_username, student_pass, id))
    con.commit()
    cur.close()
    return jsonify({'status': 'updated'})

@app.route('/api/studentManage/<int:id>', methods=['DELETE'])
def delete_studentDataManage(id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM student_info WHERE student_id=%s", (id,))
    con.commit()
    cur.close()
    return jsonify({'status': 'deleted'})


#handle teacher database
@app.route('/teacherDataManage')
def teacher_pageDataManage():
    return render_template("teacherdatamanage.html")

@app.route('/api/teacherManage', methods=['GET'])
def get_teachersDataManage():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM teacher")  # Assuming table name is `teacher`
    data = cur.fetchall()
    cur.close()
    teachers = [{'id': row[0], 'username': row[1], 'password': row[2], 'subject': row[3]} for row in data]
    return jsonify(teachers)

@app.route('/api/teacherManage', methods=['POST'])
def add_teacherDataManage():
    data = request.get_json()
    username = data['username']
    password = data['password']
    subject = data['subject']
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO teacher (username, password, subject) VALUES (%s, %s, %s)", 
                (username, password, subject))
    con.commit()
    cur.close()
    return jsonify({'status': 'success'})

@app.route('/api/teacherManage/<int:id>', methods=['PUT'])
def update_teacherDataManage(id):
    data = request.get_json()
    username = data['username']
    password = data['password']
    subject = data['subject']
    con = get_connection()
    cur = con.cursor()
    cur.execute("UPDATE teacher SET username=%s, password=%s, subject=%s WHERE id=%s", 
                (username, password, subject, id))
    con.commit()
    cur.close()
    return jsonify({'status': 'updated'})

@app.route('/api/teacherManage/<int:id>', methods=['DELETE'])
def delete_teacherDataManage(id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM teacher WHERE id=%s", (id,))
    con.commit()
    cur.close()
    return jsonify({'status': 'deleted'})


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
