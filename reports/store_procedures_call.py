from candidates.models import Candidates
import logging

from reports.utils import generateJobSummaryTableByDatewiseBreakdownCsvQuery, formulaFields, \
    generateRecruiterCallsSummaryTableByDatewiseAndIdCsvQuery, \
    generateRecruiterCallsPerformanceSummaryTableByDatewiseAndIdCsvQuery, internalFormulaFields

# Get an instance of a logger
logger = logging.getLogger(__name__)


def get_candidate_queryset(start_date, end_date):
    queryset = Candidates.objects.raw("CALL get_jobs_summary_by_date_range(%s, %s)",
                                      [start_date, end_date])
    logger.info(queryset.query)
    return queryset


def get_recruiter_calls_performance_table(start_date, end_date, recruiter_id, country, data_type):
    # queryset = Candidates.objects.raw("CALL get_recruiter_calls_performance_table(%s, %s)",
    #                                  [start_date, end_date])
    # logger.info(queryset.query)
    query = generateRecruiterCallsSummaryTableByDatewiseAndIdCsvQuery(start_date, end_date, recruiter_id, country, data_type)
    queryset = Candidates.objects.raw(query)
    logger.info(queryset.query)
    return queryset


def get_recruiter_calls_performance_table_alldata_csv(start_date, end_date, recruiter_id, country, data_type):
    query = generateRecruiterCallsPerformanceSummaryTableByDatewiseAndIdCsvQuery(start_date, end_date, recruiter_id, country, data_type)
    queryset = Candidates.objects.raw(query)
    logger.info(queryset.query)
    return queryset


def get_recruiter_calls_performance_table_alldata(start_date, end_date):
    queryset = Candidates.objects.raw("CALL get_recruiter_calls_performance_table_alldata(%s, %s)",
                                      [start_date, end_date])
    logger.info(queryset.query)
    return queryset


def get_recruiter_calls_performance_table_alldata_by_job_id(start_date, end_date, job_id, recruiter_id, country):
    filterQuery = ""
    logger.info("Country: " + str(country))
    logger.info("recruiter_id: " + str(recruiter_id))
    logger.info("start_date: " + str(start_date))
    logger.info("end_date: " + str(end_date))
    start_date = str(start_date) + " 00:00:00"
    end_date = str(end_date) + " 23:59:59"

    if recruiter_id is not None and (country is not None and country != 'none' and country != 'ALL'):
        recruiter_id = str(recruiter_id).replace("-", "")
        filterQuery = "cjs.submitted_by_id = '" + recruiter_id + "' AND ca.country = '" + country + "' AND"
    elif recruiter_id is not None:
        recruiter_id = str(recruiter_id).replace("-", "")
        filterQuery = "cjs.submitted_by_id = '" + recruiter_id + "' AND"
    elif country is not None and country != 'none' and country != 'ALL':
        filterQuery = "ca.country = '" + country + "' AND"

    query = "SELECT ca.id, j.job_title, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, " \
            "CONCAT(u.first_name, ' ' , u.last_name) as recruiter_name, ca.min_salary, ca.max_salary, cs.stage_name " \
            "as current_status, cjs.submission_date as submitted_on, cjs.updated_at as last_updated_on, " \
            "ca.total_experience as total_exp, cjs.notes as remarks, ca.country, (case when jda.primary_recruiter_name_id = u.id then 'Primary' else 'Secondary' end) as assignment_type FROM `candidates_jobs_stages` as cjs " \
            "LEFT JOIN osms_job_description as j ON j.id = cjs.job_description_id LEFT JOIN " \
            "job_description_assingment as jda ON j.id = jda.job_id_id LEFT JOIN osms_candidates as ca ON " \
            "cjs.`candidate_name_id` = ca.id LEFT JOIN candidates_stages as cs ON cs.id = cjs.stage_id LEFT JOIN " \
            "users_user as u ON cjs.submitted_by_id = u.id WHERE cs.stage_name != 'Candidate Added' AND " \
            " "+filterQuery+" (cjs.submission_date >= '"+str(start_date)+"' " \
            " AND cjs.submission_date <= '"+str(end_date)+"') group by cjs.id "

    queryset = Candidates.objects.raw(query)
    logger.info(queryset.query)

    return queryset


