from reports import views
from rest_framework import routers
from django.urls import path, include

from reports.views import RecruiterPerformanceSummaryCSV, RecruiterPerformanceSummaryTable, \
    RecruiterPerformanceSummaryGraph, BdmPerformanceSummaryTable, BdmPerformanceSummaryCSV, BdmPerformanceSummaryGraph, \
    JobSummaryTable, JobSummaryCSV, JobSummaryGraph, AggregateData, TopClients, TopFivePlacement, ClinetDropdownList, \
    JobsDropdownList, JobsDashboardList, AssingedJobsList, GraphPointList, JobsByBDMSummaryTable, JobsByBDMSummaryCSV, \
    JobsByBDMSummaryGraph, ExportGraphsPointList, ActiveJobsAgingSummaryGraph, ActiveJobsAgingSummaryTable, \
    ActiveJobsAgingSummaryCSV, \
    MyCandidatesList, UnassignedJobsCSV, ClientRevenueReport, ClientRevenueReportCSV, JobSubmissionsByClientTable, \
    JobSubmissionsByClientCSV, JobSubmissionsByClientGraph

router = routers.DefaultRouter()
# router.register(r'candidates_summary_report', views.CandidateSummaryReportViewSet )
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # path('', include(router.urls)),
    # path('candidate_summary_report_apiview/', views.candidate_summary_view),
    path('recruiter_performance_summary_csv/', RecruiterPerformanceSummaryCSV.as_view(), name='recruiter_performance_summary_csv'),
    path('recruiter_performance_summary_table/', RecruiterPerformanceSummaryTable.as_view(), name='recruiter_performance_summary_table'),
    path('recruiter_performance_summary_graph/', RecruiterPerformanceSummaryGraph.as_view(), name='recruiter_performance_summary_graph'),

    path('bdm_performance_summary_csv/', BdmPerformanceSummaryCSV.as_view(), name='bdm_performance_summary_csv'),
    path('bdm_performance_summary_table/', BdmPerformanceSummaryTable.as_view(), name='bdm_performance_summary_table'),
    path('bdm_performance_summary_graph/', BdmPerformanceSummaryGraph.as_view(), name='bdm_performance_summary_graph'),

    path('job_summary_csv/', JobSummaryCSV.as_view(), name='job_summary_csv'),
    path('job_summary_table/', JobSummaryTable.as_view(), name='job_summary_table'),
    path('job_summary_graph/', JobSummaryGraph.as_view(), name='job_summary_graph'),

    path('job_submissions_by_client_csv/', JobSubmissionsByClientCSV.as_view(), name='job_submissions_by_client_csv'),
    path('job_submissions_by_client_table/', JobSubmissionsByClientTable.as_view(), name='job_submissions_by_client_table'),
    path('job_submissions_by_client_graph/', JobSubmissionsByClientGraph.as_view(), name='job_submissions_by_client_graph'),

    path('get_dashboard_data/', AggregateData.as_view(), name='get_dashboard_data'),
    path('get_top_clients/', TopClients.as_view(), name='Top Client List'),
    path('get_top_five_placement/', TopFivePlacement.as_view(), name='Top Five Placement Data'),
    path('get_client_dropdown_list/', ClinetDropdownList.as_view(), name='Clinet Dropdown List'),
    path('get_jobs_dropdown_list/', JobsDropdownList.as_view(), name='Jobs Dropdown List'),
    path('get_jobs_dashboard_list/', JobsDashboardList.as_view(), name='Jobs Dashboard List'),
    path('get_assinged_dashboard_list/', AssingedJobsList.as_view(), name='Unassinged/assinged List'),
    path('get_graph_point_list/', GraphPointList.as_view(), name='Graph Point List'),
    path('jobs_by_bdm_summary_table/', JobsByBDMSummaryTable.as_view(), name='Jobs By BDM Table'),
    path('jobs_by_bdm_summary_csv/', JobsByBDMSummaryCSV.as_view(), name='Jobs By BDM CSV'),
    path('jobs_by_bdm_summary_graph/', JobsByBDMSummaryGraph.as_view(), name='Jobs By BDM Graph'),
    path('export_graph_point_list/', ExportGraphsPointList.as_view(), name='Export Graph Point List'),
    path('active_jobs_aging_graph/', ActiveJobsAgingSummaryGraph.as_view(), name='Active Jobs Aging Graph'),
    path('active_jobs_aging_table/', ActiveJobsAgingSummaryTable.as_view(), name='Active Jobs Aging Table'),
    path('active_jobs_aging_csv/', ActiveJobsAgingSummaryCSV.as_view(), name='Active Jobs Aging CSV'),
    path('get_my_candidates/', MyCandidatesList.as_view(), name='My Candidates List'), 
    path('get_unasssigned_jobs_csv/', UnassignedJobsCSV.as_view(), name='Unassigned CSV'),
    
    path('get_client_revenue_graph/', ClientRevenueReport.as_view(), name='Client Revenue Graph'),
    path('get_client_revenue_csv/', ClientRevenueReportCSV.as_view(), name='Client Revenue CSV'),

    # Report testing url
    path('send_bdm_email/', views.send_bdm_email, name='Send BDM email'),
    path('send_recruiter_email/', views.send_recruiter_email, name='Send BDM email'),
    path('send_weekly_bdm_jobs/', views.send_weekly_bdm_jobs, name='Send BDM Weekend email'),
    path('send_weekly_recruiter_submission/', views.send_weekly_recruiter_submission, name='send_weekly_recruiter_submission'),
    path('send_weeklly_recuiter_performance_report/', views.send_weeklly_recuiter_performance_report, name='Send Recruiter Weekend email'),
    path('send_recruiter_summary_report/', views.send_recruiter_summary_report, name='Send Recruiter Summary email'),
    path('send_last_48hours_bdm_jobs/', views.send_last_48hours_bdm_jobs, name='Send BDM JOB Summary email'),
    path('bdm_daily_submission_report/', views.bdm_daily_submission_report, name='Send BDM JOB Summary email'),
    path('send_weekly_recruiter_submission_follow_up/', views.send_weekly_recruiter_submission_follow_up, name='send_weekly_recruiter_submission_follow_up')

]