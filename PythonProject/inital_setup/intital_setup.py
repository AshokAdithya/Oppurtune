import json
import csv
from linkedin_api import Linkedin
from datetime import datetime

# For getting time as it is in count of milli seconds
def update_date(date):
    timestamp = date

    timestamp_seconds = timestamp / 1000.0

    date_time = datetime.fromtimestamp(timestamp_seconds)

    return date_time.strftime('%Y-%m-%d %H:%M:%S') # Need to converted into Date only instead of Date & Time

# return skills in the form of list
def skills_to_list(job_id):
    get_job=linkedin.get_job_skills(job_id=job_id)
    skills = [skill['localizedSkillDisplayName'] for skill in get_job['skillMatchStatuses']]
    return skills

# getting credentials from json file
with open(r"files/credentials.json","r") as file:
    contents=json.load(file)

# Logging in using API
linkedin=Linkedin(username=contents["username"],password=contents["password"],authenticate=True,refresh_cookies=False)

get_jobs_list=linkedin.search_jobs(job_title="internship",industries=["Software Development","IT Services and IT Consulting"],experience=["1"],job_type=["I"],remote=["1","2","3"],listed_at=15*86400,limit=-1)

#Dumping all jobs
with open(r"files/data.json","w") as fil:
    json.dump(get_jobs_list,fil)

all_jobs=[]
all_job_get=[]

with open (r"files/data.json","r") as fi:
    get_jobs_list=json.load(fi)

for jobs in get_jobs_list:
    try:
        job_id = jobs["entityUrn"].split(":")[-1]

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
                "jobSkills": skills
            }

        # Use the job_dict as needed, e.g., add to a list or print

        all_jobs.append(job_dict)
    
    except Exception as e:
        print(e)
        

with open(r"files/jobs.json","w") as fil:
    json.dump(all_jobs,fil)

with open(r"files/alljobs.json","w") as f:
    json.dump(all_job_get,f)
'''---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''


# Getting Data for ML
# def classify_job_role(job_title):
#     title_lower = job_title.lower()
#     if "software" in title_lower or "developer" in title_lower or "sde" in title_lower or "sre" in title_lower or "platform" in title_lower or "app" in title_lower:
#         return "Software Development"
#     elif "cyber" in title_lower or "security" in title_lower:
#         return "Cyber Security"
#     elif "data" in title_lower or "analyst" in title_lower or "science" in title_lower  or "analytics" in title_lower:
#         return "Data Analysis"
#     elif "front" in title_lower or "back" in title_lower or "web" in title_lower or "full" in title_lower or "stack" in title_lower or "ui" in title_lower or "ux" in title_lower or "node"in title_lower  :
#         return "Web development"
#     elif "seo" in title_lower:
#         return "SEO Specialist"
#     elif "devops" in title_lower:
#         return "DevOps Development"
#     elif "marketing" in title_lower:
#         return "Marketing"
#     elif "operations" in title_lower:
#         return "Operations"
#     elif "business" in title_lower or "strategy" in title_lower or "consultant" in title_lower:
#         return "Business Development"
#     elif "sales" in title_lower:
#         return "Sales"
#     elif "human resource" in title_lower or "talent acquisition" in title_lower:
#         return "Human Resources"
#     elif "graphic" in title_lower or "designer" in title_lower:
#         return "Graphic Design"
#     elif "content" in title_lower or "copywriter" in title_lower or "writer" in title_lower or "video" in title_lower:
#         return "Content Creation"
#     elif "finance" in title_lower or "financial" in title_lower or "accountant" in title_lower:
#         return "Finance"
#     elif "intern" in title_lower:
#         return "General Internship"
#     else:
#         return "Other"

# with open(r"files/allnjobs.json","r") as f:
#     content=json.load(f)

# # Prepare data and write to CSV
# csv_data = [("Job Title", "Role")]
# for job_id, job_title in content.items():
#     role = classify_job_role(job_title)
#     csv_data.append(( job_title, role))

# # Save to CSV file
# csv_file_path = r"files/classified_jobs.csv"
# with open(csv_file_path, mode="w", newline="") as file:
#     writer = csv.writer(file)
#     writer.writerows(csv_data)

'''------------------------------------------------------------------------------------------------------------------------------------------------------------------'''

#Converting Date & Time to Date only

with open(r"files/ml_jobs.json", "r") as file:
    content = json.load(file)

# 
for item in content:
    if 'jobPostedDate' in item and isinstance(item['jobPostedDate'], str):
        # Parse the date string to a datetime object
        date_with_time = datetime.strptime(item['jobPostedDate'], '%Y-%m-%d %H:%M:%S')  # Adjust format as needed
        # Update the date to keep only the date part (YYYY-MM-DD)
        item['jobPostedDate'] = date_with_time.strftime('%Y-%m-%d')  # Format as YYYY-MM-DD

# Save the updated content back to the JSON file
with open(r"files/ml_jobs.json", "w") as file:
    json.dump(content, file, indent=4)