def get_job_submission_by_client(start_date, end_date, client_id, country, bdm_id):
    filterQuery = ""
    logger.info("Country: " + str(country))
    logger.info("client_id: " + str(client_id))
    logger.info("start_date: " + str(start_date))
    logger.info("end_date: " + str(end_date))
    start_date = str(start_date) + " 00:00:00"
    end_date = str(end_date) + " 23:59:59"

    if client_id is not None and (country is not None and country != 'none' and country != 'ALL'):
        filterQuery = "cl.id = '" + client_id + "' AND cl.country = '" + country + "' AND"
    elif client_id is not None:
        client_id = str(client_id).replace("-", "")
        filterQuery = "cl.id = '" + client_id + "' AND"
    elif country is not None and country != 'none' and country != 'ALL':
        filterQuery = "cl.country = '" + country + "' AND"
    if bdm_id is not None:
        bdm_id = str(bdm_id).replace("-", "")
        filterQuery = filterQuery + " u.id = '" + bdm_id + "' AND"

    statementA = "SELECT * FROM (SELECT cl.id, COUNT(j.client_name_id) as total_jobs, " \
                 "cl.company_name AS client_name, " \
                 "CONCAT(u.first_name,' ',u.last_name) as bdm_name, " \
                 "cl.country FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN " \
                 "`osms_clients` as cl on j.client_name_id = cl.id WHERE " + filterQuery + " j.created_at >= '"+str(start_date)+"' AND " \
                 "j.created_at <= '"+str(end_date)+"' GROUP BY cl.id) AS A LEFT JOIN "

    statementB = "(select cl.id as cl_id , " + formulaFields() + " from `osms_job_description` as j , `osms_candidates` as ca , " \
                 "`candidates_stages` as s , `candidates_jobs_stages` as cjs, osms_clients as cl WHERE cjs.submission_date >= '"+str(start_date)+"' AND " \
                 "cjs.submission_date <= '"+str(end_date)+"' AND cjs.stage_id = s.id AND j.client_name_id = cl.id AND " \
                 "cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY cl.id ) AS B ON A.id = " \
                 "B.cl_id "

    query = statementA + statementB

    queryset = Candidates.objects.raw(query)
    logger.info(queryset.query)

    return queryset


def get_jobs_summary_by_job_title_alldata(start_date, end_date, job_id):
    queryset = Candidates.objects.raw("CALL get_jobs_summary_by_job_title_alldata(%s, %s, %s)",
                                      [start_date, end_date, job_id])
    logger.info(queryset.query)

    """logger.info("start_date: " + str(start_date))
    logger.info("end_date: " + str(end_date))
    start_date = str(start_date) + " 00:00:00"
    end_date = str(end_date) + " 23:59:59"
    filterQuery = ""

    if job_id is not None:
        job_id = str(job_id).replace("-", "")
        filterQuery = "AND j.id = '" + job_id + "' "

    selectStmtA = "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, u.id as bdm_id, j.job_title as job_title, " \
                  "cl.company_name AS client_name,j.employment_type, j.min_salary ,j.max_salary ,j.min_rate ," \
                  "j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date, cl.country, j.number_of_opening " \
                  " FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN " \
                  "`osms_clients` as cl on j.client_name_id = cl.id WHERE j.status = 'Active' AND u.is_active = '1' " \
                  "AND u.role IN ('9', '2') " + filterQuery + " ORDER BY client_name, job_date ASC) AS A "

    selectStmtB = "LEFT JOIN (select j.id as job_id, " + formulaFields() + ", cjs.notes as remarks from `osms_job_description` as j , `osms_candidates` as ca , " \
                                                                           "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE cjs.submission_date >= '" + str(
        start_date) + "' " \
                      "AND cjs.submission_date <= '" + str(
        end_date) + "' AND cjs.stage_id = s.id AND cjs.job_description_id = j.id AND " \
                    "cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id "

    selectStmtC = "LEFT JOIN (select j.id as jobid, " + internalFormulaFields() + ", cjs.notes as remarks from `osms_job_description` as j , `osms_candidates` as ca , " \
                                                                                  "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE cjs.submission_date >= '" + str(
        start_date) + "' " \
                      "AND cjs.submission_date <= '" + str(
        end_date) + "' AND cjs.stage_id = s.id AND cjs.job_description_id = j.id AND " \
                    "cjs.candidate_name_id = ca.id GROUP BY j.id ) AS C ON A.id = C.jobid "

    query = selectStmtA + selectStmtB + selectStmtC
    queryset = Candidates.objects.raw(query)"""

    return queryset


