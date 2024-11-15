from flask import Flask, jsonify, request
from flask_cors import CORS 
from db_singleton import DatabaseConnection
from datetime import datetime,timedelta
import cx_Oracle
import json
import re
from urllib.parse import unquote

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

db = DatabaseConnection()

def process_text(text):
    if text==None:
        return ""
    bold_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    formatted_text = re.sub(r'\n', r'<br />', bold_text)
    return formatted_text

@app.route('/api/signup', methods=['POST'])
def register():
    data=request.get_json()
    username = data.get('username') 
    password = data.get('password')

    if len(password)<8:
        return jsonify({'message': 'Password should be greater than 8 characters',"success":False}), 200

    try:
        db.cursor.execute("INSERT INTO USERS (username, password) VALUES (:username, :password)",{'username': username, 'password': password})
        db.connection.commit()
        
        return jsonify({'message': 'User registered successfully!',"success":True}), 201
    except cx_Oracle.IntegrityError:
        return jsonify({'message': 'Username already exists!',"success":False}), 200

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    # Extract username and password from request data
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:

        db.cursor.execute("SELECT * FROM USERS WHERE username = :username AND password = :password",
                       {"username": username, "password": password})

        user = db.cursor.fetchone() 

        if user:
            return jsonify({"message": "Login successful", "username": username,"success":True}), 200
        else:
            return jsonify({"message": "Invalid username or password","success":False}), 401

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return jsonify({"error": f"Database error: {error.message}"}), 500

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    page = request.args.get('page', default=1, type=int)
    limit = 50
    offset = (page - 1) * limit

    search=request.args.get('search',"")
    filters_dict = request.args.get('filters', '{}')

    # Initialize filter variables
    job_type = None
    company_name = None
    location = None
    date_posted = None
    job_role = None

    # Attempt to parse filters
    try:
        filter_dict = json.loads(filters_dict)  
        job_type = unquote(filter_dict.get('jobType', ''))
        company_name = unquote(filter_dict.get('companyName', ''))
        location = unquote(filter_dict.get('location', ''))
        date_posted = filter_dict.get('datePosted')  
        job_role = unquote(filter_dict.get('jobRole', ''))
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid filters format"}), 400
    # Count total jobs for pagination
    count_query = "SELECT COUNT(*) FROM JOB_LIST WHERE 1=1"
    count_params = {}

    if job_type:
        count_query += " AND job_type = :job_type"
        count_params['job_type'] = job_type.capitalize()

    if company_name:
        count_query += " AND company_name LIKE :company_name"
        count_params['company_name'] = f"%{company_name}%"

    if location:
        count_query += " AND LOWER(company_location) LIKE LOWER(:location)"
        count_params['location'] = f"%{location}%"

    if date_posted:
        # Calculate the start date based on the filter
        today = datetime.now().date()
        if date_posted == "last-24-hours":
            start_date = today - timedelta(days=1)
        elif date_posted == "last-5-days":
            start_date = today - timedelta(days=5)
        elif date_posted == "last-10-days":
            start_date = today - timedelta(days=10)
        
        count_query += " AND job_posted_date >= :start_date"
        count_params['start_date'] = start_date

    if job_role:
        count_query += " AND job_role = :job_role"
        count_params['job_role'] = job_role

    if search and search!="undefined":
        count_query += " AND (LOWER(job_title) LIKE :search OR LOWER(company_name) LIKE :search)"
        count_params['search'] = f"%{search.lower()}%"

    try:
        db.cursor.execute(count_query, count_params)
        total_count = db.cursor.fetchone()[0]
        total_pages = (total_count + 50 - 1) // 50
    except cx_Oracle.DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    # Fetch job listings
    job_query = "SELECT post_id, company_name, company_logo, company_location, job_title FROM JOB_LIST WHERE 1=1"
    job_params = {}

    if job_type:
        job_query += " AND job_type = :job_type"
        job_params['job_type'] = job_type.capitalize()

    if company_name:
        job_query += " AND company_name LIKE :company_name"
        job_params['company_name'] = f"%{company_name}%"

    if location:
        job_query += " AND LOWER(company_location) LIKE LOWER(:location)"
        job_params['location'] = f"%{location}%"

    if date_posted:
        # Calculate the start date based on the filter
        today = datetime.now().date()
        if date_posted == "last-24-hours":
            start_date = today - timedelta(days=1)
        elif date_posted == "last-5-days":
            start_date = today - timedelta(days=5)
        elif date_posted == "last-10-days":
            start_date = today - timedelta(days=10)
        
        job_query += " AND job_posted_date >= :start_date"
        job_params['start_date'] = start_date


    if job_role:
        job_query += " AND job_role = :job_role"
        job_params['job_role'] = job_role

    if search and search!="undefined":
        job_query += " AND (LOWER(job_title) LIKE :search OR LOWER(company_name) LIKE :search)"
        job_params['search'] = f"%{search.lower()}%"

    job_query += " ORDER BY job_posted_date DESC OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY"
    job_params.update({'offset': offset, 'limit': limit})

    try:
        db.cursor.execute(job_query, job_params)
        jobs = [
            {
                "post_id": row[0],
                "company_name": row[1],
                "company_logo": row[2],
                "company_location": row[3],
                "job_title": row[4],
            }
            for row in db.cursor.fetchall()
        ]   
        return jsonify({
            "jobs": jobs,
            "total_count": total_count, 
            "total_pages": total_pages,   
            "current_page": page          
        })
    except cx_Oracle.DatabaseError as e:
        return jsonify({"error": str(e)}), 500 
    
