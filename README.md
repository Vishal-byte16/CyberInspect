# 🛡️ CyberInspect

> A modern Website Security Assessment Platform that performs automated, non-intrusive security analysis of websites.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![JavaScript](https://img.shields.io/badge/JavaScript-Frontend-yellow?logo=javascript)
![HTML5](https://img.shields.io/badge/HTML5-Frontend-orange?logo=html5)
![CSS3](https://img.shields.io/badge/CSS3-Styling-blue?logo=css3)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📌 Overview

CyberInspect is a full-stack web application that helps users evaluate the security posture of websites using publicly available security information.

It performs a comprehensive security assessment by analyzing SSL/TLS configuration, HTTP security headers, DNS records, cookies, reputation, domain information, HTTP responses, and detected technologies.

The platform generates detailed HTML and PDF security reports with actionable recommendations while maintaining a clean and modern user interface.

---

# ✨ Features

- 🔍 Website Security Scanner
- 🔒 SSL/TLS Certificate Analysis
- 🛡️ HTTP Security Headers Analysis
- 🌐 DNS Record Inspection
- 🌍 Domain Information Lookup
- 🚨 Website Reputation Check
- 🍪 Cookie Security Analysis
- 📡 HTTP Response Analysis
- ⚙️ Technology Detection
- 📄 Professional PDF Report Generation
- 🌐 HTML Report Export
- 📚 Scan History
- ⭐ Save Favorite Websites
- 👤 User Authentication
- 🔑 JWT Authentication
- 🛠️ Admin Dashboard
- 📊 Security Score & Risk Rating
- 📱 Responsive Dashboard UI


# 🛠️ Tech Stack

## Frontend

- HTML5
- CSS3
- JavaScript

## Backend

- FastAPI
- Python

## Database

- SQLite

## Authentication

- JWT Authentication

## PDF Generation

- ReportLab

---

# 📂 Project Structure

```
CyberInspect/
│
├── backend/
│   ├── auth/
│   ├── database/
│   ├── reports/
│   ├── scanner/
│   ├── utils/
│   └── main.py
│
├── frontend/
│   ├── dashboard/
│   ├── login/
│   ├── reports/
│   ├── scanner/
│   └── js/
│
├── assets/
│
├── dashboard.html
├── scanner.html
├── history.html
├── profile.html
├── reports.html
├── saved.html
├── login.html
├── index.html
│
└── requirements.txt
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/Vishal-byte16/CyberInspect.git
```

```bash
cd CyberInspect
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment

Create a `.env` file:

```env
DATABASE_URL=sqlite:///./cyberinspect.db
JWT_SECRET=292f88a113bd5fd3e59af9de3eb8d3a208c7d88ac47cbd1d07ad587176810d5d
```

---

## Run Backend

```bash
uvicorn backend.main:app --reload
```

Backend will start on:

```
http://127.0.0.1:8000
```

---

## Run Frontend

Open the project using **VS Code Live Server** or any local web server.

---

# 📄 PDF Reports

CyberInspect generates professional downloadable reports including:

- Executive Summary
- Security Score
- Risk Rating
- SSL Analysis
- Security Headers
- DNS Configuration
- Website Information
- Security Recommendations
- Disclaimer

---

# 🔐 Security Checks

CyberInspect currently analyzes:

- HTTPS Availability
- SSL Certificate
- Certificate Issuer
- TLS Version
- Security Headers
- DNS Records
- SPF
- DMARC
- DKIM
- Domain Age
- Registrar
- WHOIS Information
- IP Address
- Cookie Security
- HTTP Status
- Response Time
- Server Information
- Technology Detection
- Website Reputation

---

# 🎯 Future Improvements

- VirusTotal Integration
- Google Safe Browsing Integration
- SSL Labs Integration
- WHOIS API Integration
- Scheduled Website Monitoring
- Email Alerts
- Multi-language Support
- Dark/Light Theme
- Docker Support
- REST API Documentation
- Cloud Deployment

---

# 👨‍💻 Author

**Vishal Nachare**

B.Sc. Computer Science Student

Cybersecurity Enthusiast | Python Developer | Full Stack Developer

GitHub:
https://github.com/Vishal-byte16

LinkedIn:
https://linkedin.com/in/vishal-nachare-68b429257

Portfolio:
https://vishalnachare.carrd.co

---

# 📜 License

This project is licensed under the MIT License.

---

## ⭐ Support

If you found this project useful, please consider giving it a ⭐ on GitHub!