def get_jobs_summary_by_datewise_breakdown(start_date, end_date, job_id):
    # queryset = Candidates.objects.raw("CALL get_jobs_summary_by_datewise_breakdown(%s, %s, %s)",
    #                                  [start_date, end_date, job_id])
    filterQuery = ""
    start_date = str(start_date) + " 00:00:00"
    end_date = str(end_date) + " 23:59:59"
    if job_id is not None:
        job_id = str(job_id).replace("-", "")
        filterQuery = "AND j.id = '" + job_id + "' "

    selectStmtA = "SELECT * FROM (select j.id, u.id as rid, j.job_title, CONCAT(u.first_name, ' ' , u.last_name) as recruiter_name, " \
          "j.job_posted_date as job_posted_date, " + formulaFields() + " from `osms_job_description` as j , `osms_candidates` as ca , " \
          "`candidates_stages` as s , `candidates_jobs_stages` as cjs, users_user as u WHERE cjs.submission_date >= " \
          " '" + str(start_date) + "' AND cjs.submission_date <= '" + str(end_date) + "' AND s.stage_name != 'Candidate Added'  AND cjs.stage_id = " \
          "s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id AND ca.created_by_id = u.id " \
          " " + filterQuery + " GROUP BY  cjs.created_by_id ) AS A "

    selectStmtC = "LEFT JOIN (select j.id as jobid, " + internalFormulaFields() + ", cjs.notes as remarks from `osms_job_description` as j , `osms_candidates` as ca , " \
                                                                                  "`candidates_stages` as s , `internal_candidates_jobs_stages` as cjs WHERE cjs.submission_date >= '" + str(
        start_date) + "' " \
                      "AND cjs.submission_date <= '" + str(
        end_date) + "' AND cjs.stage_id = s.id AND cjs.job_description_id = j.id AND " \
                    "cjs.candidate_name_id = ca.id GROUP BY j.id ) AS C ON A.id = C.jobid "

    query = selectStmtA + selectStmtC
    queryset = Candidates.objects.raw(query)
    logger.info(queryset.query)
    return queryset


def get_jobs_summary_by_datewise_breakdown_csv(start_date, end_date, job_id):
    query = generateJobSummaryTableByDatewiseBreakdownCsvQuery(start_date, end_date, job_id)
    queryset = Candidates.objects.raw(query)
    logger.info(queryset.query)
    return queryset


def get_candidate_details_by_job_id(start_date, end_date, job_id, rid):
    queryset = Candidates.objects.raw("CALL get_candidate_details_by_job_id(%s, %s, %s, %s)",
                                      [start_date, end_date, job_id, rid])
    logger.info(queryset.query)
    return queryset


def get_candidate_details_by_job_id_csv(start_date, end_date, job_id, rid):
    query = "SELECT ca.id, CONCAT(ca.first_name, ' ' , ca.last_name) as candidate_name, ca.primary_email, " \
            "ca.primary_phone_number, ca.company_name, ca.total_experience, ca.rank, ca.min_rate, ca.max_rate, " \
            "ca.min_salary, ca.max_salary, cl.company_name as client_name, ca.country as location, ca.visa, " \
            "ca.current_location as job_type, cs.stage_name as status, ca.country, cjs.submission_date, cjs.notes as remarks  FROM `candidates_jobs_stages` as " \
            "cjs, osms_candidates as ca, candidates_stages as cs, users_user as u, osms_job_description as j, osms_clients as cl  WHERE " \
            "cjs.`candidate_name_id` = ca.id AND ca.created_by_id = u.id AND cs.id = cjs.stage_id AND j.id = " \
            "cjs.job_description_id AND j.id = '" + job_id + "' AND cjs.created_by_id = '" + rid + "' AND cjs.submission_date >= '" + str(start_date) + "' AND cjs.submission_date <= '" + str(end_date) + "' AND cl.id = j.client_name_id order by ca.id ASC "
    queryset = Candidates.objects.raw(query)
    logger.info(queryset.query)
    return queryset


