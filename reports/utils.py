import csv
import logging
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.contrib import messages
from rest_framework.exceptions import PermissionDenied

from staffingapp.settings import EMAIL_FROM_USER

logger = logging.getLogger(__name__)

"""
Method for sending jd mail on submission
"""


def sendJDMail(request, obj):
    messages.add_message(request, messages.INFO, 'JD Email Successfully Sent')
    print(obj)
    recipient_list = [obj.email]
    email = EmailMessage(subject=obj.subject, body=obj.message, from_email=obj.from_email,
                         to=recipient_list)
    email.content_subtype = 'html'
    if str(obj.resume) != None and str(obj.resume) != '':
        email.attach_file('.' + str(obj.resume))
    email.cc = [obj.cc_email.strip()]
    email.send()
    return messages


def sortDic(data):
    sorteddic = sorted(data, key=lambda x: x['rank'], reverse=True)
    return sorteddic


def calculateSubmission():
    totalSubmissionSql = "(" \
                         "s.stage_name = 'Submission' OR " \
                         "s.stage_name = 'Submission Reject' OR " \
                         "s.stage_name = 'Internal Interview' OR " \
                         "s.stage_name = 'Internal Interview Reject' OR " \
                         "s.stage_name = 'Candidate Review' OR " \
                         "s.stage_name = 'SendOut' OR " \
                         "s.stage_name = 'SendOut Reject' OR " \
                         "s.stage_name = 'Client Interview - First' OR " \
                         "s.stage_name = 'Interview Backout' OR " \
                         "s.stage_name = 'Interview Reject' OR " \
                         "s.stage_name = 'Interview Select' OR " \
                         "s.stage_name = 'Interview Reject' OR " \
                         "s.stage_name = 'Client Interview - Second' OR " \
                         "s.stage_name = 'Second Interview Reject' OR " \
                         "s.stage_name = 'Offerred' OR " \
                         "s.stage_name = 'Offer Reject' OR " \
                         "s.stage_name = 'Offer Backout' OR " \
                         "s.stage_name = 'Feedback Awaited' OR " \
                         "s.stage_name = 'Hold by BDM' OR " \
                         "s.stage_name = 'Hold by Client' OR " \
                         "s.stage_name = 'Placed' " \
                         ")"
    # Submission = sum(Submission, Submission Reject, Internal Interview, Internal Interview Reject, Candidate
    # Review, Sendout, SendOut Reject, Client Interview - First, Interview Backout Interview Reject,
    # Interview Select, Client Interview - Second, Second Interview Reject, Offerred, Offer Reject, Offer Backout,
    # Feedback Awaited, Hold by BDM, Hold by Client, Placed)
    return totalSubmissionSql


def calculateSendOut():
    totalSendOutSQL = "(" \
                      "s.stage_name = 'SendOut' OR " \
                      "s.stage_name = 'SendOut Reject' OR " \
                      "s.stage_name = 'Client Interview - First' OR " \
                      "s.stage_name = 'Interview Backout' OR " \
                      "s.stage_name = 'Interview Reject' OR " \
                      "s.stage_name = 'Interview Select' OR " \
                      "s.stage_name = 'Client Interview - Second' OR " \
                      "s.stage_name = 'Second Interview Reject' OR " \
                      "s.stage_name = 'Offerred' OR " \
                      "s.stage_name = 'Offer Reject' OR " \
                      "s.stage_name = 'Offer Backout' OR " \
                      "s.stage_name = 'Feedback Awaited' OR " \
                      "s.stage_name = 'Hold by Client' OR " \
                      "s.stage_name = 'Placed' " \
                      ")"
    # SendOut = Sum (Sendout, SendOut Reject, Client Interview - First, Interview Backout Interview Reject,
    # Interview Select, Client Interview - Second, Second Interview Reject, Offerred, Offer Reject, Offer Backout,
    # Feedback Awaited, Hold by Client, Placed)
    return totalSendOutSQL


