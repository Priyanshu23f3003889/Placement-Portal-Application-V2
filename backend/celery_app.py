from time import sleep

from celery import Celery
from datetime import timedelta
from mail import sendEmail
from celery.schedules import crontab
from database.models import *
from datetime import datetime
from app import app
from celery_instance import celery

@celery.task()
def send_csv(toEmail, csv_data):
    sleep(1)
    sendEmail(toEmail, 'Student Application Data', body=csv_data, type='csv')
    return "csv email sent"
    

@celery.task()
def daily_reminder():
    with app.app_context():
        companies=db.session.execute(db.select(Company).where(Company.isApproved)).scalars().all()
        drives = []

        for c in companies:
            drives.extend(list(filter(lambda x: x.status == DriveStatus.APPROVED and datetime.strptime(str(x.deadline)[:19], "%Y-%m-%d %H:%M:%S")>= datetime.now(), c.drives )))

        if not drives:
            return "No Reminders Found"
            
        body = f"""
        <html>
            <style>table, th, td {{
              border: 1px solid black;
              border-collapse: collapse;
              padding : 5px;
            }}</style>
            <body>
                <h1 style="color: red;">Deadline Reminder!</h1>
                <table>
                  <thead>
                    <tr>
                      <th>Drive ID</th>
                      <th>Company</th>
                      <th>Job Title</th>
                      <th>Deadline</th>
                    </tr>
                  </thead>
                  <tbody>
                    {"\n".join([f'<tr><td>{d.id}</td><td>{d.company.name}</td><td>{d.jobTitle}</td><td>{d.deadline}</td></tr>' for d in drives])}
                  </tbody>
                </table>

            </body>
            </html>
        """
        sendEmail('students@email.com', 'Deadline Reminder', body, 'html')
    return " Daily Reminder sent"

@celery.task()
def monthly_report():
    with app.app_context():
        companies=db.session.execute(db.select(Company).where(Company.isApproved)).scalars().all()
        drives = []

        for c in companies:
            drives.extend(list(filter(lambda x: x.status == DriveStatus.CLOSED and datetime.today().replace(day=1)-timedelta(days=1) < datetime.strptime(str(x.deadline)[:19], "%Y-%m-%d %H:%M:%S") < datetime.now(), c.drives )))

        body = f"""
        <html>
            <style>table, th, td {{
              border: 1px solid black;
              border-collapse: collapse;
              padding : 5px;
            }}</style>
            <body>
                <h1 style="color: blue;">Monthly Report</h1>
                <table>
                  <thead>
                    <tr>
                      <th>Drive ID</th>
                      <th>Company</th>
                      <th>Job Title</th>
                      <th>Applied</th>
                      <th>Selected</th>
                    </tr>
                  </thead>
                  <tbody>
                    {"\n".join([f'<tr><td>{d.id}</td><td>{d.company.name}</td><td>{d.jobTitle}</td><td>{len(d.applications)}</td><td>{len(list(filter(lambda x: x.status == ApplicationStatus.SELECTED,d.applications)))}</td></tr>' for d in drives])}
                  </tbody>
                </table>
                <br>
                <div><strong>Total Drives : </strong>{len(drives)}<br> <strong>Total Applied : </strong>{sum([len(d.applications) for d in drives])} <br><strong>Total Selected : </strong>{sum([len(list(filter(lambda x: x.status == ApplicationStatus.SELECTED,d.applications))) for d in drives])}</div>
            </body>
            </html>
        """
        sendEmail('admin@email.com', 'Monthly Report', body, 'html')
    return "Monthly Report sent"

celery.conf.beat_schedule = {
    'send-daily-reminder' : {
        'task' : 'celery_app.daily_reminder',
        'schedule' : timedelta(minutes=3), # crontab(minute=0, hour=17)
    },
    'send-monthly-report' : {
        'task' : 'celery_app.monthly_report',
        'schedule' : timedelta(minutes=5), # crontab(minute=0, hour=0, day_of_month='1')
    }
}
