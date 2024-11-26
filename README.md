# Opportune - Internship & Job Application Platform

**Tagline/Short Description**: A platform designed to help students apply for internships and jobs, featuring automated resume generation, job scraping from multiple platforms, intelligent filtering options, and integration with advanced design patterns.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Overview

**Opportune** is a platform designed to help students streamline their internship and job application process. The application integrates multiple technologies including **Python Flask** for the backend, **Oracle Database** for storing user and job data, and a series of **Low-Level Design (LLD)** patterns like **Adapter**, **Factory**, and **Facade** to ensure scalability, maintainability, and extensibility.

- **Frontend**: React.js
- **Backend**: Python Flask
- **Database**: Oracle
- **Design Patterns**: Adapter, Factory, Facade, and more
- **Cron Jobs**: Automating tasks like job scraping and data updates

The platform allows students to create resumes, scrape job postings, and apply to internships with just a few clicks.

---

## Features

- **Automated Resume Generation**: Students can input details and generate a professional resume.
- **Job Scraping**: Automatically scrapes job listings from platforms like LinkedIn, Glassdoor, etc.
- **Advanced Job Filtering**: Filter job postings based on location, company, salary, etc.
- **Automated Application Submission**: Students can apply to jobs directly from the platform.
- **User Authentication**: Secure login with options for traditional authentication or Google OAuth.
- **Admin Panel**: Allows admin to manage job postings, users, and monitor statistics.
- **Cron Jobs**: Automatically update job data and other information on a scheduled basis.
- **Low-Level Design Patterns**: The backend uses Adapter, Factory, and Facade patterns to ensure scalable and maintainable code.

---

## Installation

### Prerequisites

- **Python** (for Flask backend)
- **Oracle Database** (for storing user and job data)
- **Node.js** and **npm** (for React frontend)
- **Cron Jobs** (for automating tasks like rent updates)

### Backend Setup (Python Flask)

1. Clone the repository:

```bash
git clone https://github.com/AshokAdithya/Opportune.git
cd opportune
```

2. Setting up the Backend
```bash
cd PythonProject
pip install -r requirements.txt
```

3. Make credentials.json and insert you testing linkedin email-id and password in a json format
   
4. Make necessary Tables and Procedures in Oracle DB 

5. Run the Cron (main.py)
```bash
python main.py
```

6. Setting up the Frontend
```bash
cd job-listing-app
npm install
```
## Usage
To run the project, use the following command:
```bash
python app.py
```
```bash
npm run dev
```

## Contributing
1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes.
4. Push your branch: `git push origin feature-name`.
5. Create a pull request.

## License
This project is licensed under the [MIT License](LICENSE).



