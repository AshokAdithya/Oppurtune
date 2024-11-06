from linkedin_api import Linkedin
from datetime import datetime,timedelta
import cx_Oracle
import pickle
import json

# Load the model
with open(r'files/job_role_model.pkl', 'rb') as model_file:
    pipeline = pickle.load(model_file)

def preprocess_text(text):
    with open(r"files/stop_words.json","r") as file:
        stop_words=json.load(file)
    # Convert to lowercase and split into words
    words = text.lower().split()
    
    # Remove stopwords and specific keywords
    words = [word for word in words if word not in stop_words and word != "intern" and word != "internship"]
    return ' '.join(words)

# Define the prediction function
def predict_job_role(job_title):
    title_processed = preprocess_text(job_title)
    job_role = pipeline.predict([title_processed])
    return job_role[0]

# Starting of the program
with open(r"files/credentials.json","r") as file:
    credentials=json.load(file)

def update_date(date):
    timestamp = date

    timestamp_seconds = timestamp / 1000.0

    date_time = datetime.fromtimestamp(timestamp_seconds)

    return date_time.strftime('%Y-%m-%d')

# return skills in the form of list
def skills_to_list(job_id):
    get_job=linkedin.get_job_skills(job_id=job_id)
    skills = [skill['localizedSkillDisplayName'] for skill in get_job['skillMatchStatuses']]
    return skills

#linkedin connection
linkedin=Linkedin(username=credentials["username"],password=credentials["password"],authenticate=True,refresh_cookies=False)

get_jobs_list=linkedin.search_jobs(job_title="internship",industries=["Software Development","IT Services and IT Consulting"],experience=["1"],job_type=["I"],remote=["1","2","3"],listed_at=86400,limit=-1)

print(len(get_jobs_list))
with open(r"files/new_data.json","w") as file:
    json.dump(get_jobs_list,file)

# Database connection
try:
    conn = cx_Oracle.connect('test/password@//localhost:1521/xe')
except Exception as e:
    print(e)
else:
    print("Connected to Oracle Database:", conn.version)

cur = conn.cursor()

cur.execute("SELECT post_id FROM JOB_LIST")
existing_job_ids = {row[0] for row in cur.fetchall()} 

#appending new jobs
all_jobs=[]
all_job_get=[]
with open (r"files/new_data.json","r") as file:
    get_jobs_list=json.load(file)

for job in get_jobs_list:
    job_id = job["entityUrn"].split(":")[-1]

    if(job_id not in existing_job_ids):
        try:
            get_job = linkedin.get_job(job_id=job_id)

            all_job_get.append(get_job)

            # Post ID
            post_id = get_job.get("jobPostingId", None)

            # Get the apply URL
            apply_url = get_job["applyMethod"].get(next(iter(get_job["applyMethod"])), {})

            skills = skills_to_list(job_id)

            workplace_types = get_job.get("workplaceTypes", [])
            workplace_types_resolution_results = get_job.get("workplaceTypesResolutionResults", {})

            # Initialize a dictionary for job details
            job_dict = {}

            # Store values in variables
            company_details = get_job.get("companyDetails", {})
            company_name = company_details.get("com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany", {}).get("companyResolutionResult", {}).get("name")
            
            company_logo = f"{
                company_details
                .get("com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany", {})
                .get("companyResolutionResult", {})
                .get("logo", {})
                .get("image", {})
                .get("com.linkedin.common.VectorImage", {})
                .get("rootUrl", "") +
                company_details
                .get("com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany", {})
                .get("companyResolutionResult", {})
                .get("logo", {})
                .get("image", {})
                .get("com.linkedin.common.VectorImage", {})
                .get("artifacts", [{}])[0]
                .get("fileIdentifyingUrlPathSegment","")
            }"

            company_location = get_job.get("formattedLocation")
            job_posted_date = update_date(get_job.get("listedAt"))
            job_title = get_job.get("title")

            jobType = workplace_types_resolution_results.get(workplace_types[0]) if workplace_types else None

            # Only add to job_dict if values are not None
            if company_name and company_logo and company_location and job_posted_date and job_title and jobType:
                job_dict = {
                    "postId": post_id,
                    "companyName": company_name,
                    "companyLogo": company_logo,
                    "companyLocation": company_location,
                    "jobPostedDate": job_posted_date,
                    "jobTitle": job_title,
                    "jobType": jobType.get("localizedName") if jobType else None,
                    "jobApplyUrl": apply_url.get("companyApplyUrl") or apply_url.get("easyApplyUrl") or f"https://www.linkedin.com/jobs/view/{post_id}/",
                    "jobSkills": skills,
                    "jobRole": predict_job_role(job_title)
                }

            # Use the job_dict as needed, e.g., add to a list or print

            all_jobs.append(job_dict)
        
        except Exception as e:
            print(e)
            
with open(r"files/dailyjobs.json","w") as fil:
    json.dump(all_jobs,fil)

with open(r"files/alldailyjobs.json","w") as f:
    json.dump(all_job_get,f)

def insert_job(job):
    try:
        sql_insert = """
        INSERT INTO JOB_LIST(post_id, company_name, company_logo, company_location, job_title, job_posted_date, job_type, job_apply_url, job_role, job_skills)
        VALUES (:post_id, :company_name, :company_logo, :company_location, :job_title, :job_posted_date, :job_type, :job_apply_url, :job_role, :job_skills)
        """

        # Convert job skills to JSON
        job_skills_json = json.dumps(job["jobSkills"]) if isinstance(job["jobSkills"], list) else job["jobSkills"]

        cur.execute(sql_insert, {
            'post_id': job["postId"],
            'company_name': job["companyName"],
            'company_logo': job["companyLogo"],
            'company_location': job["companyLocation"],
            'job_posted_date': datetime.strptime(job["jobPostedDate"], "%Y-%m-%d"),
            'job_title': job["jobTitle"],
            'job_type': job["jobType"],
            'job_apply_url': job["jobApplyUrl"],
            'job_role': job["jobRole"],
            'job_skills': job_skills_json  
        })

        conn.commit()

    except Exception as e:
        print(f"Inserted job with post_id: {job['postId']}")
        print("Error inserting job:", e)

def insert_jobs_from_json(file_path):
    try:
        with open(file_path, "r") as file:
            jobs = json.load(file)
            for job in jobs:
                if job!={}:
                    insert_job(job)
    except Exception as e:
        print("Error reading JSON file:", e)

insert_jobs_from_json(r"files/dailyjobs.json")

def delete_old_jobs():
    try:
        cutoff_date = datetime.now() - timedelta(days=15)
        cur.execute("DELETE FROM JOB_LIST WHERE job_posted_date < :cutoff_date", {'cutoff_date': cutoff_date})
        conn.commit()
        print("Old jobs deleted successfully.")
    except Exception as e:
        print("Error deleting old jobs:", e)

delete_old_jobs()

cur.close()
conn.close()


