import cx_Oracle
import json
from datetime import datetime

# Connect to the Oracle database
try:
    conn = cx_Oracle.connect('test/password@//localhost:1521/xe')
except Exception as e:
    print(e)
else:
    print("Connected to Oracle Database:", conn.version)

cur = conn.cursor()

# # Drop the JOB_LIST table if it exists and create it again
# try:
#     # Create the JOB_LIST table
#     sql_create = """
#     CREATE TABLE JOB_LIST(
#         post_id NUMBER(10,0) PRIMARY KEY,
#         company_name VARCHAR2(255) NOT NULL,
#         company_logo VARCHAR2(1000),
#         company_location VARCHAR2(255) NOT NULL,
#         job_posted_date DATE NOT NULL,
#         job_title VARCHAR2(255) NOT NULL,
#         job_type VARCHAR2(15) NOT NULL,
#         job_apply_url VARCHAR2(1000) NOT NULL,
#         job_role VARCHAR2(100) NOT NULL,
#         job_skills CLOB,
#         created_at DATE,
#         about_job VARCHAR(4000)
#     )
#     """

#     cur.execute(sql_create)
#     print("Table created.")

# except Exception as e:
#     print("Error while creating table:", e)

# def insert_job(job):
#     try:
#         sql_insert = """
#         INSERT INTO JOB_LIST(post_id, company_name, company_logo, company_location, job_title, job_posted_date, job_type, job_apply_url, job_role, job_skills)
#         VALUES (:post_id, :company_name, :company_logo, :company_location, :job_title, :job_posted_date, :job_type, :job_apply_url, :job_role, :job_skills)
#         """

#         # Convert job skills to JSON
#         job_skills_json = json.dumps(job["jobSkills"]) if isinstance(job["jobSkills"], list) else job["jobSkills"]

#         cur.execute(sql_insert, {
#             'post_id': job["postId"],
#             'company_name': job["companyName"],
#             'company_logo': job["companyLogo"],
#             'company_location': job["companyLocation"],
#             'job_posted_date': datetime.strptime(job["jobPostedDate"], "%Y-%m-%d"),
#             'job_title': job["jobTitle"],
#             'job_type': job["jobType"],
#             'job_apply_url': job["jobApplyUrl"],
#             'job_role': job["jobRole"],
#             'job_skills': job_skills_json  
#         })

#         conn.commit()

#     except Exception as e:
#         print(f"Inserted job with post_id: {job['postId']}")
#         print("Error inserting job:", e)

# def insert_jobs_from_json(file_path):
#     try:
#         with open(file_path, "r") as file:
#             jobs = json.load(file)
#             for job in jobs:
#                 if job!={}:
#                     insert_job(job)
#     except Exception as e:
#         print("Error reading JSON file:", e)

# insert_jobs_from_json(r"files/ml_jobs.json")

#Adding About job column into Database

with open(r"PythonProject/files/alldailyjobs.json", "r") as file:
    jobs = json.load(file)

    for job in jobs:

        post_id = job.get("jobPostingId")
        about_job_result = job.get("description",{}).get("text","")   #just based on your JSON structure

        about_job=about_job_result if len(about_job_result)<4000 else None
        
        if post_id:
            # Update the about_job for the job with the matching post_id
            sql_update = """
            UPDATE JOB_LIST
            SET about_job = :about_job
            WHERE post_id = :post_id
            """
            cur.execute(sql_update, {
                'about_job': about_job,
                'post_id': post_id
            })
            conn.commit()
            print(f"Updated about_job for post_id: {post_id}")

print("Database update completed successfully.")



cur.close()
conn.close()
