import json
from django.contrib import messages
import urllib.request
import ssl
from django.core import mail
from django.core.mail import EmailMessage
import requests
from django.db import connection
from interviews.models import Mails
from django.template.loader import render_to_string
from candidates.models import Candidates
from users.models import User
from users.serializers import UserSerializer
from staffingapp.settings import GLOBAL_ROLE, EMAIL_FROM_USER
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def get_datetime_from_date(date):
    logger.info('Date received from request: ' + str(date))
    if date is not None and len(date) > 10:
        dateSplit = date.split(" ")
        date = dateSplit[0]
		
    logger.info('Date modified from request: ' + str(date))
    updated_submission_date = date + 'T' + str(datetime.now().time()) + 'Z'
    return updated_submission_date


def getCurrentTime():
    current_time = datetime.now().time()
    return current_time


def sendRTRMail(request, obj):
    connection = mail.get_connection()
    # Manually open the connection
    connection.open()
    messages.add_message(request, messages.INFO, 'RTR Email Successfully Sent')
    print(obj)
    recipient_list = [obj.email]
    email = mail.EmailMessage(subject=obj.subject, body=obj.message, from_email=EMAIL_FROM_USER, to=recipient_list)
    email.content_subtype = 'html'
    email.cc = [obj.cc_email]
    email.attach_file('.' + str(obj.jd))
    email.send()
    connection.close()

    return messages


def sendSubmissionMail(request, obj):
    connection = mail.get_connection()
    # Manually open the connection
    connection.open()
    logger.info('Mail Object ...........' + str(obj))
    messages.add_message(request, messages.INFO, 'Submission Email Successfully Sent')
    print(obj)
    recipient_list = [obj.email]
    email = mail.EmailMessage(subject=obj.subject, body=obj.message, from_email=EMAIL_FROM_USER, to=recipient_list)
    email.content_subtype = 'html'
    email.cc = obj.cc_email
    email.send()
    connection.close()
    logger.info('Mail Successfully Send ...........')
    return messages


def sendMail(request, obj):
    connection = mail.get_connection()
    # Manually open the connection
    connection.open()
    messages.add_message(request, messages.INFO, 'Email Successfully Sent')
    # print(json.dumps(obj))
    print(obj.email)
    recipient_list = [obj.email]
    email = mail.EmailMessage(subject=obj.subject, body=obj.message, from_email=EMAIL_FROM_USER, to=recipient_list)
    if obj.resume != None and obj.resume != '':
        email.attach_file('.' + str(obj.resume))
    email.content_subtype = 'html'
    email.cc = [obj.cc_email]
    res = email.send()
    # print(res)
    connection.close()
    return messages


# def sendIndiviualMail(request , obj):
#     msg = MailerMessage()
#     msg.subject = obj.subject
#     msg.to_address = obj.email_to
#     msg.from_address = obj.email_from
#     msg.html_content = obj.body
#     msg.cc_address = obj.cc_email
#     msg.bcc_address = obj.bcc_email
#     photo_one = File(open('media/'+str(obj.attachment) ,'rb'))
#     msg.add_attachment(photo_one)
#     #msg.add_attachment('media/'+obj.attachment)
#     msg.save()
#     """user_recipient_list = [obj.email_to]
#     bcc_list = obj.bcc_emails
#     cc_list = obj.cc_emails
#     email = EmailMultiAlternatives(obj.subject, obj.body , obj.email_from, user_recipient_list, bcc=bcc_list, cc=cc_list)
#     email.attach_file('media/' + str(obj.attachment))
#     email.content_subtype = 'html'
#     email.send()"""
#
#     return messages

def generate_doc(id):
    conn = requests.post('https://server.opallius.com/phpword/samples/rtr_doc.php?rtr_id=' + str(id), json=None,
                         headers=None, verify=False)
    # print(conn.content.decode("utf-8"))
    print(conn.status_code)
    if conn.status_code == 200:
        ssl._create_default_https_context = ssl._create_unverified_context
        with urllib.request.urlopen('https://server.opallius.com/phpword/samples/results/rtr_doc.docx') as url:
            s = url.read()
            # print(s)
        return s


