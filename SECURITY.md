# Security Policy

🛡️ Security Standards Compliance
The Parish Database project aims to protect sensitive parishioner data by adhering to the following industry standards:

OWASP Top 10: Protection against common web vulnerabilities (Injection, Broken Access Control, etc.).

GDPR / Privacy by Design: As religious data is "Special Category Data," we implement strict data minimization and encryption.

NIST SP 800-218: Secure Software Development Framework (SSDF) practices.

🔒 Security Controls
We implement the following controls within our Tech Stack:

1. Authentication & Authorization
Framework: Powered by Auth.js and FastAPI dependency injection.

RBAC (Role-Based Access Control): Access to sacramental records and administrative analytics is restricted based on user roles (e.g., Admin, Staff, Clergy).

Session Management: Secure, HTTP-only cookies are used to prevent XSS-based token theft.

1. Data Protection
Input Validation: All data is validated via Pydantic v2 on the backend and TypeScript on the frontend to prevent malformed data entry.

Database Security: We utilize SQLAlchemy 2.0's parameterized queries to mitigate SQL Injection.

Rate Limiting: Slowapi is configured on public-facing registration routes to prevent brute-force and DoS attacks.

🛠️ Security Hardening (Production)
When moving from development to production, the following must be implemented:

TLS/SSL: All traffic must be served over HTTPS.

Environment Secrets: Never commit .env files. Use a secure Secret Management system.

Database Encryption: Enable Transparent Data Encryption (TDE) for the PostgreSQL volume.

Security Headers: Configure SvelteKit/FastAPI to send Content-Security-Policy, X-Frame-Options, and Strict-Transport-Security headers.

🐛 Reporting a Vulnerability
We welcome security reports from the community. If you find a vulnerability, please do not open a public Issue. Instead, follow these steps:

Email: Send a detailed report to <security@yourparishdomain.org>.

Details: Include a description of the vulnerability, steps to reproduce, and potential impact.

Response: We will acknowledge your report within 48 hours and provide a timeline for a fix.

🚢 Dependency Scanning
We use automated tools to monitor our supply chain:

Frontend: npm audit is run during CI to catch vulnerable packages.

Backend: Safety and pip-audit are used to check Python dependencies.

Containers: Docker images are scanned for vulnerabilities before deployment.
