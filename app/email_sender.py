import os

from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

from app import schema

templates_folder_path = './app/templates/email'
conf = ConnectionConfig(
    MAIL_USERNAME=os.environ["MAIL_USERNAME"],
    MAIL_PASSWORD=os.environ["MAIL_PASSWORD"],
    MAIL_FROM=os.environ["MAIL_FROM"],
    MAIL_PORT=os.environ["MAIL_PORT"],
    MAIL_SERVER=os.environ["MAIL_SERVER"],
    MAIL_FROM_NAME=os.environ["MAIL_FROM_NAME"],
    MAIL_TLS=os.environ["MAIL_TLS"],
    MAIL_SSL=os.environ["MAIL_SSL"],
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=templates_folder_path
)


async def _send_static_html_email_async(subject: str, email_address: str, template_name: str):
    html = open(templates_folder_path + '/' + template_name).read()

    message = MessageSchema(
        subject=subject,
        recipients=[EmailStr(email_address)],
        html=html,
        subtype='html',

    )
    fm = FastMail(conf)

    await fm.send_message(message)


async def send_email_async(subject: str, email_params: schema.EmailSchema, template_name: str):
    message = MessageSchema(
        subject=subject,
        recipients=email_params.dict().get("email"),
        template_body=email_params.dict().get("body"),
        subtype='html',

    )

    fm = FastMail(conf)

    await fm.send_message(message, template_name=template_name)


def send_email_background(background_tasks: BackgroundTasks, subject: str, email_to: EmailStr, body_email: dict,
                          template_name: str):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=body_email,
        subtype='html',
    )

    fm = FastMail(conf)

    background_tasks.add_task(
        fm.send_message, message, template_name=template_name)


async def send_verification_confirm_mail(email):
    await _send_static_html_email_async("KYC verification successful", email, template_name='email_kyc_confirm_sk.html')
    return
