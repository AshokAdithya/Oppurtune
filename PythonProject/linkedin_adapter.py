from linkedin_api import Linkedin

#Adaptor Pattern for Linkedin API
class LinkedInAdapter:
    def __init__(self, credentials):
        self.linkedin = Linkedin(username=credentials["username"], password=credentials["password"],authenticate=True,refresh_cookies=False,debug=True)
    
    def search_jobs(self,params):
        return self.linkedin.search_jobs(**params)
    
    def get_job(self,job_id):
        return self.linkedin.get_job(job_id=job_id)

    def get_job_skills(self,job_id):
        skills_result=self.linkedin.get_job_skills(job_id=job_id)
        skills=[skill['localizedSkillDisplayName'] for skill in skills_result['skillMatchStatuses']]
        return skills

