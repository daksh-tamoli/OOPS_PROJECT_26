import os
import smtplib
import uuid
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional, Dict, Any


class EmailNotification:
    def __init__(
        self,
        to_addresses: List[str],
        subject: str,
        body_html: str,
        body_text: str,
        notification_type: str,
        notification_id: Optional[str] = None,
        sent_at: Optional[datetime] = None,
        status: str = "DELIVERED_OUTBOX",
        smtp_error: Optional[str] = None
    ):
        self.id = notification_id or f"mail-{uuid.uuid4().hex[:8]}"
        self.to_addresses = to_addresses
        self.subject = subject
        self.body_html = body_html
        self.body_text = body_text
        self.notification_type = notification_type
        self.sent_at = sent_at or datetime.now(timezone.utc)
        self.status = status
        self.smtp_error = smtp_error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "to": self.to_addresses,
            "subject": self.subject,
            "body_html": self.body_html,
            "body_text": self.body_text,
            "type": self.notification_type,
            "sent_at": self.sent_at.isoformat(),
            "status": self.status,
            "smtp_error": self.smtp_error
        }


class EmailService:
    """Enterprise Notification & SMTP Delivery Service (Singleton / Outbox Pattern)."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EmailService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self.outbox: List[EmailNotification] = []
        self._initialized = True

    @property
    def smtp_configured(self) -> bool:
        host = os.environ.get("SMTP_HOST")
        return bool(host and host.strip())

    def send_email(
        self,
        to_addresses: List[str],
        subject: str,
        body_html: str,
        body_text: str = "",
        notification_type: str = "GENERAL"
    ) -> EmailNotification:
        if not to_addresses:
            to_addresses = ["it-notifications@enterprise.local"]

        status = "DELIVERED_OUTBOX"
        smtp_error = None

        # Attempt Real SMTP if configured in environment
        smtp_host = os.environ.get("SMTP_HOST")
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ.get("SMTP_USER")
        smtp_pass = os.environ.get("SMTP_PASSWORD")
        smtp_from = os.environ.get("SMTP_FROM", "noreply@itsm.local")

        if smtp_host and smtp_host.strip():
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = smtp_from
                msg["To"] = ", ".join(to_addresses)

                if body_text:
                    msg.attach(MIMEText(body_text, "plain"))
                if body_html:
                    msg.attach(MIMEText(body_html, "html"))

                with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                    server.starttls()
                    if smtp_user and smtp_pass:
                        server.login(smtp_user, smtp_pass)
                    server.sendmail(smtp_from, to_addresses, msg.as_string())
                status = "DELIVERED_SMTP"
            except Exception as e:
                status = "DELIVERED_OUTBOX_SMTP_FAILED"
                smtp_error = str(e)

        notification = EmailNotification(
            to_addresses=to_addresses,
            subject=subject,
            body_html=body_html,
            body_text=body_text or subject,
            notification_type=notification_type,
            status=status,
            smtp_error=smtp_error
        )
        self.outbox.insert(0, notification)
        # Cap outbox history at 200 items
        if len(self.outbox) > 200:
            self.outbox.pop()

        return notification

    def get_all(self, recipient: Optional[str] = None) -> List[Dict[str, Any]]:
        if not recipient:
            return [n.to_dict() for n in self.outbox]
        recip_clean = recipient.strip().lower()
        return [
            n.to_dict() for n in self.outbox
            if any(recip_clean in addr.lower() for addr in n.to_addresses)
        ]

    # Helper HTML Generators
    def send_welcome_email(self, email: str, full_name: str, role: str, department: str = "General") -> EmailNotification:
        subject = f"Welcome to I-ITSM Enterprise Platform, {full_name}"
        html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0c0c0c; color: #f5f5f5; border: 1px solid #262626; border-radius: 12px; overflow: hidden; padding: 28px;">
            <div style="border-bottom: 1px solid #262626; padding-bottom: 16px; margin-bottom: 20px;">
                <span style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #f97316; font-weight: 700;">I-ITSM Platform</span>
                <h1 style="font-size: 20px; font-weight: 700; color: #ffffff; margin: 8px 0 0 0;">Account Registered Successfully</h1>
            </div>
            <p style="font-size: 14px; line-height: 1.6; color: #a3a3a3;">
                Hello <strong>{full_name}</strong>, your account has been provisioned on the Enterprise Incident Management Platform.
            </p>
            <div style="background: #171717; border: 1px solid #262626; border-radius: 8px; padding: 16px; margin: 20px 0;">
                <div style="font-size: 12px; color: #737373; margin-bottom: 4px;">REGISTERED EMAIL</div>
                <div style="font-size: 14px; color: #ffffff; font-weight: 600; font-family: monospace;">{email}</div>
                <div style="display: flex; gap: 20px; margin-top: 12px;">
                    <div>
                        <div style="font-size: 11px; color: #737373;">SYSTEM ROLE</div>
                        <div style="font-size: 13px; color: #f97316; font-weight: 700;">{role}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #737373;">DEPARTMENT</div>
                        <div style="font-size: 13px; color: #ffffff; font-weight: 600;">{department}</div>
                    </div>
                </div>
            </div>
            <p style="font-size: 13px; color: #a3a3a3; line-height: 1.5;">
                You can now log in, submit incident requests, track service availability, and verify ticket resolutions.
            </p>
            <div style="border-top: 1px solid #262626; margin-top: 24px; padding-top: 14px; font-size: 11px; color: #525252;">
                Enterprise ITSM Automated Notification Service &bull; BITS Pilani OOPS Project
            </div>
        </div>
        """
    def send_verification_code_email(self, email: str, code: str, full_name: str) -> EmailNotification:
        subject = f"Your Verification Code: {code} - I-ITSM Account Registration"
        html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 580px; margin: 0 auto; background: #0c0c0c; color: #f5f5f5; border: 1px solid #262626; border-radius: 12px; overflow: hidden; padding: 28px;">
            <div style="border-bottom: 1px solid #262626; padding-bottom: 16px; margin-bottom: 20px;">
                <span style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #f97316; font-weight: 700;">Account Security Verification</span>
                <h1 style="font-size: 20px; font-weight: 700; color: #ffffff; margin: 8px 0 0 0;">Verify Your Corporate Email</h1>
            </div>
            <p style="font-size: 14px; line-height: 1.6; color: #a3a3a3;">
                Hello <strong>{full_name}</strong>, please use the following one-time verification code to complete your account registration on the I-ITSM Platform:
            </p>
            <div style="background: #171717; border: 2px dashed #f97316; border-radius: 10px; padding: 20px; margin: 24px 0; text-align: center;">
                <div style="font-size: 12px; color: #737373; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; margin-bottom: 8px;">6-Digit OTP Verification Code</div>
                <div style="font-size: 36px; font-weight: 800; color: #f97316; letter-spacing: 8px; font-family: monospace;">{code}</div>
                <div style="font-size: 11px; color: #737373; margin-top: 8px;">Code expires in 10 minutes &bull; Do not share this code with anyone</div>
            </div>
            <p style="font-size: 13px; color: #737373; line-height: 1.5;">
                If you did not request this account registration, please ignore this email or contact your IT security administrator immediately.
            </p>
            <div style="border-top: 1px solid #262626; margin-top: 24px; padding-top: 14px; font-size: 11px; color: #525252;">
                Enterprise ITSM Automated Security Service &bull; BITS Pilani OOPS Project
            </div>
        </div>
        """
        text = f"Your I-ITSM verification code is: {code}. It expires in 10 minutes."
        return self.send_email([email], subject, html, text, "EMAIL_VERIFICATION")

    def send_incident_created_email(self, incident_id: str, title: str, priority: str, service_name: str, reporter_email: str, response_deadline: str) -> EmailNotification:
        subject = f"[{priority}] Incident Logged: {incident_id} - {title}"
        html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0c0c0c; color: #f5f5f5; border: 1px solid #262626; border-radius: 12px; overflow: hidden; padding: 28px;">
            <div style="border-bottom: 1px solid #262626; padding-bottom: 16px; margin-bottom: 20px;">
                <span style="display: inline-block; background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase;">{priority} PRIORITY</span>
                <h1 style="font-size: 18px; font-weight: 700; color: #ffffff; margin: 10px 0 4px 0;">{incident_id}: {title}</h1>
                <div style="font-size: 12px; color: #737373;">Affected Service: <strong style="color: #ffffff;">{service_name}</strong></div>
            </div>
            <p style="font-size: 14px; line-height: 1.6; color: #a3a3a3;">
                Your incident has been acknowledged and registered in the IT Service Management orchestrator.
            </p>
            <div style="background: #171717; border: 1px solid #262626; border-radius: 8px; padding: 14px; margin: 18px 0;">
                <div style="font-size: 11px; color: #737373; text-transform: uppercase; font-weight: 700; margin-bottom: 4px;">SLA Response Target</div>
                <div style="font-size: 14px; color: #f97316; font-weight: 700;">{response_deadline}</div>
                <div style="font-size: 12px; color: #a3a3a3; margin-top: 6px;">A qualified technician has been notified for investigation.</div>
            </div>
            <div style="border-top: 1px solid #262626; margin-top: 24px; padding-top: 14px; font-size: 11px; color: #525252;">
                Enterprise ITSM Automated Notification Service &bull; BITS Pilani OOPS Project
            </div>
        </div>
        """
        text = f"Incident {incident_id} logged: {title}. Priority: {priority}. Response target: {response_deadline}."
        return self.send_email([reporter_email], subject, html, text, "INCIDENT_CREATED")

    def send_incident_assigned_email(self, incident_id: str, title: str, priority: str, technician_name: str, technician_email: str) -> EmailNotification:
        subject = f"[ASSIGNED] Incident {incident_id}: {title}"
        html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0c0c0c; color: #f5f5f5; border: 1px solid #262626; border-radius: 12px; overflow: hidden; padding: 28px;">
            <div style="border-bottom: 1px solid #262626; padding-bottom: 16px; margin-bottom: 20px;">
                <span style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 700;">Ticket Assignment Dispatch</span>
                <h1 style="font-size: 18px; font-weight: 700; color: #ffffff; margin: 8px 0 0 0;">{incident_id}: {title}</h1>
            </div>
            <p style="font-size: 14px; line-height: 1.6; color: #a3a3a3;">
                Hello <strong>{technician_name}</strong>, this ticket has been routed to you based on your skill qualifications and current workload capacity.
            </p>
            <div style="background: #171717; border: 1px solid #262626; border-radius: 8px; padding: 14px; margin: 18px 0;">
                <div style="font-size: 12px; color: #737373;">PRIORITY: <strong style="color: #f97316;">{priority}</strong></div>
                <div style="font-size: 12px; color: #a3a3a3; margin-top: 4px;">Please review diagnostic details and acknowledge the ticket to halt SLA escalation timers.</div>
            </div>
            <div style="border-top: 1px solid #262626; margin-top: 24px; padding-top: 14px; font-size: 11px; color: #525252;">
                Enterprise ITSM Automated Notification Service &bull; BITS Pilani OOPS Project
            </div>
        </div>
        """
        text = f"Incident {incident_id} ({title}) has been assigned to technician {technician_name}."
        return self.send_email([technician_email], subject, html, text, "INCIDENT_ASSIGNED")
