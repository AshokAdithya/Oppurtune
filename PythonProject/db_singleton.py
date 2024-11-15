import cx_Oracle
from datetime import datetime,timedelta
import json
import cx_Oracle

# CREATE TABLE JOB_LIST(
#     post_id NUMBER(10,0) PRIMARY KEY,
#     company_name VARCHAR2(255) NOT NULL,
#     company_logo VARCHAR2(1000),
#     company_location VARCHAR2(255) NOT NULL,
#     job_posted_date DATE NOT NULL,
#     job_title VARCHAR2(255) NOT NULL,
#     job_type VARCHAR2(15) NOT NULL,
#     job_apply_url VARCHAR2(1000) NOT NULL,
#     job_role VARCHAR2(100) NOT NULL,
#     job_skills CLOB,
#     created_at DATE,
#     about_job VARCHAR(4000)
# )


# CREATE TABLE USERS(
#     user_id NUMBER,
#     username VARCHAR2(255) PRIMARY KEY,
#     password VARCHAR2(255)
# );

# CREATE SEQUENCE user_id_seq
# START WITH 1
# INCREMENT BY 1
# NOCACHE;

# CREATE TABLE APPLICATIONS(
#     username VARCHAR(255),
#     post_id NUMBER(10,0),
#     saved_date DATE,
#     PRIMARY KEY (username,post_id),
#     CONSTRAINT fk_user FOREIGN KEY (username) REFERENCES users(username),
#     CONSTRAINT fk_post_id FOREIGN KEY (post_id) REFERENCES job_list(post_id)
# );

# Procedure for inserting jobs into the database

# CREATE OR REPLACE PROCEDURE insert_job (
#     p_post_id IN JOB_LIST.post_id%TYPE,
#     p_company_name IN JOB_LIST.company_name%TYPE,
#     p_company_logo IN JOB_LIST.company_logo%TYPE,
#     p_company_location IN JOB_LIST.company_location%TYPE,
#     p_job_posted_date IN JOB_LIST.job_posted_date%TYPE,
#     p_job_title IN JOB_LIST.job_title%TYPE,
#     p_job_type IN JOB_LIST.job_type%TYPE,
#     p_job_apply_url IN JOB_LIST.job_apply_url%TYPE,
#     p_job_skills IN JOB_LIST.job_skills%TYPE,
#     p_job_role IN JOB_LIST.job_role%TYPE,
#     p_about_job IN JOB_LIST.about_job%TYPE,
#     p_created_at IN JOB_LIST.created_at%TYPE
# )
# AS
# BEGIN
#     INSERT INTO JOB_LIST (
#         post_id,
#         company_name,
#         company_logo,
#         company_location,
#         job_title,
#         job_posted_date,
#         job_type,
#         job_apply_url,
#         job_role,
#         job_skills,
#         created_at,
#         about_job
#     ) VALUES (
#         p_post_id,
#         p_company_name,
#         p_company_logo,
#         p_company_location,
#         p_job_title,
#         p_job_posted_date,
#         p_job_type,
#         p_job_apply_url,
#         p_job_role,
#         p_job_skills,
#         P_created_at,
#         p_about_job
#     );
#     COMMIT;
# END;
# /

# Trigger

# CREATE OR REPLACE TRIGGER increment_applicants_count
# AFTER INSERT ON applications
# FOR EACH ROW
# BEGIN
#   UPDATE job_list
#   SET applicants = applicants+1
#   WHERE post_id = :NEW.post_id;
# END;
# /

class DatabaseConnection:
    _instance = None  

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            # Call __init__ only once
            cls._instance._is_initialized = False  
        return cls._instance

    def __init__(self):
        if not self._is_initialized:
            username = 'test'
            password = 'password'
            dsn = 'localhost:1521/xe'
            self.pool = cx_Oracle.SessionPool(username, password, dsn, min=2, max=10, increment=1, encoding="UTF-8")
            self.connection = self.pool.acquire()
            self.cursor = self.connection.cursor()
            self._is_initialized = True 

    def close(self):
        self.cursor.close()
        self.pool.release(self.connection)
        self.pool.close()
        DatabaseConnection._instance = None


#For minimizing redundancy
def get_existing_job_ids(db):
    try:
        db.cursor.execute("SELECT post_id FROM JOB_LIST")
        existing_ids = [row[0] for row in db.cursor.fetchall()]
        return set(existing_ids) 
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Oracle Database Error - Retrieving existing job IDs, Error: {error.message}")
        return set()
    except Exception as e:
        print(f"Error retrieving existing job IDs: {e}")
        return set()

#Inserting a new JOB
def call_insert_procedure(job, db):
    try:
        db.cursor.callproc('insert_job', [
            job["postId"],
            job["companyName"],
            job["companyLogo"],
            job["companyLocation"],
            datetime.strptime(job["jobPostedDate"], "%Y-%m-%d"),
            job["jobTitle"],
            job["jobType"],
            job["jobApplyUrl"],
            json.dumps(job["jobSkills"]) if isinstance(job["jobSkills"], list) else job["jobSkills"],
            job["jobRole"],
            job["aboutJob"],
            datetime.now().date()
        ])
        db.connection.commit()
        print(f"Job with post_id {job['postId']} inserted successfully.")
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Oracle Database Error - Insertion failed for post_id {job['postId']}, Error: {error.message}")
    except Exception as e:
        print(f"Error inserting job with post_id {job['postId']}: {e}")

# Inserting all jobs
def insert_jobs(jobs, db):
    for job in jobs:
        if job!={}:
            call_insert_procedure(job, db)


#Inserting Old jobs which are greater 15 days from posted date
def delete_old_jobs(db):
    try:
        cutoff_date = datetime.now() - timedelta(days=15)
        db.cursor.execute("DELETE FROM JOB_LIST WHERE job_posted_date < :cutoff_date", {'cutoff_date': cutoff_date})
        db.connection.commit()
        print("Old jobs deleted successfully.")
    except Exception as e:
        print("Error deleting old jobs:", e)

