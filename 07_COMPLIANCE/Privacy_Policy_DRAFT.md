# Privacy Policy — Themis Court Path
## DRAFT — REQUIRES COMMANDER REVIEW
**Effective Date**: [TO BE SET AT LAUNCH]
**Last Updated**: 2026-04-17

---

## 1. Introduction

Themis Court Path ("the Platform"), operated by Athena Intelligence, a division of Atlas Systems Group ("we," "us," or "our"), respects your privacy. This Privacy Policy explains how we collect, use, store, and protect your personal information when you use our document preparation platform.

**Given the sensitive nature of legal filings, we take data protection extremely seriously.** This policy is designed to be transparent about exactly what we do with your data.

---

## 2. Information We Collect

### 2.1 Personal Information You Provide

When you use the Platform to prepare court documents, we collect the following categories of personally identifiable information (PII):

| Category | Data Collected | Why We Need It |
|----------|---------------|----------------|
| **Identity** | Full legal names (petitioner, respondent, children) | Required on court forms |
| **Dates of Birth** | DOB for all parties and children | Required on court forms |
| **Social Security Numbers** | SSN for petitioner, respondent, and children | Required on Sensitive Data Sheet |
| **Driver's License** | DL number for petitioner and respondent | Required on Sensitive Data Sheet |
| **Addresses** | Mailing addresses for all parties | Required on court forms |
| **Contact Information** | Phone numbers, email addresses | Required on court forms |
| **Employment** | Employer names, addresses, phone numbers | Required for wage garnishment |
| **Financial** | Income amounts, support calculations | Required for child support worksheet |
| **Family** | Relationship details, custody arrangements | Required for petition content |

### 2.2 Information Collected Automatically

- **Session data**: Temporary session cookies to maintain your progress through the intake wizard
- **Server logs**: IP address, browser type, access times (standard web server logs)
- **Error logs**: Technical error information for troubleshooting

### 2.3 Information We Do NOT Collect

- We do not use tracking cookies, advertising pixels, or analytics trackers (Phase 1)
- We do not collect biometric data
- We do not record keystrokes or screen activity
- We do not access your device contacts, photos, or files

---

## 3. How We Use Your Information

Your personal information is used **exclusively** for document preparation:

| Use | Description |
|-----|-------------|
| **Document generation** | Populating official court PDF forms with your data |
| **Calculations** | Computing child support amounts per Arizona Guidelines |
| **Validation** | Generating a validation report of filled fields |
| **Account management** | Storing your filing history (Phase 2) |
| **Customer support** | Responding to your questions about your filing |

### We Do NOT Use Your Data For:
- Advertising or marketing to third parties
- Data mining or profiling
- Selling or renting to any third party
- Training AI models
- Any purpose unrelated to your document preparation

---

## 4. How We Store and Protect Your Data

### 4.1 Storage
- **Application hosting**: Google Cloud Run (US-based data centers, us-west1 region)
- **Database** (Phase 2): Google Cloud SQL with encryption at rest (AES-256)
- **File storage**: Generated PDFs are served immediately and NOT permanently stored on our servers (Phase 1)

### 4.2 Security Measures
- All data transmitted over HTTPS (TLS 1.2+)
- Database encryption at rest (Phase 2)
- Application-level security headers (CSP, HSTS, X-Frame-Options)
- Rate limiting on submission endpoints
- No PII stored in server logs
- Access restricted to authorized personnel only

### 4.3 Data Retention
- **Phase 1 (current)**: Generated PDFs are created in temporary storage and served to your browser immediately. They are automatically deleted when the server session ends. We do not retain copies of your completed documents.
- **Phase 2 (future)**: When user accounts are implemented, filing data will be retained for 90 days after generation, then automatically purged. Users may request earlier deletion at any time.
- **Server logs**: Retained for 30 days for security and troubleshooting, then deleted.

---

## 5. Who We Share Your Data With

### We share your data with NO ONE, with these limited exceptions:

| Recipient | When | Why |
|-----------|------|-----|
| **eFileAZ** (Phase 3) | When you choose to e-file | To submit your documents to the court — only with your explicit authorization |
| **Stripe** | When you make a payment | Payment processing only — Stripe receives payment card data, NOT your case data |
| **Law enforcement** | If legally required | In response to a valid subpoena, court order, or legal process |
| **Attorney network** | If you request a consultation | Your name and case type only — full case details shared only with your consent |

### We will NEVER:
- Sell your personal information
- Share your SSN, income, or family data with marketers
- Provide your data to data brokers
- Use your data for advertising purposes

---

## 6. Your Rights

### 6.1 Access
You have the right to request a copy of all personal information we hold about you. Contact privacy@themiscourtpath.com.

### 6.2 Deletion
You have the right to request deletion of your personal information at any time. We will delete all data within 30 days of your request, except where retention is required by law.

### 6.3 Correction
You have the right to request correction of inaccurate personal information.

### 6.4 Data Portability
You have the right to receive your data in a structured, machine-readable format (JSON export).

### 6.5 Opt-Out
You may opt out of any marketing communications at any time by clicking "unsubscribe" or contacting us.

---

## 7. California Consumer Privacy Act (CCPA) Notice

If you are a California resident, you have additional rights under the CCPA:

- **Right to Know**: What personal information we collect, use, and disclose
- **Right to Delete**: Request deletion of your personal information
- **Right to Opt-Out of Sale**: We do NOT sell personal information. This right is satisfied by default.
- **Right to Non-Discrimination**: We will not discriminate against you for exercising your CCPA rights

To exercise these rights, contact: privacy@themiscourtpath.com or call [PHONE NUMBER TO BE ADDED].

---

## 8. Children's Privacy (COPPA)

The Platform is designed for adults (18+) preparing family court documents. We do not knowingly collect personal information from children under 13. Information about minor children (names, DOBs, SSNs) is collected from their parent/guardian as required by court forms, not directly from the children.

If we learn we have collected information from a child under 13 without parental consent, we will delete it immediately. Contact: privacy@themiscourtpath.com.

---

## 9. Cookies

### Phase 1 (Current)
We use only **essential session cookies** to maintain your progress through the intake wizard. These cookies:
- Are strictly necessary for the Platform to function
- Contain no personal information
- Expire when you close your browser
- Cannot be used to track you across websites

### We Do NOT Use:
- Tracking cookies
- Advertising cookies
- Third-party analytics cookies (no Google Analytics in Phase 1)

---

## 10. Data Breach Notification

In the event of a data breach that compromises your personal information:

- We will notify affected users within 72 hours of discovering the breach
- Notification will be sent via email and posted on the Platform
- We will describe what information was affected, what steps we are taking, and what steps you should take
- We will notify relevant authorities as required by applicable law (Arizona A.R.S. 18-552)

---

## 11. International Users

The Platform is designed for use in the United States, specifically Arizona. If you access the Platform from outside the US, your data will be transferred to and processed in the United States. By using the Platform, you consent to this transfer.

---

## 12. Changes to This Policy

We may update this Privacy Policy from time to time. Material changes will be communicated via email to registered users and posted on the Platform with an updated "Last Updated" date. Your continued use of the Platform after changes constitutes acceptance.

---

## 13. Contact Us

For privacy questions, data requests, or concerns:

**Athena Intelligence — Themis Court Path Division**
Email: privacy@themiscourtpath.com
General: info@themiscourtpath.com
Website: themiscourtpath.com

---

*Privacy Policy — DRAFT v1.0*
*Prepared by Agent B for Commander review*
*This document requires review by a licensed attorney before publication*