def sendCandidateBDMMail(request, obj):
    connection = mail.get_connection()
    # Manually open the connection
    connection.open()
    logger.info('Mail Object ...........' + str(obj))
    recipient_list = [obj.email]
    email = EmailMessage(subject=obj.subject, body=obj.message, from_email=EMAIL_FROM_USER,
                         to=recipient_list)
    email.content_subtype = 'html'
    if obj.resume is not None and str(obj.resume) != '':
        logger.info("Attached  Resume File: " + str(obj.resume) )
        email.attach_file('media/' + str(obj.resume))
    else:
        logger.info("Attached Resume File not found: " + str(obj.resume))
    email.cc = obj.cc_email
    email.send()
    logger.info('Mail Successfully Send ...........')
    return messages


def sendBDMMail(request, id, stage, job_id, submission_date, notes):
    candObj = User.objects.get(pk=request.user.id)
    serializeObj = UserSerializer(candObj)
    groups = dict(serializeObj.data)
    userGroupDict = None
    userGroup = None
    queryset = None
    if len(groups['groups']) > 0:
        userGroupDict = dict(groups['groups'][0])
    if userGroupDict is not None:
        userGroup = userGroupDict['name']
    print(userGroup)
    uid = str(request.user.id).replace("-", "")
    print(uid)

    if id is not None and stage is not None and job_id is not None and submission_date is not None:

        candidate_id = str(id).replace('UUID', ''). \
            replace('(\'', '').replace('\')', '').replace('-', '')
        job_id = str(job_id).replace('UUID', ''). \
            replace('(\'', '').replace('\')', '').replace('-', '')

        cursor = connection.cursor()
        cursor.execute(
            "SELECT resume , remarks,first_name,last_name,primary_phone_number,primary_email,min_salary,min_rate,max_rate,"
            "current_location,visa,open_for_relocation,total_experience,qualification,total_experience_in_usa,any_offer_in_hand,created_by_id ,max_salary, remarks, employer_name, engagement_type, company_name, employer_email, employer_phone_number from osms_candidates WHERE id =%s",
            [candidate_id])
        candidate = cursor.fetchone()

        cursor.execute("SELECT job_title , created_by_id ,location ,job_id  FROM osms_job_description WHERE id=%s",
                       [job_id])

        jd = cursor.fetchone()
        cursor.execute("SELECT first_name , last_name , email, country FROM users_user WHERE id=%s",
                       [jd[1]])
        BDM = cursor.fetchone()

        cursor.execute("SELECT first_name , last_name , email , created_by_id, country FROM users_user WHERE id=%s",
                       [candidate[16]])
        recruiter = cursor.fetchone()

        cursor.execute("SELECT first_name , last_name , email , created_by_id, country FROM users_user WHERE id=%s",
                       [recruiter[3]])
        recruiter_manager = cursor.fetchone()

        cursor.execute("SELECT resume , driving_license , offer_letter , passport , rtr , salary_slip , i94_document"
                       ", visa_copy , educational_document FROM osms_candidates_repositery WHERE candidate_name_id = %s",
                       [candidate_id])
        repo = cursor.fetchone()
        if repo is not None:
            logger.info('Repo Created ...........')
            context_email1 = {'BDM_name': BDM[0],
                              'sender_name': request.user.first_name + ' ' + request.user.last_name,
                              'job_title': jd[0],
                              'notes': notes,
                              'candidate_info': {"first_name": candidate[2],
                                                 "last_name": candidate[3],
                                                 "primary_phone_number": candidate[4],
                                                 "primary_email": candidate[5],
                                                 "min_salary": candidate[6],
                                                 "max_salary": candidate[17],
                                                 "min_rate": candidate[7],
                                                 "max_rate": candidate[8],
                                                 "current_location": candidate[9],
                                                 "visa": candidate[10],
                                                 "stage": stage,
                                                 "open_for_relocation": candidate[11],
                                                 "total_experience": candidate[12],
                                                 "qualification": candidate[13],
                                                 "total_experience_in_usa": candidate[14],
                                                 "any_offer_in_hand": candidate[15],
                                                 "job_id": jd[3],
                                                 "updated_by": request.user.first_name + ' ' + request.user.last_name,
                                                 "submission_date": submission_date,
                                                 "remarks": candidate[18],
                                                 "employer_name": candidate[19],
                                                 "engagement_type": candidate[20],
                                                 "company_name": candidate[21],
                                                 "employer_email": candidate[22],
                                                 "employer_phone_number": candidate[23]
                                                 },
                              'repo_details': {"resume": repo[0],
                                               "driving_license": repo[1],
                                               "offer_letter": repo[2],
                                               "passport": repo[3],
                                               "rtr": repo[4],
                                               "salary_slip": repo[5],
                                               "i94_document": repo[6],
                                               "visa_copy": repo[7],
                                               "educational_document": repo[8]
                                               }
                              }

        else:
            logger.info('No Repo Created ...........')
            context_email1 = {'BDM_name': BDM[0],
                              'sender_name': request.user.first_name + ' ' + request.user.last_name,
                              'job_title': jd[0],
                              'notes': notes,
                              'candidate_info': {"first_name": candidate[2],
                                                 "last_name": candidate[3],
                                                 "primary_phone_number": candidate[4],
                                                 "primary_email": candidate[5],
                                                 "min_salary": candidate[6],
                                                 "max_salary": candidate[17],
                                                 "min_rate": candidate[7],
                                                 "max_rate": candidate[8],
                                                 "current_location": candidate[9],
                                                 "visa": candidate[10],
                                                 "stage": stage,
                                                 "open_for_relocation": candidate[11],
                                                 "total_experience": candidate[12],
                                                 "qualification": candidate[13],
                                                 "total_experience_in_usa": candidate[14],
                                                 "any_offer_in_hand": candidate[15],
                                                 "job_id": jd[3],
                                                 "updated_by": request.user.first_name + ' ' + request.user.last_name,
                                                 "submission_date": submission_date,
                                                 "remarks": candidate[18],
                                                 "employer_name": candidate[19],
                                                 "engagement_type": candidate[20],
                                                 "company_name": candidate[21],
                                                 "employer_email": candidate[22],
                                                 "employer_phone_number": candidate[23]
                                                 }
                              }

        mail = Mails()
        mail.subject = 'Submission: ' + candidate[2] + ' ' + candidate[3] \
                       + ' for ' + jd[0] + ' ' + jd[2]
        mail.from_email = request.user.email.strip()
        mail.email = BDM[2].strip()
        mail.jd = None
        if stage.strip() == 'Submission':
            mail.resume = candidate[0]
        else:
            mail.resume = None
        mail.message = render_to_string('candidate_submission_to_BDM.html', context_email1)
        mail.condidate_email = None

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            setattr(mail, 'cc_email', [request.user.email.strip(), recruiter_manager[2].strip(), recruiter[2].strip(),
                                       'recsub@opallios.com'])
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            if BDM[3].strip() == 'India':
                setattr(mail, 'cc_email', [recruiter_manager[2].strip(), recruiter[2].strip(), 'recsub@opallios.com',
                                           'vibhuti@opallioslabs.com'])
            else:
                setattr(mail, 'cc_email', [recruiter_manager[2].strip(), recruiter[2].strip(), 'recsub@opallios.com'])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            if recruiter_manager[4].strip() == 'India':
                setattr(mail, 'cc_email', [request.user.email.strip(), recruiter[2].strip(), 'recsub@opallios.com',
                                           'vibhuti@opallioslabs.com'])
            else:
                setattr(mail, 'cc_email', [request.user.email.strip(), recruiter[2].strip(), 'recsub@opallios.com'])

        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            if recruiter[4].strip() == 'India':
                setattr(mail, 'cc_email',
                        [request.user.email.strip(), recruiter_manager[2].strip(), 'recsub@opallios.com',
                         'vibhuti@opallioslabs.com'])
            else:
                setattr(mail, 'cc_email',
                        [request.user.email.strip(), recruiter_manager[2].strip(), 'recsub@opallios.com'])

        elif userGroup is None or userGroup == '':
            setattr(mail, 'cc_email', [])

        sendCandidateBDMMail(request, mail)


