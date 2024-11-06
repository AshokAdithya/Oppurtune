// JobList.js
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { useQuery } from "react-query";
import axios from "axios";
import { setJobs, setSelectedJob } from "./store/jobsSlice";
import "./JobList.css";
import { login, logout } from "./store/authSlice";
import UserImage from "./assets/user.png";

const fetchSavedJobs = async (user) => {
  const response = await axios.get(
    `http://127.0.0.1:5000/api/saved-jobs/${user}`
  );
  return response.data;
};

const fetchJobDetails = async (postId, user) => {
  const response = await axios.get(
    `http://127.0.0.1:5000/api/jobs/${postId}/${user}`
  );
  return response.data;
};

const refetchSavedJobs = () => {
  const newJobData = fetchSavedJobs(user);
  dispatch(setJobs(newJobData.jobs));
};

const saveJobPost = async (postId, username) => {
  try {
    const response = await axios.post("http://127.0.0.1:5000/api/save/job", {
      postId,
      username,
    });
    return response.data;
  } catch (error) {
    console.error("Error saving job:", error);
    return { success: false };
  }
};

const SavedJobs = () => {
  const dispatch = useDispatch();
  const Navigate = useNavigate();
  const { jobs, selectedJobId } = useSelector((state) => state.jobs);
  const { user, isAuthenticated } = useSelector((state) => state.auth);

  useEffect(() => {
    const user = localStorage.getItem("user");
    if (user) {
      dispatch(login(user));
    } else {
      dispatch(logout());
    }
  }, [dispatch]);

  const [save, setSave] = useState("Save");

  const {
    data: jobData,
    refetch: refetchSavedJobs,
    isLoading: jobsLoading,
  } = useQuery(["jobs", user], () => fetchSavedJobs(user), {
    onSuccess: (data) => {
      dispatch(setJobs(data));
      if (data.length > 0) {
        dispatch(setSelectedJob(data[0].post_id));
      }
    },
    refetchOnWindowFocus: false,
  });

  const { data: jobDetails, isLoading: jobDetailsLoading } = useQuery(
    ["jobDetails", selectedJobId, user],
    () => fetchJobDetails(selectedJobId, user),
    {
      enabled: !!selectedJobId && !!user,
      onSuccess: (data) => {
        setSave(data?.isSaved ? "Saved" : "Save");
      },
    }
  );

  const saveJob = async () => {
    if (selectedJobId && user) {
      try {
        const response = await saveJobPost(selectedJobId, user);
        if (response.success) {
          setSave("Saved");
        } else {
          setSave("Save");
        }
      } catch (error) {
        console.error("Error saving job:", error);
        setSave("Save");
      }
    }
  };

  if (!isAuthenticated) {
    Navigate("/login");
  }

  const logoutFunction = () => {
    localStorage.removeItem("user");
    dispatch(logout());
  };

  if (jobsLoading) return <div className="loading">Loading jobs...</div>;
  if (jobDetailsLoading && selectedJobId)
    return <div className="loading">Loading job details...</div>;

  return (
    isAuthenticated && (
      <div className="job-list-container">
        <div className="full-header">
          <div className="header-section">
            <h1>Opportune</h1>
          </div>
          <div className="user-details">
            <p style={{ margin: "auto 0" }}>{user}</p>
            <img
              src={UserImage}
              alt="account-image"
              width="40px"
              height="40px"
              style={{ margin: "auto 0" }}
            />
            <button className="logout" onClick={logoutFunction}>
              Logout
            </button>
            <button
              className="saved-jobs"
              onClick={() => {
                Navigate("/");
              }}
            >
              Back
            </button>
          </div>
        </div>
        <hr className="line-bar"></hr>

        {jobs.length > 0 && (
          <div className="body-section">
            <div className="left-box">
              <div className="internship-title">
                <h1>Saved Internships</h1>
                <hr></hr>
              </div>
              <div className="job-list">
                <ul>
                  {jobs.map((job) => (
                    <li
                      key={job.post_id}
                      onClick={() => dispatch(setSelectedJob(job.post_id))}
                    >
                      <div className="job-postings">
                        <div className="company-logo">
                          <img
                            src={job.company_logo}
                            alt=""
                            width="100px"
                            height="100px"
                          />
                        </div>
                        <div className="job-small-details">
                          <h4 className="job-title">{job.job_title}</h4>
                          <p className="job-company">{job.company_name}</p>
                          <p className="job-company-location">
                            {job.company_location}
                          </p>
                          <p className="job-company-location">
                            Saved Date:{" "}
                            {new Date(
                              jobDetails.job_posted_date
                            ).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <hr className="job-separator"></hr>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="job-details">
              {jobDetails && (
                <div>
                  <h2>{jobDetails.job_title}</h2>
                  <p>
                    <strong>Company: </strong> {jobDetails.company_name}
                  </p>
                  <p>
                    <strong>Location: </strong> {jobDetails.company_location}
                  </p>
                  <p>
                    <strong>Posted on: </strong>
                    {new Date(jobDetails.job_posted_date).toLocaleDateString()}
                  </p>
                  <p>
                    <strong>Job Type: </strong> {jobDetails.job_type}
                  </p>
                  <p>
                    <strong>Role: </strong> {jobDetails.job_role}
                  </p>
                  <p>
                    <strong>Interested Applicants :</strong>{" "}
                    {jobDetails.applicants}
                  </p>
                  <div className="applications-context">
                    <div className="apply-link">
                      <a
                        href={jobDetails.job_apply_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Apply Now
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          height="20px"
                          viewBox="0 -960 960 960"
                          width="20px"
                          fill="#ffffff"
                        >
                          <path d="m243-240-51-51 405-405H240v-72h480v480h-72v-357L243-240Z" />
                        </svg>
                      </a>
                    </div>
                    <button className="save-button" onClick={saveJob}>
                      {save}
                    </button>
                  </div>

                  {jobDetails.job_skills.length > 0 && (
                    <p>
                      <strong>Skills:</strong>
                      {jobDetails.job_skills.join("  •  ")}
                    </p>
                  )}
                  {jobDetails.about_job && (
                    <div>
                      <p>
                        <strong>About Job:</strong>
                      </p>
                      <div
                        style={{ marginLeft: "15px" }}
                        dangerouslySetInnerHTML={{
                          __html: jobDetails.about_job,
                        }}
                      />
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
        {!jobs.length > 0 && (
          <div
            className="body-section"
            style={{
              background: "none",
              border: "none",
              display: "flex",
              alignContent: "center",
              justifyContent: "center",
            }}
          >
            <p>No saved jobs found</p>
          </div>
        )}
      </div>
    )
  );
};

export default SavedJobs;