def calculateInterview():
    totalInterviewSql = "(" \
                        "s.stage_name = 'Client Interview - First' OR " \
                        "s.stage_name = 'Interview Backout' OR " \
                        "s.stage_name = 'Interview Reject' OR " \
                        "s.stage_name = 'Interview Select' OR " \
                        "s.stage_name = 'Client Interview - Second' OR " \
                        "s.stage_name = 'Second Interview Reject' OR " \
                        "s.stage_name = 'Offerred' OR " \
                        "s.stage_name = 'Offer Reject' OR " \
                        "s.stage_name = 'Offer Backout' OR " \
                        "s.stage_name = 'Feedback Awaited' OR " \
                        "s.stage_name = 'Hold by Client' OR " \
                        "s.stage_name = 'Placed' " \
                        ")"

    # Interview = sum (Client Interview - First, Interview Backout Interview Reject, Interview Select,
    # Client Interview - Second, Second Interview Reject, Offerred, Offer Reject, Offer Backout, Feedback Awaited,
    # Hold by Client, Placed)
    return totalInterviewSql


def calculateShortlisted():
    totalShortlistedSql = "(" \
                          "s.stage_name = 'Interview Select' " \
                          ")"
    # Shortlisted = Sum (Interview Select)
    return totalShortlistedSql


def calculateOffered():
    totalOfferedSql = "(" \
                      "s.stage_name = 'Offerred' OR " \
                      "s.stage_name = 'Offer Reject' OR " \
                      "s.stage_name = 'Offer Backout' " \
                      ")"
    # Offered = Sum (Offerred, Offer Reject, Offer Backout)
    return totalOfferedSql


def download_csv(request, queryset, filename, field_names):
    if not request.user.is_staff:
        raise PermissionDenied
    opts = queryset.model._meta
    logger.info(opts)
    # model = queryset.model
    response = HttpResponse(content_type='text/csv')
    # force download.
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    # the csv writer
    writer = csv.writer(response)
    # field_names = [field.name for field in opts.fields]
    logger.info(str(field_names))
    # Write a first row with header information
    writer.writerow(field_names)
    # Write data rows
    for obj in queryset:
        logger.info(obj)
        writer.writerow([getattr(obj, field) for field in field_names])

    return response


# download_csv.short_description = "Download selected as csv"

