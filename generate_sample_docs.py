"""
Generate three realistic sample PDF documents for the Mini-RAG Assistant demo.
Uses fpdf2 to create:
  1. HR_Policy_Manual.pdf
  2. IT_Support_Process_Guide.pdf
  3. Client_Onboarding_FAQ.pdf
"""

from fpdf import FPDF
from pathlib import Path
import sys


class StyledPDF(FPDF):
    """PDF with consistent header/footer styling."""

    def __init__(self, title: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.doc_title = title
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, self.doc_title, align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(102, 126, 234)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def add_title_page(self, title: str, subtitle: str):
        self.add_page()
        self.ln(50)
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(50, 50, 80)
        self.cell(0, 15, title, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)
        self.set_font("Helvetica", "", 14)
        self.set_text_color(100, 100, 130)
        self.cell(0, 10, subtitle, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(10)
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "Confidential - Internal Use Only", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 10, "Version 3.2 | Last Updated: January 2025", align="C", new_x="LMARGIN", new_y="NEXT")

    def section_heading(self, text: str):
        self.ln(5)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(60, 60, 100)
        self.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(102, 126, 234)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 100, self.get_y())
        self.ln(3)

    def sub_heading(self, text: str):
        self.ln(3)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(80, 80, 120)
        self.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def bullet_point(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        x = self.get_x()
        self.cell(8, 6, chr(8226))  # bullet character
        self.multi_cell(0, 6, text)
        self.ln(1)


def generate_hr_policy(output_dir: Path):
    """Generate HR_Policy_Manual.pdf."""
    pdf = StyledPDF("HR Policy Manual")
    pdf.alias_nb_pages()
    pdf.add_title_page("HR Policy Manual", "Meridian Consulting Group")

    # Chapter 1: Leave Policies
    pdf.add_page()
    pdf.section_heading("1. Leave Policies")

    pdf.sub_heading("1.1 Annual Leave")
    pdf.body_text(
        "All full-time employees are entitled to 20 working days of paid annual leave per calendar year. "
        "Annual leave accrues at a rate of 1.67 days per month of continuous service. Employees in their "
        "probationary period (first 6 months) accrue leave but may only use up to 5 days during this period. "
        "Unused annual leave may be carried forward up to a maximum of 5 days into the next calendar year, "
        "subject to manager approval. Any leave beyond the carry-forward limit will be forfeited on December 31st."
    )
    pdf.body_text(
        "Leave requests must be submitted through the HR portal at least 10 business days in advance for "
        "periods of 3 or more consecutive days. For shorter absences, a minimum of 3 business days notice "
        "is required. All leave requests require direct manager approval. During peak business periods "
        "(January, June, and December), leave requests may be subject to additional restrictions."
    )

    pdf.sub_heading("1.2 Sick Leave")
    pdf.body_text(
        "Employees are entitled to 12 days of paid sick leave per calendar year. Sick leave does not carry "
        "forward and resets on January 1st each year. For absences exceeding 3 consecutive working days, "
        "a medical certificate from a registered healthcare provider must be submitted to HR within 5 "
        "business days of returning to work. Failure to provide medical documentation may result in the "
        "absence being treated as unauthorized leave."
    )
    pdf.body_text(
        "If an employee exhausts their sick leave entitlement, additional sick days may be granted at the "
        "discretion of the HR Director, subject to medical evidence. Extended illness (more than 10 "
        "consecutive days) triggers the company's Short-Term Disability policy, which provides 60% of "
        "base salary for up to 90 days."
    )

    pdf.sub_heading("1.3 Parental Leave")
    pdf.body_text(
        "Primary caregivers are entitled to 16 weeks of paid parental leave at full salary. Secondary "
        "caregivers are entitled to 4 weeks of paid parental leave. Parental leave must commence within "
        "12 months of the birth or adoption of a child. Employees must notify HR at least 8 weeks before "
        "the expected commencement date. Parental leave may be taken in a single continuous block or, "
        "with manager approval, in up to two separate blocks."
    )

    pdf.sub_heading("1.4 Bereavement Leave")
    pdf.body_text(
        "In the event of a death in the immediate family (spouse, parent, child, sibling), employees are "
        "entitled to 5 days of paid bereavement leave. For extended family members (grandparents, "
        "in-laws, aunts, uncles), 3 days of paid bereavement leave is provided. Additional unpaid leave "
        "may be requested through the HR department."
    )

    # Chapter 2: Work From Home Policy
    pdf.add_page()
    pdf.section_heading("2. Work From Home Policy")

    pdf.sub_heading("2.1 Eligibility and General Guidelines")
    pdf.body_text(
        "Meridian Consulting Group supports a hybrid work model. All employees who have completed "
        "their probationary period are eligible to work from home up to 3 days per week. New employees "
        "in their first 6 months must work from the office at least 4 days per week. Remote work "
        "arrangements must be agreed upon with the direct manager and documented in the HR portal."
    )
    pdf.body_text(
        "Employees working from home are expected to maintain their regular working hours (9:00 AM to "
        "6:00 PM local time) and must be reachable via company communication channels (Microsoft Teams, "
        "email, and phone) during core business hours (10:00 AM to 4:00 PM). All remote work must be "
        "performed from a secure, private location with reliable internet connectivity (minimum 25 Mbps "
        "download speed)."
    )

    pdf.sub_heading("2.2 Equipment and Setup")
    pdf.body_text(
        "The company provides a one-time home office setup allowance of $500 for furniture and equipment "
        "not supplied by IT. Standard IT equipment (laptop, headset, monitor) will be provided by the IT "
        "department. Employees are responsible for their own internet connection costs. A monthly internet "
        "stipend of $50 is provided for employees approved for 3+ WFH days per week."
    )

    pdf.sub_heading("2.3 Full Remote Arrangements")
    pdf.body_text(
        "Full-time remote work (5 days per week) requires VP-level approval and is available only for "
        "roles designated as 'remote-eligible' in the job classification system. Full remote employees "
        "must visit the nearest office at least once per quarter for team meetings and performance reviews. "
        "Travel expenses for mandatory office visits will be reimbursed per the company travel policy."
    )

    # Chapter 3: Performance Reviews
    pdf.add_page()
    pdf.section_heading("3. Performance Management")

    pdf.sub_heading("3.1 Annual Performance Review Cycle")
    pdf.body_text(
        "Performance reviews are conducted annually in November-December, with results communicated "
        "by January 15th. The review process includes: (a) employee self-assessment, (b) manager "
        "evaluation, (c) peer feedback from 2-3 colleagues, and (d) a calibration session with senior "
        "leadership. Employees are rated on a 5-point scale: Exceptional (5), Exceeds Expectations (4), "
        "Meets Expectations (3), Needs Improvement (2), and Unsatisfactory (1)."
    )

    pdf.sub_heading("3.2 Mid-Year Check-Ins")
    pdf.body_text(
        "Mandatory mid-year check-in meetings occur in June-July. These are informal performance "
        "discussions between the employee and their direct manager, focused on goal progress, development "
        "areas, and any support needed. No formal ratings are given during mid-year reviews."
    )

    pdf.sub_heading("3.3 Performance Improvement Plans (PIP)")
    pdf.body_text(
        "Employees receiving a rating of 2 (Needs Improvement) or below will be placed on a Performance "
        "Improvement Plan lasting 60-90 days. The PIP will include specific, measurable objectives and "
        "weekly check-ins with the manager. Failure to meet PIP objectives may result in reassignment, "
        "demotion, or termination. HR must be involved in all PIP-related discussions and decisions."
    )

    # Chapter 4: Code of Conduct
    pdf.add_page()
    pdf.section_heading("4. Code of Conduct")

    pdf.sub_heading("4.1 Professional Behavior")
    pdf.body_text(
        "All employees are expected to conduct themselves professionally in all workplace interactions. "
        "This includes treating colleagues, clients, and vendors with respect and dignity. Harassment, "
        "discrimination, or bullying of any kind is strictly prohibited and will result in disciplinary "
        "action up to and including termination. Reports of misconduct can be made through the anonymous "
        "ethics hotline at 1-800-555-ETHICS or via the online portal."
    )

    pdf.sub_heading("4.2 Confidentiality")
    pdf.body_text(
        "Employees must maintain strict confidentiality regarding client data, proprietary information, "
        "and internal business operations. All employees sign a Non-Disclosure Agreement (NDA) at the "
        "time of hiring. Violation of confidentiality obligations may result in immediate termination and "
        "legal action. Client data must never be stored on personal devices, shared via personal email, "
        "or discussed in public settings."
    )

    pdf.sub_heading("4.3 Dress Code")
    pdf.body_text(
        "Business professional attire is required when meeting clients or attending external events. "
        "For regular office days, business casual is acceptable. Fridays are designated as casual dress "
        "days. When working from home, employees should maintain a professional appearance for video "
        "calls. Specific dress code guidelines by department are available on the HR portal."
    )

    # Chapter 5: Benefits
    pdf.add_page()
    pdf.section_heading("5. Employee Benefits")

    pdf.sub_heading("5.1 Health Insurance")
    pdf.body_text(
        "The company provides comprehensive health insurance coverage including medical, dental, and "
        "vision plans. Coverage begins on the first day of the month following 30 days of employment. "
        "The company covers 80% of premium costs for employee-only plans and 65% for family plans. "
        "Three plan tiers are available: Basic (HMO), Standard (PPO), and Premium (PPO with lower "
        "deductibles). Open enrollment occurs annually in November."
    )

    pdf.sub_heading("5.2 Retirement Plan")
    pdf.body_text(
        "Meridian offers a 401(k) retirement plan with company matching. The company matches 100% of "
        "employee contributions up to 4% of base salary, and 50% of contributions between 4-6%. "
        "Matching contributions vest over a 3-year period: 33% after Year 1, 66% after Year 2, and "
        "100% after Year 3. Employees are eligible to enroll in the 401(k) immediately upon hire."
    )

    pdf.sub_heading("5.3 Professional Development")
    pdf.body_text(
        "Each employee receives an annual professional development budget of $3,000 for conferences, "
        "certifications, courses, and training materials. Requests must be submitted through the Learning "
        "& Development portal and approved by the employee's manager. The company also offers tuition "
        "reimbursement of up to $10,000 per year for degree programs relevant to the employee's role, "
        "subject to maintaining a B average or equivalent."
    )

    # Chapter 6: Grievance Procedure
    pdf.add_page()
    pdf.section_heading("6. Grievance and Complaint Procedures")

    pdf.sub_heading("6.1 Informal Resolution")
    pdf.body_text(
        "Employees are encouraged to first attempt informal resolution of workplace concerns by speaking "
        "directly with the involved party or their immediate manager. Many issues can be resolved through "
        "open, professional dialogue. If informal resolution is not possible or appropriate, the formal "
        "grievance process should be initiated."
    )

    pdf.sub_heading("6.2 Formal Grievance Process")
    pdf.body_text(
        "Step 1: Submit a written grievance to the HR department via the Grievance Form on the HR portal. "
        "Include a detailed description of the issue, dates, witnesses, and any evidence. "
        "Step 2: HR will acknowledge receipt within 2 business days and assign an HR Business Partner to "
        "investigate. "
        "Step 3: An investigation will be conducted within 10 business days, including interviews with "
        "all relevant parties. "
        "Step 4: HR will issue a written determination within 5 business days of completing the investigation. "
        "Step 5: If the employee is not satisfied with the outcome, they may appeal to the VP of HR within "
        "10 business days. The VP's decision is final."
    )

    pdf.sub_heading("6.3 Whistleblower Protection")
    pdf.body_text(
        "Employees who report violations of company policy, legal requirements, or ethical standards in "
        "good faith are protected from retaliation. The company maintains an anonymous ethics hotline "
        "(1-800-555-ETHICS) and an online reporting portal. All reports are investigated by the Compliance "
        "team, independent of the management chain."
    )

    pdf.output(str(output_dir / "HR_Policy_Manual.pdf"))
    print("  Created HR_Policy_Manual.pdf")


def generate_it_support(output_dir: Path):
    """Generate IT_Support_Process_Guide.pdf."""
    pdf = StyledPDF("IT Support Process Guide")
    pdf.alias_nb_pages()
    pdf.add_title_page("IT Support Process Guide", "Meridian Consulting Group - IT Department")

    # Chapter 1: Support Ticket System
    pdf.add_page()
    pdf.section_heading("1. IT Support Ticket System")

    pdf.sub_heading("1.1 Creating a Support Ticket")
    pdf.body_text(
        "All IT support requests must be submitted through the ServiceDesk portal at "
        "https://servicedesk.meridian.internal. To create a ticket: (1) Log in with your corporate "
        "credentials, (2) Click 'New Request', (3) Select the appropriate category, (4) Provide a "
        "detailed description including error messages, screenshots, and steps to reproduce the issue, "
        "(5) Set the priority level based on impact, (6) Submit the ticket. You will receive a "
        "confirmation email with your ticket number (format: INC-XXXXXXX)."
    )
    pdf.body_text(
        "For urgent issues that prevent you from accessing the portal, you may call the IT Help Desk "
        "directly at extension 5555 or email helpdesk@meridian.com. Phone support is available Monday "
        "through Friday, 7:00 AM to 8:00 PM Eastern Time. After-hours emergency support is available "
        "for P1 (Critical) issues only via the emergency line: 1-800-555-4357."
    )

    pdf.sub_heading("1.2 Ticket Categories")
    pdf.body_text(
        "Hardware Issues: Laptop, desktop, monitor, keyboard, mouse, docking station problems. "
        "Software Issues: Application errors, installation requests, license issues, crashes. "
        "Network/Connectivity: VPN issues, Wi-Fi problems, internet outage, network drive access. "
        "Account/Access: Password resets, account lockouts, permission requests, new account setup. "
        "Email: Outlook issues, calendar problems, shared mailbox access, email delivery failures. "
        "Security: Suspicious emails, potential malware, data breach concerns, lost/stolen devices. "
        "Other: Requests that don't fit into the above categories."
    )

    # Chapter 2: Priority Levels & SLAs
    pdf.add_page()
    pdf.section_heading("2. Priority Levels and SLA Targets")

    pdf.sub_heading("2.1 Priority Classification")
    pdf.body_text(
        "P1 - Critical: Complete system outage, security breach, or issue affecting 50+ users. "
        "Examples: Email server down, VPN service outage, ransomware detection, client-facing system "
        "failure. Response Time: 15 minutes. Resolution Target: 4 hours."
    )
    pdf.body_text(
        "P2 - High: Significant impact on business operations affecting a team or department. "
        "Examples: Department printer failure, shared drive inaccessible, critical application crash "
        "for multiple users, video conferencing system down during client calls. Response Time: 1 hour. "
        "Resolution Target: 8 business hours."
    )
    pdf.body_text(
        "P3 - Medium: Moderate impact on individual productivity with a workaround available. "
        "Examples: Single user application issue, non-critical software request, peripheral device "
        "malfunction, slow system performance. Response Time: 4 business hours. Resolution Target: "
        "2 business days."
    )
    pdf.body_text(
        "P4 - Low: Minimal impact, informational requests, or enhancements. "
        "Examples: General questions, feature requests, non-urgent software installation, cosmetic "
        "issues. Response Time: 1 business day. Resolution Target: 5 business days."
    )

    pdf.sub_heading("2.2 SLA Escalation Matrix")
    pdf.body_text(
        "If SLA targets are not met, automatic escalation occurs: "
        "Level 1 Escalation (SLA breach by 25%): Notification to IT Team Lead. "
        "Level 2 Escalation (SLA breach by 50%): Notification to IT Manager and department head. "
        "Level 3 Escalation (SLA breach by 100%): Notification to IT Director and VP of Operations. "
        "Employees can manually escalate a ticket at any time by clicking 'Escalate' in the ServiceDesk "
        "portal or by emailing it-escalation@meridian.com with the ticket number."
    )

    # Chapter 3: Access Management
    pdf.add_page()
    pdf.section_heading("3. Access Request Procedures")

    pdf.sub_heading("3.1 New Employee Access Setup")
    pdf.body_text(
        "IT access provisioning for new employees begins automatically when HR creates the employee "
        "record in the HRIS system. Standard provisioning includes: Corporate email account (Outlook 365), "
        "Active Directory account with department-appropriate group memberships, VPN access credentials, "
        "standard software suite (Microsoft Office, Teams, Zoom, Slack), network drive access for the "
        "employee's department, and badge access to the assigned office building."
    )
    pdf.body_text(
        "Provisioning is typically completed within 2 business days of the HRIS record creation. The "
        "employee's manager will receive a Welcome Kit email with all credentials and setup instructions "
        "to share on the first day. If access is needed urgently (within 24 hours), the hiring manager "
        "should submit a Priority Access Request through the ServiceDesk portal."
    )

    pdf.sub_heading("3.2 Application Access Requests")
    pdf.body_text(
        "Access to applications beyond the standard suite requires a formal request: "
        "(1) Submit an 'Application Access Request' form in the ServiceDesk portal. "
        "(2) Select the application from the catalog (Salesforce, Jira, Confluence, Tableau, SAP, etc.). "
        "(3) Specify the required access level (Read-Only, Standard User, Power User, Admin). "
        "(4) Provide business justification for the request. "
        "(5) The request is routed to the application owner and the employee's manager for dual approval. "
        "(6) Upon approval, IT provisions access within 1 business day. "
        "Some applications (e.g., production database access, financial systems) require additional "
        "approval from the Information Security team."
    )

    pdf.sub_heading("3.3 Access Revocation")
    pdf.body_text(
        "When an employee leaves the company, IT receives an automated notification from HR and "
        "initiates the access revocation process within 4 hours. This includes: disabling the AD account, "
        "revoking VPN access, removing application access, forwarding email to the designated recipient, "
        "and remotely wiping company data from mobile devices. For role changes within the company, "
        "managers must submit an 'Access Modification Request' to update permissions within 5 business days."
    )

    # Chapter 4: VPN and Remote Access
    pdf.add_page()
    pdf.section_heading("4. VPN and Remote Access")

    pdf.sub_heading("4.1 VPN Setup")
    pdf.body_text(
        "The company uses Cisco AnyConnect VPN client for secure remote access. Installation instructions: "
        "(1) Download Cisco AnyConnect from the Software Center on your company laptop. "
        "(2) Connect to VPN server: vpn.meridian.com. "
        "(3) Enter your corporate username and password. "
        "(4) Approve the multi-factor authentication (MFA) prompt on your registered device. "
        "The VPN provides access to internal resources including network drives, intranet, internal "
        "applications, and printers. VPN sessions automatically disconnect after 12 hours of inactivity."
    )

    pdf.sub_heading("4.2 VPN Troubleshooting")
    pdf.body_text(
        "Common VPN issues and solutions: "
        "Issue: 'Connection attempt has failed' - Ensure internet connectivity, try alternate server "
        "(vpn2.meridian.com), restart the VPN client. "
        "Issue: 'Authentication failed' - Verify credentials, check if account is locked in AD, ensure "
        "MFA device is operational and has network connectivity. "
        "Issue: Slow VPN performance - Check local internet speed (minimum 25 Mbps required), disconnect "
        "from other VPNs, close bandwidth-heavy applications. "
        "Issue: Split tunneling not working - This is by design for security. All traffic routes through "
        "the VPN when connected. Contact IT Security for exceptions."
    )

    # Chapter 5: Password and MFA
    pdf.add_page()
    pdf.section_heading("5. Password and Security Policies")

    pdf.sub_heading("5.1 Password Requirements")
    pdf.body_text(
        "Corporate passwords must meet the following requirements: Minimum 12 characters, at least one "
        "uppercase letter, at least one lowercase letter, at least one number, at least one special "
        "character (!@#$%^&*), cannot reuse any of the last 12 passwords, must be changed every 90 days. "
        "Passwords must not contain your name, username, or common dictionary words."
    )

    pdf.sub_heading("5.2 Password Reset Procedure")
    pdf.body_text(
        "Self-service password reset: Visit https://passwordreset.meridian.internal, verify your "
        "identity using your registered MFA method, set a new password meeting the requirements above. "
        "If you cannot access the self-service portal, contact the IT Help Desk at extension 5555. "
        "Identity verification will be performed using your employee ID, manager's name, and a security "
        "question. Password resets by the Help Desk take effect immediately."
    )

    pdf.sub_heading("5.3 Multi-Factor Authentication (MFA)")
    pdf.body_text(
        "MFA is mandatory for all employees and is required for: VPN connections, remote email access, "
        "cloud application logins (Salesforce, AWS, Azure), the ServiceDesk portal, and the HR portal. "
        "Supported MFA methods: Microsoft Authenticator app (preferred), hardware security key (YubiKey), "
        "SMS verification (backup only, not recommended for primary use). To register or change your MFA "
        "method, visit https://mfa.meridian.internal or contact the IT Help Desk."
    )

    # Chapter 6: Hardware Provisioning
    pdf.add_page()
    pdf.section_heading("6. Hardware Provisioning and Support")

    pdf.sub_heading("6.1 Standard Equipment")
    pdf.body_text(
        "All employees receive the following standard equipment: Laptop (Dell Latitude 5540 or MacBook "
        "Pro 14-inch, based on role requirements), 24-inch external monitor, USB-C docking station, "
        "wireless keyboard and mouse, headset with microphone (Jabra Evolve2 75). Additional equipment "
        "such as a second monitor or ergonomic accessories can be requested through the ServiceDesk portal "
        "with manager approval."
    )

    pdf.sub_heading("6.2 Equipment Replacement Cycle")
    pdf.body_text(
        "Laptops are replaced every 3 years as part of the standard refresh cycle. Monitors and peripherals "
        "are replaced on an as-needed basis. If your equipment malfunctions before the replacement cycle, "
        "submit a hardware support ticket. A loaner device will be provided within 4 business hours while "
        "your device is being repaired or replaced."
    )

    pdf.sub_heading("6.3 BYOD Policy")
    pdf.body_text(
        "Bring Your Own Device (BYOD) is permitted for mobile phones and tablets only. Personal laptops "
        "may not be used for work purposes due to security requirements. BYOD devices must be enrolled "
        "in the company's Mobile Device Management (MDM) system (Microsoft Intune) and comply with "
        "the following: Screen lock enabled with 6-digit PIN or biometric, automatic device encryption "
        "enabled, ability for IT to remotely wipe company data (not personal data), operating system "
        "must be within 2 major versions of the latest release."
    )

    pdf.output(str(output_dir / "IT_Support_Process_Guide.pdf"))
    print("  Created IT_Support_Process_Guide.pdf")


def generate_client_onboarding(output_dir: Path):
    """Generate Client_Onboarding_FAQ.pdf."""
    pdf = StyledPDF("Client Onboarding FAQ")
    pdf.alias_nb_pages()
    pdf.add_title_page("Client Onboarding FAQ", "Meridian Consulting Group - Client Services")

    # Section 1: Overview
    pdf.add_page()
    pdf.section_heading("1. Onboarding Overview")

    pdf.sub_heading("Q: What is the client onboarding process?")
    pdf.body_text(
        "A: The client onboarding process is a structured 6-phase program designed to ensure a smooth "
        "transition from contract signing to active service delivery. The phases are: (1) Welcome & "
        "Kickoff (Week 1), (2) Discovery & Requirements Gathering (Weeks 2-3), (3) Solution Design & "
        "Configuration (Weeks 4-6), (4) Data Migration & Integration (Weeks 7-9), (5) User Acceptance "
        "Testing (Weeks 10-11), and (6) Go-Live & Hypercare (Week 12+). The entire process typically "
        "takes 10-12 weeks for standard engagements."
    )

    pdf.sub_heading("Q: Who is involved in the onboarding process?")
    pdf.body_text(
        "A: Each client is assigned a dedicated onboarding team consisting of: "
        "Client Success Manager (CSM) - your primary point of contact throughout the engagement. "
        "Solution Architect - designs the technical solution based on your requirements. "
        "Project Manager - manages timelines, milestones, and deliverables. "
        "Data Migration Specialist - handles data transfer and validation. "
        "Training Coordinator - schedules and conducts user training sessions. "
        "The team is introduced during the Kickoff Meeting in Week 1."
    )

    pdf.sub_heading("Q: How long does onboarding take?")
    pdf.body_text(
        "A: Standard onboarding takes 10-12 weeks. Complex engagements (enterprise clients with custom "
        "integrations) may take 16-20 weeks. Expedited onboarding (8 weeks) is available for an "
        "additional fee and requires dedicated resources. The timeline is agreed upon during the "
        "Discovery phase and documented in the Project Charter."
    )

    # Section 2: KYC and Documentation
    pdf.add_page()
    pdf.section_heading("2. KYC and Documentation Requirements")

    pdf.sub_heading("Q: What documents are required for client onboarding?")
    pdf.body_text(
        "A: The following documents must be submitted within 5 business days of contract signing: "
        "(1) Signed Master Service Agreement (MSA), (2) Certificate of Incorporation or equivalent, "
        "(3) Tax Identification Number (TIN) or EIN documentation, (4) Authorized signatory list with "
        "specimen signatures, (5) Proof of business address (utility bill or bank statement less than "
        "3 months old), (6) Beneficial ownership declaration (for entities with 25%+ ownership), "
        "(7) AML/KYC questionnaire (provided by our Compliance team), (8) Data Processing Agreement "
        "(DPA) signed by both parties."
    )

    pdf.sub_heading("Q: What is the KYC verification process?")
    pdf.body_text(
        "A: Our KYC (Know Your Customer) process involves three levels of verification: "
        "Level 1 - Document Verification: Automated validation of submitted documents against public "
        "databases and registries. Completed within 2 business days. "
        "Level 2 - Enhanced Due Diligence: For clients in regulated industries or high-risk jurisdictions, "
        "additional checks including PEP (Politically Exposed Persons) screening and sanctions list "
        "verification. Completed within 5 business days. "
        "Level 3 - Ongoing Monitoring: Continuous monitoring of client compliance status throughout "
        "the engagement, with annual re-certification."
    )

    pdf.sub_heading("Q: What happens if documents are incomplete?")
    pdf.body_text(
        "A: If submitted documents are incomplete or require clarification, the Compliance team will "
        "notify the client's authorized contact within 1 business day. The client has 10 business days "
        "to provide the missing information. Failure to complete documentation within 30 days of contract "
        "signing may result in delayed service activation and potential contract review."
    )

    # Section 3: SLA and Service Level
    pdf.add_page()
    pdf.section_heading("3. Service Level Agreements (SLA)")

    pdf.sub_heading("Q: What SLA tiers are available?")
    pdf.body_text(
        "A: Meridian offers three SLA tiers: "
        "Silver (Standard): Business hours support (8 AM - 6 PM local time, Mon-Fri). Response time: "
        "4 hours for critical issues, 8 hours for high priority, 24 hours for medium/low. Monthly "
        "uptime guarantee: 99.5%. Included in standard pricing. "
        "Gold (Enhanced): Extended hours support (7 AM - 10 PM local time, Mon-Sat). Response time: "
        "2 hours for critical, 4 hours for high, 12 hours for medium/low. Monthly uptime guarantee: "
        "99.9%. 15% premium over standard pricing. "
        "Platinum (Premium): 24/7/365 support with dedicated support engineer. Response time: 30 minutes "
        "for critical, 1 hour for high, 4 hours for medium/low. Monthly uptime guarantee: 99.99%. "
        "30% premium over standard pricing."
    )

    pdf.sub_heading("Q: How are SLA breaches handled?")
    pdf.body_text(
        "A: SLA breach management follows a structured process: "
        "First Breach: Written notification to the client with root cause analysis and corrective action "
        "plan within 5 business days. "
        "Second Breach (within 90 days): Client receives a 5% service credit for the affected month. "
        "A formal review meeting is scheduled with the Client Success Manager. "
        "Third Breach (within 90 days): Client receives a 15% service credit. Escalation to VP of "
        "Client Services with a remediation plan and executive sponsorship. "
        "Chronic Breaches (3+ in any rolling 6-month period): Client may invoke early termination "
        "clause without penalty, as specified in the MSA."
    )

    # Section 4: Data Migration
    pdf.add_page()
    pdf.section_heading("4. Data Migration")

    pdf.sub_heading("Q: How does data migration work?")
    pdf.body_text(
        "A: Data migration follows a 4-step process: "
        "Step 1 - Data Assessment: Our Data Migration Specialist reviews your existing data sources, "
        "formats, volume, and quality. A Data Migration Plan is created with timelines and risk "
        "assessment. "
        "Step 2 - Data Mapping: Source-to-target field mapping is documented and reviewed with your "
        "team. Transformation rules are defined for data that needs reformatting or cleansing. "
        "Step 3 - Trial Migration: A test migration is performed with a representative data subset "
        "(typically 10-20% of total volume). Results are validated by your team before proceeding. "
        "Step 4 - Production Migration: Full data migration is executed during a scheduled maintenance "
        "window. Post-migration validation includes data integrity checks, record count verification, "
        "and functional testing."
    )

    pdf.sub_heading("Q: What data formats are supported?")
    pdf.body_text(
        "A: We support migration from the following formats and sources: "
        "File Formats: CSV, Excel (XLSX/XLS), JSON, XML, Parquet, SQL dumps. "
        "Databases: MySQL, PostgreSQL, SQL Server, Oracle, MongoDB. "
        "Cloud Platforms: Salesforce, HubSpot, SAP, Workday, ServiceNow via API integration. "
        "Legacy Systems: Custom integrations can be developed for proprietary systems (additional "
        "scoping and fees may apply). "
        "Maximum single-migration volume: 50 GB for standard tier, 500 GB for enterprise tier. "
        "Larger migrations require custom planning."
    )

    pdf.sub_heading("Q: What about data security during migration?")
    pdf.body_text(
        "A: Data security is paramount during the migration process: "
        "All data is encrypted in transit (TLS 1.3) and at rest (AES-256). "
        "Data transfer uses secure SFTP channels or encrypted API connections. "
        "Temporary migration environments are isolated and access-controlled. "
        "All migration data is purged from temporary environments within 30 days of go-live. "
        "Our data handling practices comply with SOC 2 Type II, ISO 27001, and GDPR requirements. "
        "A Data Processing Agreement (DPA) is signed before any data transfer begins."
    )

    # Section 5: Training
    pdf.add_page()
    pdf.section_heading("5. Training and Enablement")

    pdf.sub_heading("Q: What training is provided during onboarding?")
    pdf.body_text(
        "A: Our comprehensive training program includes: "
        "Administrator Training (8 hours): System configuration, user management, security settings, "
        "reporting, and integration management. Delivered to 2-3 designated administrators. "
        "End-User Training (4 hours per role): Role-specific training covering daily workflows, "
        "key features, and best practices. Delivered in groups of up to 20 users. "
        "Train-the-Trainer (6 hours): For clients who prefer to conduct internal training, we "
        "provide a comprehensive train-the-trainer program with all materials and certification. "
        "All training sessions are recorded and made available in your client portal for 12 months."
    )

    pdf.sub_heading("Q: How is training delivered?")
    pdf.body_text(
        "A: Training can be delivered in three formats: "
        "Virtual (Default): Live sessions via Zoom with screen sharing and interactive exercises. "
        "In-Person: On-site training at your location (travel expenses apply). Minimum 10 participants "
        "required per session. "
        "Self-Paced: Access to our Learning Management System (LMS) with video tutorials, quizzes, "
        "and hands-on labs. Available 24/7 for 12 months post-go-live. "
        "A training schedule is agreed upon during the Discovery phase and can be adjusted based on "
        "your team's availability."
    )

    # Section 6: Go-Live and Hypercare
    pdf.add_page()
    pdf.section_heading("6. Go-Live and Hypercare")

    pdf.sub_heading("Q: What are the go-live criteria?")
    pdf.body_text(
        "A: The following criteria must be met before go-live approval: "
        "(1) All data migration completed and validated by the client team. "
        "(2) User Acceptance Testing (UAT) signed off with no critical or high-severity defects. "
        "(3) All administrator and end-user training completed. "
        "(4) Production environment configured and performance-tested. "
        "(5) Runbook and escalation procedures documented and distributed. "
        "(6) Go-live checklist completed and signed by both the client sponsor and Meridian PM. "
        "(7) Rollback plan documented and tested. "
        "A Go/No-Go meeting is held 3 business days before the planned go-live date."
    )

    pdf.sub_heading("Q: What is the hypercare period?")
    pdf.body_text(
        "A: The hypercare period is an intensive 4-week support phase immediately following go-live. "
        "During this period: "
        "Your dedicated onboarding team remains assigned and actively monitors system health. "
        "Daily stand-up calls (15 minutes) are held during Week 1 to address any emerging issues. "
        "SLA response times are reduced by 50% from your standard tier. "
        "A dedicated Slack/Teams channel is maintained for real-time communication. "
        "Weekly status reports are provided with system health metrics, user adoption rates, and "
        "issue summaries. "
        "After the hypercare period, support transitions to your assigned SLA tier and the regular "
        "support team. A formal handoff meeting is conducted."
    )

    pdf.sub_heading("Q: What if we need to delay go-live?")
    pdf.body_text(
        "A: Go-live can be delayed if critical readiness criteria are not met. The process is: "
        "Notify your Project Manager and Client Success Manager immediately. "
        "A revised timeline is developed within 3 business days. "
        "Delays of up to 2 weeks are accommodated at no additional cost. "
        "Delays beyond 2 weeks may incur resource holding fees (as specified in the MSA). "
        "If the delay is caused by Meridian (e.g., unresolved critical defects), no fees apply and "
        "additional credits may be provided per the SLA terms."
    )

    # Section 7: Post-Onboarding
    pdf.add_page()
    pdf.section_heading("7. Post-Onboarding Support")

    pdf.sub_heading("Q: What support is available after onboarding?")
    pdf.body_text(
        "A: After the onboarding and hypercare phases, clients receive: "
        "Ongoing Technical Support: Based on your selected SLA tier (Silver, Gold, or Platinum). "
        "Quarterly Business Reviews (QBRs): Strategic review meetings with your CSM to discuss usage "
        "metrics, ROI, and future roadmap alignment. "
        "Product Updates: Access to new features and enhancements as they are released, with change "
        "notes and updated documentation. "
        "Client Community: Access to the Meridian Client Community portal for knowledge sharing, "
        "best practices, and peer networking. "
        "Annual Training Refresher: One complimentary training session per year to cover new features "
        "and reinforce best practices."
    )

    pdf.sub_heading("Q: How do I request changes after onboarding?")
    pdf.body_text(
        "A: Post-onboarding changes are handled through the Change Request process: "
        "Minor Changes (configuration tweaks, user additions): Submit through the support portal. "
        "Handled within your SLA response times at no additional cost. "
        "Moderate Changes (new integrations, workflow modifications): Submit a Change Request form "
        "through your CSM. Scoped and quoted within 5 business days. "
        "Major Changes (new modules, significant customization): Requires a new Statement of Work "
        "(SOW) with separate project scoping, timeline, and pricing."
    )

    pdf.output(str(output_dir / "Client_Onboarding_FAQ.pdf"))
    print("  Created Client_Onboarding_FAQ.pdf")


if __name__ == "__main__":
    output_dir = Path(__file__).parent / "documents"
    output_dir.mkdir(exist_ok=True)

    print("Generating sample documents...")
    generate_hr_policy(output_dir)
    generate_it_support(output_dir)
    generate_client_onboarding(output_dir)
    print("Done! All 3 documents created in:", output_dir)
