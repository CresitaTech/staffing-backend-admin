DELIMITER $$
CREATE DEFINER=`Nareshkhuriwal`@`localhost` PROCEDURE `get_jobs_summary_by_date_range`(IN startData Date, IN endDate Date)
BEGIN
	SELECT * FROM (SELECT j.id ,j.job_id as Job_ID, j.job_title as job_title, cl.company_name AS client_name,j.employment_type,
	j.min_salary ,j.max_salary ,j.min_rate ,j.max_rate, CONCAT(u.first_name,' ',u.last_name) as bdm_name, j.created_at AS job_date,
	cl.country FROM `osms_job_description` as j LEFT JOIN `users_user` as u on j.created_by_id = u.id LEFT JOIN `osms_clients` as cl
	on j.client_name_id = cl.id WHERE j.created_at >= startData AND j.created_at <= endDate )AS A LEFT JOIN (select j.id as job_id ,
	sum(case when s.stage_name = 'Candidate Review' then 1 else 0 end) as CandidateReview,
	sum(case when s.stage_name = 'Rejected By Team' then 1 else 0 end) as RejectedByTeam ,
	sum(case when s.stage_name != 'Candidate Added' then 1 else 0 end) as Submission ,
	sum(case when s.stage_name = 'Client Interview - Second' then 1 else 0 end) as ClientInterviewSecond ,
	sum(case when s.stage_name = 'Sendout Reject' then 1 else 0 end) as SendoutReject ,
	sum(case when s.stage_name = 'Client Interview - First' then 1 else 0 end) as ClientInterviewFirst ,
	sum(case when s.stage_name = 'Offer Rejected' then 1 else 0 end) as OfferRejected ,
	sum(case when s.stage_name = 'Shortlisted' then 1 else 0 end) as Shortlisted ,
	sum(case when s.stage_name = 'Second Interview Reject' then 1 else 0 end) as SecondInterviewReject ,
	sum(case when s.stage_name = 'Hold by Client' then 1 else 0 end) as HoldbyClient,
	sum(case when s.stage_name = 'Interview Select' then 1 else 0 end) as InterviewSelect ,
	sum(case when s.stage_name = 'Offer Backout' then 1 else 0 end) as OfferBackout ,
	sum(case when s.stage_name = 'Hold by BDM' then 1 else 0 end) as HoldbyBDM,
	sum(case when s.stage_name = 'Internal Interview' then 1 else 0 end) as InternalInterview,
	sum(case when s.stage_name = 'Interview Backout' then 1 else 0 end) as InterviewBackout,
	sum(case when s.stage_name = 'Feedback Awaited' then 1 else 0 end) as FeedbackAwaited,
	sum(case when s.stage_name = 'Internal Interview Reject' then 1 else 0 end) as InternalInterviewReject,
	sum(case when s.stage_name = 'Placed' then 1 else 0 end) as Placed,
	sum(case when s.stage_name = 'Offered' then 1 else 0 end) as Offered,
	sum(case when s.stage_name = 'Interview Reject' then 1 else 0 end) as InterviewReject,
	sum(case when s.stage_name = 'Submission Reject' then 1 else 0 end) as SubmissionReject,
	sum(case when s.stage_name = 'SendOut' then 1 else 0 end) as SendOut

	from `osms_job_description` as j , `osms_candidates` as ca , `candidates_stages` as s , `candidates_jobs_stages` as cjs
	WHERE cjs.stage_id = s.id AND cjs.job_description_id = j.id AND cjs.candidate_name_id = ca.id GROUP BY j.id ) AS B ON A.id = B.job_id;

END$$
DELIMITER ;