def get_jobs_summary_csv_by_date_range_and_id(start_date, end_date, bdm_id, country, status,employment_type):
    logger.info("bdm_id: " + str(bdm_id))
    logger.info("country: " + str(country))
    logger.info("start_date: " + str(start_date))
    logger.info("end_date: " + str(end_date))
    start_date = str(start_date) + " 00:00:00"
    end_date = str(end_date) + " 23:59:59"
    filterQuery = ""
    filterQuery1 = ""
    filterQuery2=""

    if bdm_id is not None and 'ALL' in bdm_id:
        bdm_id = 'ALL'
    if country is not None and 'ALL' in country:
        country = 'ALL'
    if status is not None and 'ALL' in status:
        status = 'ALL'

    
    if bdm_id is not None and (country is not None and country != 'none' and country != 'ALL'):
        bdm_id = str(bdm_id).replace("-", "")
        bdm_id_values = "','".join(bdm_id.strip("[]").replace("'", "").split(","))
        filterQuery = "AND j.created_by_id IN ('"+bdm_id_values+"') AND cl.country IN ('" + "','".join(country) + "') "
    elif bdm_id is not None:
        bdm_id = str(bdm_id).replace("-", "")
        bdm_id_values = "','".join(bdm_id.strip("[]").replace("'", "").split(","))
        filterQuery = "AND j.created_by_id IN ('"+bdm_id_values+"') "
    elif country is not None and country != 'none' and country != 'ALL':
        filterQuery = "AND cl.country IN ('" + "','".join(country) + "') "

    if status:
        filterQuery1 = "AND j.status IN ('" + "','".join(status) + "') "

    if employment_type:
        filterQuery2 = "AND j.employment_type IN ('" + "','".join(employment_type) + "') "
 

