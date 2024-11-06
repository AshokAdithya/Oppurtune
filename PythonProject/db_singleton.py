import cx_Oracle
from datetime import datetime,timedelta
import json
import oracledb

class DatabaseConnection:
    def __init__(self):
        username = 'test'
        password = 'password'
        dsn = 'localhost:1521/xe'
        self.connection = cx_Oracle.connect('test/password@//localhost:1521/xe')
        # self.connection = oracledb.connect(user=username, password=password, host="localhost", port=1521, service_name="xe")
        self.cursor = self.connection.cursor()

    def close(self):
        self.cursor.close()
        self.connection.close()


class DatabaseConnectionFactory:
    @staticmethod
    def create_connection():
        return DatabaseConnection()

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

#Procedure for inserting jobs into the database
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

# with open("files.json","r") as file:
#     content=json.load(file)

# insert_jobs(content,DatabaseConnection())

#Inserting Old jobs which are greater 15 days from posted date
def delete_old_jobs(db):
    try:
        cutoff_date = datetime.now() - timedelta(days=15)
        db.cursor.execute("DELETE FROM JOB_LIST WHERE job_posted_date < :cutoff_date", {'cutoff_date': cutoff_date})
        db.connection.commit()
        print("Old jobs deleted successfully.")
    except Exception as e:
        print("Error deleting old jobs:", e)


# def insert_job(job, db):
#     try:
#         sql_insert = """
#         INSERT INTO JOB_LIST(post_id, company_name, company_logo, company_location, job_title, job_posted_date, job_type, job_apply_url, job_role, job_skills,created_at,about_job)
#         VALUES (:post_id, :company_name, :company_logo, :company_location, :job_title, :job_posted_date, :job_type, :job_apply_url, :job_role, :job_skills,:created_at,:about_job)
#         """

#         job_skills_json = json.dumps(job["jobSkills"]) if isinstance(job["jobSkills"], list) else job["jobSkills"]

#         db.cursor.execute(sql_insert, {
#             'post_id': job["postId"],
#             'company_name': job["companyName"],
#             'company_logo': job["companyLogo"],
#             'company_location': job["companyLocation"],
#             'job_posted_date': datetime.strptime(job["jobPostedDate"], "%Y-%m-%d"),
#             'job_title': job["jobTitle"],
#             'job_type': job["jobType"],
#             'job_apply_url': job["jobApplyUrl"],
#             'job_role': job["jobRole"],
#             'job_skills': job_skills_json,
#             'created_at':datetime.now().date(),
#             'about_job':job["aboutJob"] 
#         })

#         db.connection.commit()
#     except Exception as e:
#         print(f"Error inserting job with post_id: {job['postId']}, Error: {e}")