def formulaFields():
    aggregateData = "sum(case when s.stage_name = 'Candidate Added' then 1 else 0 end) as CandidateAdded, " \
                    "sum(case when s.stage_name = 'Candidate Review' then 1 else 0 end) as CandidateReview, " \
                    "sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as RejectedByTeam, " \
                    "sum(case when (s.stage_name = 'Submission' OR s.stage_name = 'Submission Reject' OR s.stage_name = 'Internal Interview' OR s.stage_name = 'Internal Interview Reject' OR s.stage_name = 'Candidate Review' OR s.stage_name = 'SendOut' OR s.stage_name = 'SendOut Reject' OR s.stage_name = 'Client Interview - First' OR s.stage_name = 'Interview Backout Interview Reject' OR s.stage_name = 'Interview Select' OR s.stage_name = 'Client Interview - Second' OR s.stage_name = 'Second Interview Reject' OR s.stage_name = 'Offerred' OR s.stage_name = 'Offer Reject' OR s.stage_name = 'Offer Backout' OR s.stage_name = 'Feedback Awaited' OR s.stage_name = 'Hold by BDM' OR s.stage_name = 'Hold by Client' OR s.stage_name = 'Placed' OR s.stage_name = 'Interview Reject') then 1 else 0 end) as Submission, " \
                    "sum(case when s.stage_name = 'Submission' then 1 else 0 end) as StillSubmission," \
                    "sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as SubmissionReject," \
                    "sum(case when (s.stage_name = 'SendOut' OR s.stage_name = 'SendOut Reject' OR s.stage_name = 'Client Interview - First' OR s.stage_name = 'Interview Backout' OR s.stage_name = 'Interview Reject' OR s.stage_name = 'Interview Select' OR s.stage_name = 'Client Interview - Second' OR s.stage_name = 'Second Interview Reject' OR s.stage_name = 'Offerred' OR s.stage_name = 'Offer Reject' OR s.stage_name = 'Offer Backout' OR s.stage_name = 'Feedback Awaited' OR s.stage_name = 'Hold by Client' OR s.stage_name = 'Placed' ) then 1 else 0 end) as 'SendOut'," \
                    "sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as SendoutReject ," \
                    "sum(case when (s.stage_name = 'Client Interview - First' OR s.stage_name = 'Interview Backout' OR s.stage_name = 'Interview Reject' OR s.stage_name = 'Interview Select' OR s.stage_name = 'Client Interview - Second' OR s.stage_name = 'Second Interview Reject' OR s.stage_name = 'Offerred' OR s.stage_name = 'Offer Reject' OR s.stage_name = 'Offer Backout' OR s.stage_name = 'Feedback Awaited' OR s.stage_name = 'Hold by Client' OR s.stage_name = 'Placed' ) then 1 else 0 end) as ClientInterview ," \
                    "sum(case when s.stage_name = 'Interview Reject' then 1 else 0 end) as 'RejectedByClient'," \
                    "sum(case when (s.stage_name = 'Offerred' OR s.stage_name = 'Offer Rejected' OR s.stage_name = 'Offer Backout' OR s.stage_name = 'Placed') then 1 else 0 end) as Offered ," \
                    "sum(case when (s.stage_name = 'Shortlisted' OR s.stage_name = 'Offered' OR s.stage_name = 'Offer Rejected' OR s.stage_name = 'Offer Backout' OR s.stage_name = 'Placed') then 1 else 0 end) as Shortlisted," \
                    "sum(case when (s.stage_name = 'Client Interview - First' OR s.stage_name = 'Hold by Client' OR s.stage_name = 'Interview Backout' OR s.stage_name = 'Feedback Awaited' OR s.stage_name = 'Interview Reject' OR s.stage_name = 'Interview Select' OR s.stage_name = 'Client Interview - Second' OR s.stage_name = 'Second Interview Reject' OR s.stage_name = 'Shortlisted' OR s.stage_name = 'Offered' OR s.stage_name = 'Offer Rejected' OR s.stage_name = 'Offer Backout' OR s.stage_name = 'Placed' ) then 1 else 0 end) as ClientInterviewFirst," \
                    "sum(case when (s.stage_name = 'Client Interview - Second' OR s.stage_name = 'Second Interview Reject' OR s.stage_name = 'Shortlisted' OR s.stage_name = 'Offered' OR s.stage_name = 'Offer Rejected' OR s.stage_name = 'Offer Backout' OR s.stage_name = 'Placed' ) then 1 else 0 end) as ClientInterviewSecond," \
                    "sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as OfferRejected," \
                    "sum(case when s.stage_name = 'Second Interview Reject' then 1 else 0 end) as SecondInterviewReject ," \
                    "sum(case when s.stage_name = 'Hold by Client' then 1 else 0 end) as HoldbyClient," \
                    "sum(case when s.stage_name = 'Interview Select' then 1 else 0 end) as InterviewSelect ," \
                    "sum(case when s.stage_name = 'Offer Backout' then 1 else 0 end) as OfferBackout," \
                    "sum(case when s.stage_name = 'Hold by BDM' then 1 else 0 end) as HoldbyBDM," \
                    "sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as InternalInterview," \
                    "sum(case when s.stage_name = 'Interview Backout' then 1 else 0 end) as InterviewBackout," \
                    "sum(case when s.stage_name = 'Feedback Awaited' then 1 else 0 end) as FeedbackAwaited," \
                    "sum(case when s.stage_name = 'Internal Interview Reject' then 1 else 0 end) as InternalInterviewReject," \
                    "sum(case when s.stage_name = 'Placed' then 1 else 0 end) as Placed," \
                    "sum(case when s.stage_name = 'Interview Reject' then 1 else 0 end) as InterviewReject "

    return aggregateData