# Now you can use filterQuery2 in your SQL query or further processing


    filterQuery = filterQuery + filterQuery1 +filterQuery2

    # j.status = 'Active' AND j.created_at as ca,j.created_at as ca
    selectStmtA = "SELECT * FROM (SELECT DISTINCT j.id ,j.job_id as Job_ID, u.id as bdm_id, j.job_title as job_title, " \
                  "cl.company_name AS client_name,j.employment_type, j.min_salary ,j.max_salary ,j.min_rate ," \
                  "j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.job_posted_date AS job_date, cl.country, j.number_of_opening, " \
                  "j.status FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN " \
                  "`osms_clients` as cl on j.client_name_id = cl.id WHERE u.is_active = '1' " \
                  "AND u.role IN ('9', '2') " + filterQuery + " ORDER BY client_name,job_date ASC) AS A "

    selectStmtB = "LEFT JOIN (select j.id as job_id, " + formulaFields() + ", cjs.notes as remarks from `osms_job_description` as j , `osms_candidates` as ca , " \
                                                                 "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE cjs.submission_date >= '" + str(
        start_date) + "' " \
                      "AND cjs.submission_date <= '" + str(
        end_date) + "' AND cjs.stage_id = s.id AND cjs.job_description_id = j.id AND " \
                    "cjs.candidate_name_id = ca.id GROUP BY j.id) AS B ON A.id = B.job_id "

    selectStmtC = "LEFT JOIN (select j.id as jobid, " + internalFormulaFields() + ", cjs.notes as remarks from `osms_job_description` as j , `osms_candidates` as ca , " \
                                                                           "`candidates_stages` as s , `internal_candidates_jobs_stages` as cjs WHERE cjs.submission_date >= '" + str(
        start_date) + "' " \
                      "AND cjs.submission_date <= '" + str(
        end_date) + "' AND cjs.stage_id = s.id AND cjs.job_description_id = j.id AND " \
                    "cjs.candidate_name_id = ca.id GROUP BY j.id ) AS C ON A.id = C.jobid "

    query = selectStmtA + selectStmtB + selectStmtC
    queryset = Candidates.objects.raw(query)


    """    if bdm_id is not None and country is not None and country != 'ALL':
        bdm_id = str(bdm_id).replace("-", "")
        logger.info("BDM and Country both are not None")
        selectStmtA = "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, u.id as bdm_id, j.job_title as job_title, " \
                      "cl.company_name AS client_name,j.employment_type, j.min_salary ,j.max_salary ,j.min_rate ," \
                      "j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date, cl.country, j.number_of_opening " \
                      " FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN " \
                      "`osms_clients` as cl on j.client_name_id = cl.id WHERE j.status = 'Active' AND u.is_active = '1' " \
                      "AND u.role IN ('9', '2') AND j.created_by_id = '" + bdm_id + "' AND j.country = '" + country + "' ORDER BY client_name, job_date ASC) AS A LEFT " \
                      "JOIN "

        selectStmtB = "(select j.id as job_id, " + formulaFields() + ", cjs.notes as remarks from `osms_job_description` as j , `osms_candidates` as ca , " \
                                                                    "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE cjs.submission_date >= '" + str(start_date) + "' " \
                                                                    "AND cjs.submission_date <= '" + str(end_date) + "' AND cjs.stage_id = s.id AND cjs.job_description_id = j.id AND " \
                                                                    "cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id; "
        query = selectStmtA + selectStmtB
        queryset = Candidates.objects.raw(query)
    elif bdm_id is not None:
        bdm_id = str(bdm_id).replace("-", "")
        logger.info("BDM are not None")
        selectStmtA = "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, u.id as bdm_id, j.job_title as job_title, " \
                      "cl.company_name AS client_name,j.employment_type, j.min_salary ,j.max_salary ,j.min_rate ," \
                      "j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date, cl.country, j.number_of_opening " \
                      " FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN " \
                      "`osms_clients` as cl on j.client_name_id = cl.id WHERE j.status = 'Active' AND u.is_active = '1' " \
                      "AND u.role IN ('9', '2') AND j.created_by_id = '" + bdm_id + "' ORDER BY client_name, job_date ASC) AS A LEFT " \
                                                                                    "JOIN "

        selectStmtB = "(select j.id as job_id, " + formulaFields() + ", cjs.notes as remarks  from `osms_job_description` as j , `osms_candidates` as ca , " \
                                                                     "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE cjs.submission_date >= '" + str(start_date) + "' " \
                                                                                                                                                                                "AND cjs.submission_date <= '" + str(end_date) + "' AND cjs.stage_id = s.id AND cjs.job_description_id = j.id AND " \
                                                                                                                                                                                                                            "cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id; "
        query = selectStmtA + selectStmtB

        queryset = Candidates.objects.raw(query)
    else:
        logger.info("startdate and enddate are not None")
        selectStmtA = "SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, u.id as bdm_id, j.job_title as job_title, " \
                      "cl.company_name AS client_name,j.employment_type, j.min_salary ,j.max_salary ,j.min_rate ," \
                      "j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date, cl.country, j.number_of_opening " \
                      " FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN " \
                      "`osms_clients` as cl on j.client_name_id = cl.id WHERE j.status = 'Active' AND u.is_active = '1' " \
                      "AND u.role IN ('9', '2') ORDER BY client_name, job_date ASC) AS A LEFT " \
                                                                                    "JOIN "

        selectStmtB = "(select j.id as job_id, " + formulaFields() + ", cjs.notes as remarks from `osms_job_description` as j , " \
                                                                     "`osms_candidates` as ca, `candidates_stages` as " \
                                                                     "s , `candidates_jobs_stages` as cjs WHERE " \
                                                                     "cjs.submission_date >= '" + str(start_date) + "' AND " \
                                                                                                               "cjs.submission_date <= '" + str(end_date) + "' AND cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id; "
        query = selectStmtA + selectStmtB

        queryset = Candidates.objects.raw(query)"""
    # logger.info(queryset.query)
    return queryset