@app.route('/api/get-filters', methods=["GET"])
def get_filters():
    cursor = db.cursor

    # Fetch top companies ordered by the number of job postings
    companies_query = """
        SELECT company_name, COUNT(*) as job_count
        FROM JOB_LIST
        GROUP BY company_name
        ORDER BY job_count DESC
        FETCH FIRST 10 ROWS ONLY
    """

    # Fetch top locations ordered by the number of job postings
    locations_query = """
        SELECT company_location, COUNT(*) as job_count
        FROM JOB_LIST
        GROUP BY company_location
        ORDER BY job_count DESC
        FETCH FIRST 10 ROWS ONLY
    """

    try:
        # Execute queries for top companies and locations
        cursor.execute(companies_query)
        companies = cursor.fetchall()

        cursor.execute(locations_query)
        locations = cursor.fetchall()

        # Prepare response for companies with job count
        response = {
            "top_companies": [company[0] for company in companies],
            "top_locations": [location[0] for location in locations],
        }

        return jsonify(response)

    except cx_Oracle.DatabaseError as e:
        return jsonify({"error": str(e)}), 500

    
@app.route('/api/jobs/<int:post_id>/<string:username>', methods=['GET'])
def get_job_details(post_id,username):
    query1 = """
    SELECT post_id, company_name, company_logo, company_location, job_posted_date, job_title, job_type, job_apply_url, job_role, job_skills,about_job,applicants
    FROM JOB_LIST
    WHERE post_id = :post_id
    """

    query2="""
    SELECT * FROM APPLICATIONS WHERE username = :username AND post_id = :post_id
    """
    try:
        db.cursor.execute(query1, {"post_id": post_id})
        row = db.cursor.fetchone()

        if len(row) > 9:
            job_skills = row[9].read() if row[9] else "No skills listed"
        else:
            job_skills = "No skills listed"

        if row:
            job_details = {
                "post_id": row[0],
                "company_name": row[1],
                "company_logo": row[2],
                "company_location": row[3],
                "job_posted_date":row[4],
                "job_title": row[5],
                "job_type": row[6],
                "job_apply_url": row[7],
                "job_role": row[8],
                "job_skills":json.loads(job_skills.decode('utf-8') if isinstance(job_skills, bytes) else job_skills),
                "about_job":process_text(row[10]),
                "applicants":row[11]
            }
        else:
            return jsonify({"error": "Job not found"}), 404
    
        db.cursor.execute(query2, {"username": username, "post_id": post_id})
        row = db.cursor.fetchone()

        job_details["isSaved"] = bool(row)  

        return jsonify(job_details), 200
    except cx_Oracle.DatabaseError as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/save/job',methods=["POST"])
def save_job_details():
    data=request.get_json()

    post_id=data.get("postId")
    username=data.get("username")
    date=datetime.now().date()


    query = "INSERT INTO APPLICATIONS (username, post_id, saved_date) VALUES (:username, :post_id, :saved_date)"
    params = {"username": username, "post_id": post_id, "saved_date": date}

    try:
        db.cursor.execute(query,params)
        db.connection.commit()
        
        return jsonify({'message': 'Job saved successfully',"success":True}), 201

    except Exception as e:
        return jsonify({'message': 'Error while saving job',"success":False}), 500

@app.route("/api/saved-jobs/<string:username>",methods=["GET"])
def get_saved_jobs(username):
    query="SELECT * FROM APPLICATIONS WHERE username = :username"
    query = """
        SELECT 
            JOB_LIST.post_id, 
            JOB_LIST.company_name, 
            JOB_LIST.company_logo, 
            JOB_LIST.company_location, 
            JOB_LIST.job_title, 
            APPLICATIONS.saved_date 
        FROM 
            APPLICATIONS 
        JOIN 
            JOB_LIST 
        ON 
            APPLICATIONS.post_id = JOB_LIST.post_id 
        WHERE 
            APPLICATIONS.username = :username
    """
    params = {"username": username}

    try:
        # Execute the JOIN query
        db.cursor.execute(query, params)
        rows = db.cursor.fetchall()

        # Construct the jobs list
        jobs = [
            {
                "post_id": row[0],
                "company_name": row[1],
                "company_logo": row[2],
                "company_location": row[3],
                "job_title": row[4],
                "saved_date": row[5]
            }
            for row in rows
        ]
        
        return jsonify(jobs), 200

    except Exception as e:
        return jsonify({'message': 'Error fetching jobs', "success": False}), 500

if __name__ == '__main__':
    app.run(debug=True)