def internalFormulaFields():
    aggregateData = "sum(case when (s.stage_name = 'Internal Submission' or s.stage_name = 'Internal Submission Reject' or s.stage_name = 'Internal Interview' or s.stage_name = 'Internal Interview Reject' or s.stage_name = 'Internal Shortlisted' or s.stage_name = 'Internal Offered' or s.stage_name = 'Internal Offered Reject' or s.stage_name = 'Internal Placed' or s.stage_name = 'SendOut to Client') then 1 else 0 end) as InternalSubmission, " \
                    "sum(case when (s.stage_name = 'Internal Submission Reject') then 1 else 0 end) as InternalSubmissionReject, " \
                    "sum(case when (s.stage_name = 'Internal Interview' or s.stage_name = 'Internal Interview Reject' or s.stage_name = 'Internal Shortlisted' or s.stage_name = 'Internal Offered' or s.stage_name = 'Internal Offered Reject' or s.stage_name = 'Internal Placed' or s.stage_name = 'SendOut to Client') then 1 else 0 end) as InternalInterview1, " \
                    "sum(case when (s.stage_name = 'Internal Interview Reject') then 1 else 0 end) as InternalInterviewReject1, " \
                    "sum(case when (s.stage_name = 'Internal Shortlisted' or s.stage_name = 'Internal Offered' or s.stage_name = 'Internal Offered Reject' or s.stage_name = 'Internal Placed' or s.stage_name = 'SendOut to Client') then 1 else 0 end) as InternalShortlisted, " \
                    "sum(case when (s.stage_name = 'Internal Offered' or s.stage_name = 'Internal Offered Reject' or s.stage_name = 'Internal Placed' or s.stage_name = 'SendOut to Client') then 1 else 0 end) as InternalOffered, " \
                    "sum(case when (s.stage_name = 'Internal Offered Reject') then 1 else 0 end) as InternalOfferedReject, " \
                    "sum(case when (s.stage_name = 'Internal Placed') then 1 else 0 end) as InternalPlaced, " \
                    "sum(case when (s.stage_name = 'SendOut to Client') then 1 else 0 end) as SendOuttoClient "
    return aggregateData


def generateJobSummaryTableByDatewiseBreakdownCsvQuery(start_date, end_date, job_id):
    selectStmt = "select j.id,  u.id as rid,  j.job_title, CONCAT(u.first_name, ' ' , u.last_name) as recruiter_name, j.job_posted_date, "
    where = "from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs, users_user as u " \
            "WHERE  cjs.submission_date >= '" + start_date + "' AND cjs.submission_date <= '" + end_date + "' AND s.stage_name != 'Candidate Added'  AND cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id AND ca.created_by_id = u.id AND j.id = '" + str(
        job_id) + "' GROUP BY  cjs.created_by_id "

    query = selectStmt + str(formulaFields()) + where
    return query


def recruiterCallStatsQuery(start_date, end_date):
    selectStmt = "select COUNT(*) FROM recruiter_daily_calls as r WHERE (r.call_to_number = u.external_user OR " \
                 "r.caller_id_number = u.external_user) AND (r.created_at >= '" + str(start_date) + "' AND " \
                                                                                                    "r.created_at <= " \
                                                                                                    "'" + str(
        end_date) + "') "

    query = selectStmt
    return query