def sendClientMail(request, candidate_name_id, job_id):
    candObj = User.objects.get(pk=request.user.id)
    serializeObj = UserSerializer(candObj)
    groups = dict(serializeObj.data)
    userGroupDict = None
    userGroup = None
    queryset = None
    if len(groups['groups']) > 0:
        userGroupDict = dict(groups['groups'][0])
    if userGroupDict is not None:
        userGroup = userGroupDict['name']
    print(userGroup)
    uid = str(request.user.id).replace("-", "")
    print(uid)

    if candidate_name_id is not None and job_id is not None:

        candidate_id = str(candidate_name_id).replace('UUID', ''). \
            replace('(\'', '').replace('\')', '').replace('-', '')

        job_id = str(job_id).replace('UUID', ''). \
            replace('(\'', '').replace('\')', '').replace('-', '')

        cursor = connection.cursor()
        cursor.execute(
            "SELECT resume , remarks ,first_name,last_name,primary_phone_number,primary_email,min_salary,min_rate,"
            "current_location,visa,open_for_relocation,total_experience,qualification,total_experience_in_usa,any_offer_in_hand,created_by_id,max_salary from osms_candidates WHERE id =%s",
            [candidate_id])
        candidate = cursor.fetchone()

        cursor.execute(
            "SELECT client_name_id , job_title , location ,min_rate , max_rate,created_by_id , min_salary , max_salary from osms_job_description WHERE id=%s",
            [job_id])
        jd = cursor.fetchone()

        cursor.execute("SELECT first_name , last_name , email FROM users_user WHERE id=%s",
                       [jd[5]])
        BDM = cursor.fetchone()

        cursor.execute("SELECT first_name , last_name , email , created_by_id FROM users_user WHERE id=%s",
                       [candidate[15]])
        recruiter = cursor.fetchone()

        cursor.execute("SELECT first_name , last_name , email , created_by_id FROM users_user WHERE id=%s",
                       [recruiter[3]])
        recruiter_manager = cursor.fetchone()

        cursor.execute("SELECT first_name ,primary_email from osms_clients WHERE id=%s", [jd[0]])
        client = cursor.fetchone()

        context_email = {'BDM_name': client[0],
                         'sender_name': request.user.first_name + ' ' + request.user.last_name,
                         'job_title': jd[1],
                         'candidate_info': {"first_name": candidate[2],
                                            "last_name": candidate[3],
                                            "primary_phone_number": candidate[4],
                                            "primary_email": candidate[5],
                                            "min_salary": jd[6],
                                            "max_salary": jd[7],
                                            "min_rate": jd[3],
                                            "max_rate": jd[4],
                                            "current_location": candidate[8],
                                            "visa": candidate[9],
                                            "open_for_relocation": candidate[10],
                                            "total_experience": candidate[11],
                                            "qualification": candidate[12],
                                            "total_experience_in_usa": candidate[13],
                                            "any_offer_in_hand": candidate[14]
                                            }
                         }

        mail = Mails()
        mail.subject = mail.subject = 'Submission: ' + candidate[2] + ' ' + candidate[3] \
                                      + ' for ' + jd[1] + ' ' + jd[2]
        mail.from_email = request.user.email
        mail.email = client[1]
        # mail.email = 'pandeym@cresitatech.com'
        mail.resume = None
        mail.jd = candidate[0]
        mail.message = render_to_string('candidates_submission.html', context_email)
        mail.condidate_email = None

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            setattr(mail, 'cc_email', [request.user.email.strip(), 'recsub@opallios.com'])
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            setattr(mail, 'cc_email', [request.user.email.strip(), recruiter_manager[2].strip(), recruiter[2].strip(),
                                       'recsub@opallios.com'])
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            setattr(mail, 'cc_email',
                    [request.user.email.strip(), BDM[2].strip(), recruiter[2].strip(), 'recsub@opallios.com'])
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            setattr(mail, 'cc_email',
                    [request.user.email.strip(), BDM[2].strip(), recruiter_manager[2].strip(), 'recsub@opallios.com'])
        elif userGroup is None or userGroup == '':
            setattr(mail, 'cc_email', [])

        sendSubmissionMail(request, mail)