def recruiter_calls_performance_summary_by_job_and_recruiter(start_date, end_date, recruiter_id, country):
    logger.info("recruiter_id: " + str(recruiter_id))
    logger.info("country: " + str(country))
    logger.info("start_date: " + str(start_date))
    logger.info("end_date: " + str(end_date))
    start_date = str(start_date) + " 00:00:00"
    end_date = str(end_date) + " 23:59:59"
    filterQuery = ""

    if recruiter_id is not None and (country is not None and country != 'none' and country != 'ALL'):
        recruiter_id = str(recruiter_id).replace("-", "")
        filterQuery = "AND (jda.primary_recruiter_name_id = '" + recruiter_id + "' OR jda.secondary_recruiter_name_id = '" + recruiter_id + "') AND cl.country = '" + country + "' "
    elif recruiter_id is not None:
        recruiter_id = str(recruiter_id).replace("-", "")
        filterQuery = "AND (jda.primary_recruiter_name_id = '" + recruiter_id + "' OR jda.secondary_recruiter_name_id = '" + recruiter_id + "') "
    elif country is not None and country != 'none' and country != 'ALL':
        filterQuery = "AND cl.country = '" + country + "' "

    selectStmtA = "SELECT * FROM (SELECT j.id, j.job_title as job_title, " \
                  "cl.company_name AS client_name, CONCAT(u.first_name,' ',u.last_name) as bdm_name, jda.created_at AS job_date, cl.country, j.number_of_opening, " \
                  "(case when jda.primary_recruiter_name_id = '"+recruiter_id+"' then 'Primary' else 'Secondary' end) as " \
                  "assignment_type FROM job_description_assingment as jda LEFT JOIN `osms_job_description` as j ON jda.job_id_id = j.id LEFT " \
                  "JOIN candidates_jobs_stages as cjs ON j.id = cjs.job_description_id LEFT " \
                  "JOIN `users_user` as u ON j.created_by_id = u.id LEFT JOIN `osms_clients` as cl on j.client_name_id = cl.id WHERE (jda.created_at >= '" + str(
        start_date) + "' " \
                      "AND jda.created_at <= '" + str(
        end_date) + "')  " + filterQuery + " GROUP BY j.id ORDER BY job_date ASC) AS A "

    selectStmtB = "LEFT JOIN (select j.id as job_id, " + formulaFields() + ", cjs.notes as remarks from `osms_job_description` as j , `osms_candidates` as ca , " \
                                                                 "`candidates_stages` as s , `candidates_jobs_stages` as cjs WHERE cjs.submission_date >= '" + str(
        start_date) + "' " \
                      "AND cjs.submission_date <= '" + str(
        end_date) + "' AND cjs.stage_id = s.id AND cjs.job_description_id = j.id AND " \
                    "cjs.candidate_name_id = ca.id AND cjs.created_by_id = '"+ recruiter_id +"' GROUP BY j.id ) AS B ON A.id = B.job_id "

    selectStmtC = "LEFT JOIN (select j.id as jobid, " + internalFormulaFields() + ", cjs.notes as remarks from `osms_job_description` as j , `osms_candidates` as ca , " \
                                                                           "`candidates_stages` as s , `internal_candidates_jobs_stages` as cjs WHERE cjs.submission_date >= '" + str(
        start_date) + "' " \
                      "AND cjs.submission_date <= '" + str(
        end_date) + "' AND cjs.stage_id = s.id AND s.stage_name != 'Candidate Added' AND cjs.job_description_id = j.id AND " \
                    "cjs.candidate_name_id = ca.id AND cjs.created_by_id = '"+ recruiter_id +"' GROUP BY j.id ) AS C ON A.id = C.jobid "

    query = selectStmtA + selectStmtB + selectStmtC
    queryset = Candidates.objects.raw(query)

    return queryset