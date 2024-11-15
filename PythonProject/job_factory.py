import asyncio
from utils import update_date
from job_role_predictor import JobRolePredictor
from abc import ABC, abstractmethod

class createFactory(ABC):
    @abstractmethod
    def create_job(self,get_job):
        pass

    @abstractmethod()
    def get_company_logo(self,company_logo):
        pass

class JobFactory(createFactory):
    def __init__(self, linkedin_adapter):
        self.job_role_predictor = JobRolePredictor()
        self.linkedin_adapter = linkedin_adapter

    async def create_job(self, get_job):
        try:
            post_id = get_job.get("jobPostingId", None)
            workplace_types = get_job.get("workplaceTypes", [])
            workplace_types_resolution_results = get_job.get("workplaceTypesResolutionResults", {})
            company_details = get_job.get("companyDetails", {})
            
            # Start concurrent tasks
            skills_task = asyncio.create_task(self.linkedin_adapter.get_job_skills(post_id))
            job_role_task = asyncio.create_task(self.job_role_predictor.predict(get_job.get("title")))
            
            # Other synchronous operations
            apply_url = get_job["applyMethod"].get(next(iter(get_job["applyMethod"])), {})
            company_name = company_details.get("com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany", {}).get("companyResolutionResult", {}).get("name")
            company_logo = self.get_company_logo(company_details)
            company_location = get_job.get("formattedLocation")
            job_posted_date = update_date(get_job.get("listedAt"))
            job_title = get_job.get("title")
            job_type = workplace_types_resolution_results.get(workplace_types[0]) if workplace_types else None
            about_job_result = get_job.get("description", {}).get("text", "")
            about_job = about_job_result if len(about_job_result) < 4000 else None

            # Await concurrent tasks
            skills = await skills_task
            job_role = await job_role_task

            # Only add to job_dict if values are valid
            if all([company_name, company_logo, company_location, job_posted_date, job_title, job_type]):
                job_dict = {
                    "postId": int(post_id),
                    "companyName": company_name,
                    "companyLogo": company_logo,
                    "companyLocation": company_location,
                    "jobPostedDate": job_posted_date,
                    "jobTitle": job_title,
                    "jobType": job_type.get("localizedName") if job_type else None,
                    "jobApplyUrl": apply_url.get("companyApplyUrl") or apply_url.get("easyApplyUrl") or f"https://www.linkedin.com/jobs/view/{post_id}/",
                    "jobSkills": skills,
                    "jobRole": job_role,
                    "aboutJob": about_job
                }

            return job_dict

        except Exception as e:
            print(f"Error creating job from data: {e}")
            return None

    def get_company_logo(self, company_details):
        try:
            logo_url = (
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
                .get("fileIdentifyingUrlPathSegment", "")
            )
            return logo_url

        except Exception as e:
            print(f"Error retrieving company logo: {e}")
            return ""
