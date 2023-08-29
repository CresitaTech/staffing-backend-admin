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
    
def sendBDMMail(request, id):

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

    if id is not None:

        candidate_id = str(id).replace('UUID', ''). \
            replace('(\'', '').replace('\')', '').replace('-', '')

        cursor = connection.cursor()
        cursor.execute(
            "SELECT resume , remarks,first_name,last_name,primary_phone_number,primary_email , created_by_id from osms_candidates WHERE id =%s",
            [candidate_id])
        candidate = cursor.fetchone()

        cursor.execute("SELECT first_name , last_name , email , created_by_id FROM users_user WHERE id=%s",
                       [candidate[6]])
        recruiter = cursor.fetchone()

        cursor.execute("SELECT first_name , last_name , email , created_by_id FROM users_user WHERE id=%s",
                       [recruiter[3]])
        recruiter_manager = cursor.fetchone()
        
        cursor.execute("SELECT resume , driving_license , offer_letter , passport , rtr , salary_slip , i94_document"
        ", visa_copy , educational_document FROM osms_candidates_repositery WHERE candidate_name_id = %s",
                       [candidate_id])
        repo = cursor.fetchone()
        

        context_email1 = {'sender_name': request.user.first_name + ' ' + request.user.last_name,
                          'candidate_info': {"first_name": candidate[2],
                                            "last_name": candidate[3],
                                            "primary_phone_number": candidate[4],
                                            "primary_email": candidate[5],
                                            "updated_by": request.user.first_name + ' ' + request.user.last_name,
                                             },
                             'repo_details': { "resume" : repo[0],
                                        "driving_license" : repo[1],
                                        "offer_letter" : repo[2],
                                        "passport" : repo[3],
                                        "rtr" : repo[4],
                                        "salary_slip" : repo[5],
                                        "i94_document": repo[6],
                                        "visa_copy" : repo[7],
                                        "educational_document" : repo[8]
                            }
                    }

        mail = Mails()
        mail.subject = "New Document Updated On Repo"
        mail.from_email = request.user.email.strip()
        mail.email = BDM[2].strip()
        mail.jd = None
        mail.message = render_to_string('candidate_documentary_to_BDM.html', context_email1)
        mail.condidate_email = None

        if userGroup is not None and userGroup == GLOBAL_ROLE.get('ADMIN'):
            setattr(mail, 'cc_email', [request.user.email.strip() , recruiter_manager[2].strip() ,recruiter[2].strip() , 'recsub@opallios.com'])
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('BDMMANAGER'):
            setattr(mail, 'cc_email', [recruiter_manager[2].strip() ,recruiter[2].strip() , 'recsub@opallios.com'])
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITERMANAGER'):
            setattr(mail, 'cc_email', [request.user.email.strip() ,recruiter[2].strip() , 'recsub@opallios.com'])
        elif userGroup is not None and userGroup == GLOBAL_ROLE.get('RECRUITER'):
            setattr(mail, 'cc_email', [request.user.email.strip() ,recruiter_manager[2].strip() , 'recsub@opallios.com'])
        elif userGroup is None or userGroup == '':
            setattr(mail, 'cc_email', [])

        print("+++++++++++++++++++++++++++++")
        sendCandidateBDMMail(request, mail)
        print("+++++++++++++++++++++++++++++")