def generateRecruiterCallsSummaryTableByDatewiseAndIdCsvQuery(start_date, end_date, recruiter_id, country, data_type):
    selectStmt = ""
    where = ""
    start_date = str(start_date) + " 00:00:00"
    end_date = str(end_date) + " 23:59:59"
    filterQuery = ""
    callQuery = recruiterCallStatsQuery(start_date, end_date)

    if recruiter_id is not None and (country is not None and country != 'none' and country != 'ALL'):
        recruiter_id = str(recruiter_id).replace("-", "")
        filterQuery = "AND (jda.primary_recruiter_name_id = '" + recruiter_id + "' OR jda.secondary_recruiter_name_id = '" + recruiter_id + "')  AND j.country = '" + country + "' "
    elif recruiter_id is not None:
        recruiter_id = str(recruiter_id).replace("-", "")
        filterQuery = "AND (jda.primary_recruiter_name_id = '" + recruiter_id + "' OR jda.secondary_recruiter_name_id = '" + recruiter_id + "') "
    elif country is not None and country != 'none' and country != 'ALL':
        filterQuery = "AND j.country = '" + country + "' "

    selectStmt = "SELECT * FROM (SELECT u.id, COUNT(DISTINCT(jda.job_id_id)) as job_title, CONCAT(u.first_name, ' ' , u.last_name) as " \
                 "recruiter_name, ("+callQuery+") as attempted_calls, j.country FROM job_description_assingment as jda LEFT JOIN `osms_job_description` as j ON jda.job_id_id = j.id " \
                    "LEFT JOIN `users_user` as u on (u.id = jda.primary_recruiter_name_id or u.id = jda.secondary_recruiter_name_id) WHERE (jda.created_at >= '" + str(
        start_date) + "' AND jda.created_at <= '" + str(
        end_date) + "')  " + filterQuery + " GROUP BY u.id ) AS A LEFT JOIN (select u.id as rid, "

    where1 = "from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s , " \
             "`candidates_jobs_stages` as cjs, users_user as u WHERE cjs.submission_date >= '" + str(
        start_date) + "' AND " \
                      "cjs.submission_date <= '" + str(
        end_date) + "' AND cjs.stage_id = s.id AND s.stage_name != 'Candidate Added' AND cjs.job_description_id = j.id AND " \
                    "cjs.candidate_name_id = ca.id AND cjs.created_by_id = u.id GROUP BY u.id ) AS B ON A.id = B.rid "

    where2 = "LEFT JOIN (select u.id as rrid, " + str(
        internalFormulaFields()) + " from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s , " \
                                   "`internal_candidates_jobs_stages` as cjs, users_user as u WHERE cjs.submission_date >= '" + str(
        start_date) + "' AND " \
                      "cjs.submission_date <= '" + str(
        end_date) + "' AND cjs.stage_id = s.id AND s.stage_name != 'Candidate Added' AND cjs.job_description_id = j.id AND " \
                    "cjs.candidate_name_id = ca.id AND cjs.created_by_id = u.id GROUP BY u.id ) AS C ON A.id = C.rrid;"

    query = selectStmt + str(formulaFields()) + where1 + where2
    return query

    """start_date = str(start_date) + " 00:00:00"
    end_date = str(end_date) + " 23:59:59"

    if recruiter_id is not None:
        recruiter_id = str(recruiter_id).replace("-", "")
        selectStmt = "SELECT * FROM (SELECT u.id, CONCAT(u.first_name, ' ' , u.last_name) as " \
                     "recruiter_name, (select SUM(r.attempted_calls) FROM recruiter_calls as r WHERE r.recruiter_name " \
                     "= u.external_user AND r.created_at >= '"+str(start_date)+"' AND r.created_at <= '"+str(
            end_date)+"' GROUP BY r.recruiter_name) as attempted_calls, rc.connected_calls, rc.missed_calls, " \
                        "j.country FROM `osms_job_description` as j LEFT JOIN candidates_jobs_stages as cjs ON j.id = " \
                     "cjs.job_description_id LEFT JOIN `users_user` as u on u.id = cjs.created_by_id LEFT JOIN " \
                     "recruiter_calls as rc ON u.external_user = rc.recruiter_name WHERE j.status = 'Active' AND " \
                     "u.is_active = '1' AND u.role IN ('3', '2', '9') AND cjs.created_by_id = '" + str(recruiter_id) +"' GROUP BY u.id ORDER BY `rc`.`attempted_calls` ASC ) " \
                     "AS A LEFT JOIN (select u.id as rid, COUNT(*) as job_title, "
        where = "from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s , " \
                "`candidates_jobs_stages` as cjs, users_user as u WHERE cjs.submission_date >= '"+str(start_date)+"' AND " \
                "cjs.submission_date <= '"+str(end_date)+"' AND cjs.stage_id = s.id AND cjs.job_description_id = j.id AND " \
                "cjs.candidate_name_id = ca.id AND cjs.created_by_id = u.id GROUP BY u.id ) AS B ON A.id = B.rid; "

    else:
        selectStmt = "SELECT * FROM (SELECT u.id, CONCAT(u.first_name, ' ' , u.last_name) as " \
                     "recruiter_name, (select SUM(r.attempted_calls) FROM recruiter_calls as r WHERE r.recruiter_name " \
                     "= u.external_user AND r.created_at >= '"+str(start_date)+"' AND r.created_at <= '"+str(end_date) + "' GROUP BY r.recruiter_name) as attempted_calls, rc.connected_calls, rc.missed_calls, j.country FROM " \
                     "`osms_job_description` as j LEFT JOIN candidates_jobs_stages as cjs ON j.id = " \
                     "cjs.job_description_id LEFT JOIN `users_user` as u on u.id = cjs.created_by_id LEFT JOIN " \
                     "recruiter_calls as rc ON u.external_user = rc.recruiter_name WHERE j.status = 'Active' AND " \
                     "u.is_active = '1' AND u.role IN ('3', '2', '9') GROUP BY u.id ORDER BY `rc`.`attempted_calls` ASC ) " \
                                                                                                                "AS A LEFT JOIN (select u.id as rid, COUNT(*) as job_title, "
        where = "from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s , " \
                "`candidates_jobs_stages` as cjs, users_user as u WHERE cjs.submission_date >= '"+str(start_date)+"' AND " \
                "cjs.submission_date <= '"+str(end_date)+"' AND cjs.stage_id = s.id AND cjs.job_description_id = j.id AND " \
                "cjs.candidate_name_id = ca.id AND cjs.created_by_id = u.id GROUP BY u.id ) AS B ON A.id = B.rid; "
    query = selectStmt + str(formulaFields()) + where
    return query"""


