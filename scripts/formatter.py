# formatter.py
from jinja2 import Environment, FileSystemLoader
import datetime

def format_html(repos_data):
    env = Environment(loader=FileSystemLoader('templates/'))
    template = env.get_template('email_template.html')
    report_date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    html_output = template.render(repos=repos_data, report_date=report_date_str)
    return html_output