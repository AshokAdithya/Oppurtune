import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import json
from db_singleton import DatabaseConnection, insert_jobs, get_existing_job_ids, call_insert_procedure
from job_role_predictor import JobRolePredictor

class TestDatabaseConnection(unittest.TestCase):

    @patch('cx_Oracle.SessionPool')  # Mock the cx_Oracle SessionPool
    def test_insert_jobs(self, mock_session_pool):
        # Create a mock connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()

        # Setup the mock behavior
        mock_connection.cursor.return_value = mock_cursor
        mock_session_pool.return_value.acquire.return_value = mock_connection

        # Create a mock DatabaseConnection instance
        db = DatabaseConnection()

        # Example job data
        jobs = [
            {
                "postId": 1,
                "companyName": "Test Company",
                "companyLogo": "https://test.com/logo.png",
                "companyLocation": "Test City",
                "jobPostedDate": "2024-11-01",
                "jobTitle": "Software Engineer",
                "jobType": "Full-time",
                "jobApplyUrl": "https://test.com/apply",
                "jobSkills": ["Python", "Django"],
                "jobRole": "Developer",
                "aboutJob": "Job description here"
            }
        ]

        # Mock the insert_jobs function
        insert_jobs(jobs, db)

        # Assertions to ensure the insert_job procedure was called correctly
        mock_cursor.callproc.assert_called_once_with(
            'insert_job', [
                1, "Test Company", "https://test.com/logo.png", "Test City", 
                datetime.strptime("2024-11-01", "%Y-%m-%d"), "Software Engineer", 
                "Full-time", "https://test.com/apply", 
                json.dumps(["Python", "Django"]), "Developer", 
                "Job description here", datetime.now().date()
            ]
        )

        # Ensure that commit was called
        mock_connection.commit.assert_called_once()

        # Close the mock connection
        db.close()

    @patch('cx_Oracle.SessionPool')  # Mock the cx_Oracle SessionPool for get_existing_job_ids
    def test_get_existing_job_ids(self, mock_session_pool):
        # Create a mock connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()

        # Setup the mock behavior
        mock_connection.cursor.return_value = mock_cursor
        mock_session_pool.return_value.acquire.return_value = mock_connection

        # Mock the cursor to return specific values
        mock_cursor.fetchall.return_value = [(1,), (2,)]

        # Create DatabaseConnection instance
        db = DatabaseConnection()

        # Test retrieving existing job IDs
        existing_ids = get_existing_job_ids(db)
        self.assertEqual(existing_ids, {1, 2})

        # Ensure the execute method was called correctly
        mock_cursor.execute.assert_called_once_with("SELECT post_id FROM JOB_LIST")

        # Close the mock connection
        db.close()

    @patch('cx_Oracle.SessionPool')  # Mock the cx_Oracle SessionPool for call_insert_procedure
    def test_call_insert_procedure(self, mock_session_pool):
        # Create a mock connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()

        # Setup the mock behavior
        mock_connection.cursor.return_value = mock_cursor
        mock_session_pool.return_value.acquire.return_value = mock_connection

        # Initialize the db object here to avoid the NameError
        db = DatabaseConnection()

        # Example job data
        job = {
            "postId": 1,
            "companyName": "Test Company",
            "companyLogo": "https://test.com/logo.png",
            "companyLocation": "Test City",
            "jobPostedDate": "2024-11-01",
            "jobTitle": "Software Engineer",
            "jobType": "Full-time",
            "jobApplyUrl": "https://test.com/apply",
            "jobSkills": ["Python", "Django"],
            "jobRole": "Developer",
            "aboutJob": "Job description here"
        }

        # Mock the call_insert_procedure function
        call_insert_procedure(job, db)

        # Assertions to ensure the call to the insert job procedure was made with the correct parameters
        mock_cursor.callproc.assert_called_once_with(
            'insert_job', [
                1, "Test Company", "https://test.com/logo.png", "Test City", 
                datetime.strptime("2024-11-01", "%Y-%m-%d"), "Software Engineer", 
                "Full-time", "https://test.com/apply", 
                json.dumps(["Python", "Django"]), "Developer", 
                "Job description here", datetime.now().date()
            ]
        )

        # Ensure that commit was called
        mock_connection.commit.assert_called_once()

        # Close the mock connection
        db.close()


if __name__ == "__main__":
    unittest.main()
