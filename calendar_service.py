import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from icalendar import Calendar, Event, vCalAddress
from datetime import datetime
import pytz

def send_email_with_invite(sender_email, sender_password, recipient_email, subject, body, event_details):
    # Create the email header
    msg = MIMEMultipart('mixed')
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Create the email body
    msg.attach(MIMEText(body, 'plain'))

    # Create an iCalendar event
    cal = Calendar()
    cal.add('prodid', '-//My calendar product//example.com//')
    cal.add('version', '2.0')
    cal.add('method', 'REQUEST')

    event = Event()
    event.add('summary', event_details['summary'])
    event.add('dtstart', event_details['start'])
    event.add('dtend', event_details['end'])
    event.add('dtstamp', datetime.now(pytz.timezone('America/Chicago')))
    event.add('location', event_details['location'])
    event.add('description', event_details['description'])
    event['uid'] = 'kowligi1998@gmail.com'

    organizer = vCalAddress('MAILTO:' + sender_email)
    organizer.params['cn'] = 'LibSeat'
    organizer.params['role'] = 'CHAIR'
    event['organizer'] = organizer

    attendee = vCalAddress('MAILTO:' + recipient_email)
    attendee.params['cn'] = 'Recipient'
    attendee.params['RSVP'] = 'TRUE'
    event.add('attendee', attendee)

    cal.add_component(event)

    # Attach the calendar event to the email
    ical_attach = MIMEBase('text', 'calendar', method='REQUEST', name='invite.ics')
    ical_attach.set_payload(cal.to_ical())
    encoders.encode_base64(ical_attach)
    ical_attach.add_header('Content-Disposition', 'attachment; filename="invite.ics"')

    msg.attach(ical_attach)

    # Send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
