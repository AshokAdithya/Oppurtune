from linkedin_adapter import LinkedInAdapter
from db_singleton import DatabaseConnection, insert_jobs, delete_old_jobs
from job_factory import JobFactory
from utils import update_date
import json
import time
import threading

class JobFacade:
    def __init__(self, credentials):
        self.linkedin_adapter = LinkedInAdapter(credentials=credentials)
        self.db = DatabaseConnection()
        self.job_factory = JobFactory(linkedin_adapter=self.linkedin_adapter)

    def process_and_collect_job(self,job,all_jobs):
        time.sleep(7)  # Simulate delay
        job_id = job["entityUrn"].split(":")[-1]
        try:
            get_job = self.linkedin_adapter.get_job(job_id=job_id)
            job_instance = self.job_factory.create_job(get_job)
            all_jobs.append(job_instance)
        except Exception as e:
            print(f"Error processing job {job_id}: {e}")


    def fetch_and_store_jobs(self, params):
        print("Step 1: Got all jobs")
        get_jobs_list = self.linkedin_adapter.search_jobs(params=params)
        all_jobs = []

        threads = []
        for job in get_jobs_list:
            thread = threading.Thread(target=self.process_and_collect_job, args=(job, all_jobs))
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        with open(r"files/files.json","w") as file:
            json.dump(all_jobs,file)

        print("Step 2 : Got required data from the api response and preprocessed")
        insert_jobs(all_jobs, self.db)

        print("Step 3: Inserted all jobs into DB")
        delete_old_jobs(self.db)

        print("Step 4: Deleted old jobs from DB")

    def close_connection(self):
        self.db.close()


def main():
    with open(r"files/credentials.json", "r") as file:
        credentials = json.load(file)

    job_facade = JobFacade(credentials=credentials)

    params = {
        "job_title": "internship",
        "industries": ["Software Development", "IT Services and IT Consulting", "Technology, Information and Internet", "Information Services"],
        "experience": ["1", "2"],
        "job_type": ["I"],
        "remote": ["1", "2", "3"],
        "listed_at": 2*86400,
        "limit": -1
    }
    
    job_facade.fetch_and_store_jobs(params)
    job_facade.close_connection()

if __name__ == "__main__":
    main()
