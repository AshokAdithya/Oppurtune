// JobList.js
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { useQuery } from "react-query";
import axios from "axios";
import {
  setJobs,
  setSelectedJob,
  setPage,
  setSearch,
  setTotalPages,
  setTopCompanies,
  setTopLocations,
} from "./store/jobsSlice";
import "./JobList.css";
import { login, logout } from "./store/authSlice";
import UserImage from "./assets/user.png";

const fetchJobs = async (page, search, appliedFilters) => {
  const response = await axios.get(
    `http://127.0.0.1:5000/api/jobs?page=${page}&search=${search}&filters=${JSON.stringify(
      appliedFilters
    )}`
  );
  return response.data;
};

const fetchFilters = async () => {
  const response = await axios.get(`http://127.0.0.1:5000/api/get-filters`);
  return response.data;
};

const fetchJobDetails = async (postId, user) => {
  const response = await axios.get(
    `http://127.0.0.1:5000/api/jobs/${postId}/${user}`
  );
  return response.data;
};

const refetchJobs = () => {
  const newJobData = fetchJobs(page, search, appliedFilters);
  dispatch(setJobs(newJobData.jobs));
  dispatch(setTotalPages(newJobData.total_pages));
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

const JobList = () => {
  const dispatch = useDispatch();
  const Navigate = useNavigate();
  const {
    jobs,
    selectedJobId,
    page,
    search,
    totalPages,
    topCompanies,
    topLocations,
  } = useSelector((state) => state.jobs);

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
  const [searchInput, setSearchInput] = useState(search);
  const [filters, setFilters] = useState({
    datePosted: "",
    companyName: "",
    location: "",
    jobType: "",
    jobRole: "",
  });

  const [appliedFilters, setAppliedFilters] = useState({});

  const {
    data: jobData,
    refetch: refetchJobs,
    isLoading: jobsLoading,
  } = useQuery(
    ["jobs", page, search, appliedFilters],
    () => fetchJobs(page, search, appliedFilters),
    {
      onSuccess: (data) => {
        dispatch(setJobs(data.jobs));
        dispatch(setTotalPages(data.total_pages));
        if (data.jobs.length > 0) {
          dispatch(setSelectedJob(data.jobs[0].post_id));
        }
      },
      refetchOnWindowFocus: false,
    }
  );

  const { data: jobDetails, isLoading: jobDetailsLoading } = useQuery(
    ["jobDetails", selectedJobId, user, save],
    () => fetchJobDetails(selectedJobId, user),
    {
      enabled: !!selectedJobId && !!user,
      onSuccess: (data) => {
        setSave(data?.isSaved ? "Saved" : "Save");
      },
    }
  );

  const { data: filtersData, isLoading: filtersLoading } = useQuery(
    "filters",
    fetchFilters,
    {
      onSuccess: (data) => {
        dispatch(setTopCompanies(data.top_companies));
        dispatch(setTopLocations(data.top_locations));
      },
    }
  );

  const handleSearchChange = (event) => {
    setSearchInput(event.target.value);
  };

  const handleSearchSubmit = () => {
    dispatch(setSearch(searchInput));
    dispatch(setPage(1));
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      handleSearchSubmit();
    }
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters((prevFilters) => ({
      ...prevFilters,
      [name]: value,
    }));
  };

  const applyFilters = () => {
    setAppliedFilters(filters);
    setFilters({
      datePosted: "",
      companyName: "",
      location: "",
      jobType: "",
      jobRole: "",
    });
    dispatch(setPage(1));
  };

  const resetFilters = () => {
    setFilters({
      datePosted: "",
      companyName: "",
      location: "",
      jobType: "",
      jobRole: "",
    });
    setAppliedFilters({});
    dispatch(setPage(1));
  };

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
            <div className="search-bar-container">
              <input
                className="search-bar"
                type="text"
                value={searchInput}
                onChange={handleSearchChange}
                onKeyDown={handleKeyDown}
              />
              <button className="search-button" onClick={handleSearchSubmit}>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  height="30px"
                  viewBox="0 -960 960 960"
                  width="30px"
                  fill="#ffffff"
                  style={{
                    display: "block",
                    margin: 0,
                    padding: 0,
                    border: "none",
                  }}
                >
                  <path d="M792-120.67 532.67-380q-30 25.33-69.64 39.67Q423.39-326 378.67-326q-108.44 0-183.56-75.17Q120-476.33 120-583.33t75.17-182.17q75.16-75.17 182.5-75.17 107.33 0 182.16 75.17 74.84 75.17 74.84 182.27 0 43.23-14 82.9-14 39.66-40.67 73l260 258.66-48 48Zm-414-272q79.17 0 134.58-55.83Q568-504.33 568-583.33q0-79-55.42-134.84Q457.17-774 378-774q-79.72 0-135.53 55.83-55.8 55.84-55.8 134.84t55.8 134.83q55.81 55.83 135.53 55.83Z" />
                </svg>
              </button>
            </div>
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
                Navigate("/saved-jobs");
              }}
            >
              Saved Jobs
            </button>
          </div>
        </div>
        <hr className="line-bar"></hr>

        <div className="filter-section">
          <div className="filter-container">
            <label htmlFor="datePosted">Date Posted:</label>
            <select
              id="datePosted"
              name="datePosted"
              onChange={handleFilterChange}
            >
              <option value="">Any time</option>
              <option value="last-24-hours">Last 24 hours</option>
              <option value="last-5-days">Last 5 days</option>
              <option value="last-10-days">Last 10 days</option>
            </select>
          </div>

          <div className="filter-container">
            <label htmlFor="companyName">Company Name:</label>
            <select
              id="companyName"
              name="companyName"
              onChange={handleFilterChange}
            >
              <option value="">All Companies</option>
              {topCompanies.map((company) => (
                <option key={company} value={company}>
                  {company}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-container">
            <label htmlFor="location">Location:</label>
            <select id="location" name="location" onChange={handleFilterChange}>
              <option value="">Any Location</option>
              {topLocations.map((location) => (
                <option key={location} value={location}>
                  {location}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-container">
            <label htmlFor="jobType">Job Type:</label>
            <select id="jobType" name="jobType" onChange={handleFilterChange}>
              <option value="">Any Type</option>
              <option value="on-site">On-site</option>
              <option value="remote">Remote</option>
              <option value="hybrid">Hybrid</option>
            </select>
          </div>

          <div className="filter-container">
            <label htmlFor="jobRole">Job Role:</label>
            <select id="jobRole" name="jobRole" onChange={handleFilterChange}>
              <option value="">Any Role</option>
              <option value="Finance">Finance</option>
              <option value="Software Development">Software Development</option>
              <option value="Data Analysis">Data Analysis</option>
              <option value="Business Development">Business Development</option>
              <option value="Other">Other</option>
              <option value="Machine Learning">Machine Learning</option>
              <option value="Content Creation">Content Creation</option>
              <option value="Web Development">Web Development</option>
              <option value="Sales">Sales</option>
              <option value="Operations">Operations</option>
              <option value="Marketing">Marketing</option>
              <option value="Human Resources">Human Resources</option>
              <option value="Graphic Design">Graphic Design</option>
              <option value="SEO Specialist">SEO Specialist</option>
              <option value="Cyber Security">Cyber Security</option>
            </select>
          </div>

          <div className="reset-container">
            <button className="apply-button" onClick={applyFilters}>
              Apply Filters
            </button>
            <button className="reset-button" onClick={resetFilters}>
              Reset Filters
            </button>
          </div>
        </div>
        {jobs.length > 0 && (
          <div className="body-section">
            <div className="left-box">
              <div className="internship-title">
                <h1>Internships in India</h1>
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
                        </div>
                      </div>
                      <hr className="job-separator"></hr>
                    </li>
                  ))}
                </ul>
              </div>
              <hr style={{ width: "100%" }}></hr>
              <div className="pagination">
                <div>
                  <button
                    disabled={page === 1}
                    onClick={() => dispatch(setPage(page - 1))}
                  >
                    Previous
                  </button>
                </div>
                <span>
                  Page {page} of {totalPages}
                </span>
                <div>
                  <button
                    disabled={page === totalPages}
                    onClick={() => dispatch(setPage(page + 1))}
                  >
                    Next
                  </button>
                </div>
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
                      <strong>Skills:</strong>{" "}
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

export default JobList;
