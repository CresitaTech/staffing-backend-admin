import json
from django.contrib import messages
import urllib.request
import ssl
from django.core.mail import  EmailMessage
import requests
from django.db import connection
from interviews.models import Mails
from django.template.loader import render_to_string
from candidates.models import Candidates
from users.models import User
from users.serializers import UserSerializer
from staffingapp.settings import GLOBAL_ROLE

def sendRTRMail(request,obj):
    messages.add_message(request, messages.INFO, 'RTR Email Successfully Sent')
    print(obj)
    recipient_list = [obj.email]
    email = EmailMessage(subject=obj.subject, body=obj.message, from_email=obj.from_email, to=recipient_list)
    email.content_subtype = 'html'
    email.cc = [obj.cc_email]
    email.attach_file('.'+str(obj.jd))
    email.send()
    return messages

def sendSubmissionMail(request,obj):
    messages.add_message(request, messages.INFO, 'Submission Email Successfully Sent')
    print(obj)
    recipient_list = [obj.email]
    email = EmailMessage(subject=obj.subject, body=obj.message, from_email=obj.from_email, to=recipient_list)
    email.content_subtype = 'html'
    email.cc = obj.cc_email
    email.send()
    return messages

def sendMail(request, obj):

    messages.add_message(request, messages.INFO, 'Email Successfully Sent')
    #print(json.dumps(obj))
    print(obj.email)
    recipient_list = [obj.email]
    email = EmailMessage(subject=obj.subject, body=obj.message, from_email=obj.from_email, to=recipient_list)
    if obj.resume != None and obj.resume != '':
        email.attach_file('.' + str(obj.resume))
    email.content_subtype = 'html'
    email.cc = [obj.cc_email]
    res = email.send()
    #print(res)
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

    conn = requests.post('https://server.opallius.com/phpword/samples/rtr_doc.php?rtr_id='+str(id), json=None, headers=None, verify=False)
    #print(conn.content.decode("utf-8"))
    print(conn.status_code)
    if conn.status_code == 200:
        ssl._create_default_https_context = ssl._create_unverified_context
        with urllib.request.urlopen('https://server.opallius.com/phpword/samples/results/rtr_doc.docx') as url:
            s = url.read()
            #print(s)
        return s
        
def sendCandidateBDMMail(request, obj):
    print(obj)
    recipient_list = [obj.email]
    email = EmailMessage(subject=obj.subject, body=obj.message, from_email=obj.from_email,
                         to=recipient_list)
    email.content_subtype = 'html'
    if obj.resume != None and str(obj.resume) != '':
        email.attach_file('media/'+str(obj.resume))
    email.cc = obj.cc_email
    email.send()
    return messages
    
def sendBDMMail(request, id ,stage):

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
    
    candidate_id = str(id).replace('UUID', ''). \
        replace('(\'', '').replace('\')', '').replace('-', '')
    cursor = connection.cursor()
    cursor.execute(
        "SELECT resume , job_description_id ,first_name,last_name,primary_phone_number,primary_email,min_salary,min_rate,max_rate,"
        "current_location,visa,open_for_relocation,total_experience,qualification,total_experience_in_usa,any_offer_in_hand,created_by_id ,max_salary from osms_candidates WHERE id =%s",
        [candidate_id])
    candidate = cursor.fetchone()

    cursor.execute("SELECT job_title , created_by_id ,location,job_id  FROM osms_job_description WHERE id=%s", [candidate[1]])
    jd = cursor.fetchone()
    cursor.execute("SELECT first_name , last_name , email FROM users_user WHERE id=%s",
                   [jd[1]])
    BDM = cursor.fetchone()
    
    cursor.execute("SELECT first_name , last_name , email , created_by_id FROM users_user WHERE id=%s",
                   [candidate[16]])
    recruiter = cursor.fetchone()
    
    cursor.execute("SELECT first_name , last_name , email , created_by_id FROM users_user WHERE id=%s",
                   [recruiter[3]])
    recruiter_manager = cursor.fetchone()

    context_email1 = {'BDM_name': BDM[0],
                      'sender_name': request.user.first_name + ' ' + request.user.last_name,
                      'job_title': jd[0],
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
                                        "stage": stage ,
                                        "open_for_relocation": candidate[11],
                                        "total_experience": candidate[12],
                                        "qualification": candidate[13],
                                        "total_experience_in_usa": candidate[14],
                                        "any_offer_in_hand": candidate[15],
                                        "job_id": jd[3],
                                        "updated_by": request.user.first_name + ' ' + request.user.last_name
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
        setattr(mail, 'cc_email', [request.user.email.strip() , recruiter_manager[2].strip() ,recruiter[2].strip(),'recsub@opallios.com'])
    elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
        setattr(mail, 'cc_email', [recruiter_manager[2].strip() ,recruiter[2].strip() ,'recsub@opallios.com'])
    elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
        setattr(mail, 'cc_email', [request.user.email.strip() ,recruiter[2].strip(),'recsub@opallios.com'])
    elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
        setattr(mail, 'cc_email', [request.user.email.strip() ,recruiter_manager[2].strip() ,'recsub@opallios.com'])
    elif userGroup is None or userGroup == '':
        setattr(mail, 'cc_email', [])
        
    print("+++++++++++++++++++++++++++++")
    sendCandidateBDMMail(request, mail)
    print("+++++++++++++++++++++++++++++")
    
def sendClientMail(request, activity_status_id , candidate_name_id):
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

    candidate_id = str(candidate_name_id).replace('UUID', ''). \
        replace('(\'', '').replace('\')', '').replace('-', '')
    Candidates.objects.filter(id=candidate_id).update(stage_id=activity_status_id)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT resume , job_description_id ,first_name,last_name,primary_phone_number,primary_email,min_salary,min_rate,"
        "current_location,visa,open_for_relocation,total_experience,qualification,total_experience_in_usa,any_offer_in_hand,created_by_id,max_salary from osms_candidates WHERE id =%s",
        [candidate_id])
    candidate = cursor.fetchone()
    
    cursor.execute("SELECT client_name_id , job_title , location ,min_rate , max_rate,created_by_id , min_salary , max_salary from osms_job_description WHERE id=%s",
                   [candidate[1]])
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
    #mail.email = 'pandeym@cresitatech.com'
    mail.resume = None
    mail.jd = candidate[0]
    mail.message = render_to_string('candidates_submission.html', context_email)
    mail.condidate_email = None
    
    if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
        setattr(mail, 'cc_email', [request.user.email.strip()])
    elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
        setattr(mail, 'cc_email', [request.user.email.strip() ,recruiter_manager[2].strip() ,recruiter[2].strip()])
    elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
        setattr(mail, 'cc_email', [request.user.email.strip() ,BDM[2].strip() ,recruiter[2].strip()])
    elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
        setattr(mail, 'cc_email', [request.user.email.strip() , BDM[2].strip() ,recruiter_manager[2].strip()])
    elif userGroup is None or userGroup == '':
        setattr(mail, 'cc_email', [])
        
    print("+++++++++++++++++++++++++++++")
    sendSubmissionMail(request, mail)
    print("========================")