def generateRecruiterCallsPerformanceSummaryTableByDatewiseAndIdCsvQuery(start_date, end_date, recruiter_id, country,
                                                                         data_type):
    selectStmt = ""
    where = ""
    start_date = str(start_date) + " 00:00:00"
    end_date = str(end_date) + " 23:59:59"
    filterQuery = ""

    if recruiter_id is not None:
        recruiter_id = str(recruiter_id).replace("-", "")
        filterQuery = " AND cjs.created_by_id = '" + str(recruiter_id) + "' "

    selectStmt = "SELECT * FROM (SELECT j.id, j.job_title, CONCAT(u.first_name, ' ' , u.last_name) as " \
                 "recruiter_name, rc.attempted_calls, rc.connected_calls, rc.missed_calls, j.country, " \
                 "j.min_salary, j.max_salary, j.max_rate, j.min_rate, j.notice_period, j.mode_of_interview, " \
                 "j.number_of_opening, j.mode_of_work, j.projected_revenue, j.job_posted_date, j.created_at, " \
                 "j.updated_at FROM `osms_job_description` as j LEFT JOIN candidates_jobs_stages as cjs ON j.id = " \
                 "cjs.job_description_id LEFT JOIN `users_user` as u on u.id = cjs.created_by_id LEFT JOIN " \
                 "recruiter_calls as rc ON u.external_user = rc.recruiter_name WHERE j.status = 'Active' AND " \
                 "u.is_active = '1' AND u.role IN ('3', '2', '9') " + filterQuery + " GROUP BY j.id ORDER BY `rc`.`attempted_calls` ASC ) AS A "

    where1 = "LEFT JOIN (select j.id as job_id, " + str(
        formulaFields()) + " from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s , " \
                           "`candidates_jobs_stages` as cjs, users_user as u WHERE cjs.submission_date >= '" + str(
        start_date) + "' AND " \
                      "cjs.submission_date <= '" + str(
        end_date) + "' AND cjs.stage_id = s.id AND cjs.job_description_id = j.id AND " \
                    "cjs.candidate_name_id = ca.id AND cjs.created_by_id = u.id GROUP BY j.id ) AS B ON A.id = B.job_id; "

    where2 = "LEFT JOIN (select j.id as jobid, " + str(
        internalFormulaFields()) + " from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s , " \
                                   "`candidates_jobs_stages` as cjs, users_user as u WHERE cjs.submission_date >= '" + str(
        start_date) + "' AND " \
                      "cjs.submission_date <= '" + str(
        end_date) + "' AND cjs.stage_id = s.id AND cjs.job_description_id = j.id AND " \
                    "cjs.candidate_name_id = ca.id AND cjs.created_by_id = u.id GROUP BY j.id ) AS C ON A.id = C.jobid; "

    query = selectStmt + where1 + where2
    return query
