import logging
import os

from analytics.models import ParserModel
from analytics.serializers import ParserSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, filters, generics
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.permissions import AllowAny

from analytics.utils import get_training_data, readPdf, readDocx, readDoc, preprocess_text, clean_doc, \
    remove_punctuations, remove_html, remove_url, remove_all_special, remove_hyperlinks, remove_cases, remove_achor_tag, \
    remove_extra_spaces, remove_numbers, remove_digits, remove_non_alphabetic
from candidates.filters import CandidateFilter
from candidates.models import Candidates
from candidates.serializers import CandidateSerializer
from jobdescriptions.filters import JDFilter
from jobdescriptions.models import jobModel
from jobdescriptions.serializers import JobDescriptionWriteSerializer, JobDescriptionSerializer
from staffingapp.settings import MEDIA_URL, BASE_DIR
from users.models import User
from users.serializers import UserSerializer

logger = logging.getLogger(__name__)

import pandas as pd
import numpy as np
import re
import os
import pickle
import logging  # Setting up the loggings to monitor gensim
logging.basicConfig(format="%(levelname)s - %(asctime)s: %(message)s", datefmt= '%H:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__)
# uploading the file from the local drive
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

import textdistance as td
from sklearn.metrics.pairwise import cosine_similarity
import sklearn
from sentence_transformers import SentenceTransformer
import pickle


class RecommendedCandidatesViewSet(viewsets.ModelViewSet):
    queryset = Candidates.objects.none()
    serializer_class = CandidateSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, ]  # SearchFilter,
    ordering_fields = ['first_name', 'created_at']
    ordering = ['first_name', 'created_at']
    filter_fields = ["first_name", "company_name", "created_at", ]
    search_fields = ['first_name', 'last_name', 'skills_1', 'skills_2', 'job_description__job_title', 'primary_email',
                     'job_description__client_name__company_name']
    filter_class = CandidateFilter
    permission_classes = [DjangoModelPermissions]

    def list(self, request):
        job_id = request.query_params.get('job_id')
        candObj = User.objects.get(pk=request.user.id)
        serializeObj = UserSerializer(candObj)
        # print(userGroup)
        logger.info("job_id: " + str(job_id))
        jobdescriptionObj = self.get_object(job_id)
        jobserializeObj = JobDescriptionWriteSerializer(jobdescriptionObj)
        jobdesc = ""
        if jobserializeObj.is_valid:
            jobdesc = jobserializeObj.data['job_description']


        try:
            # text = await preprocess_text(text)
            text = preprocess_text(jobdesc)
            text = clean_doc(text)
            # print("clean_doc completed")
            text = remove_punctuations(text)
            # print("remove_punctuations completed")
            text = remove_html(text)
            # print("remove_html completed")
            text = remove_url(text)
            # print("remove_url completed")
            text = remove_all_special(text)
            # print("remove_newline completed")
            # text = await remove_stopwords(text)
            # print("remove_emoji completed")
            text = remove_hyperlinks(text)
            text = remove_cases(text)
            text = remove_achor_tag(text)
            text = remove_extra_spaces(text)
            text = remove_numbers(text)
            text = remove_digits(text)
            text = remove_non_alphabetic(text)
            # text = lemma_traincorpus(text)
            # text = await remove_short_tokens(text)
        except:
            print("Oops! Error occurred. File not formated.")

        logger.info("jobdesc: ===== " + str(text))
        df = pd.read_csv("/var/www/staffing_backend/static/cleaned_resume_4731.csv")

        # loaded_model = pickle.load(open("/home/admin/projectDir/staffingapp/static/candidates-embedding.pkl", 'rb'))
        loaded_model = pickle.load(open("/var/www/staffing_backend/static/candidates-embedding.pkl", 'rb'))
        # listing out the first 5 rows of the data set
        sen = [text]
        model = SentenceTransformer('bert-base-nli-mean-tokens')
        sen_embedding = model.encode(sen)

        output = map(lambda x: cosine_similarity(sen_embedding, [x]), loaded_model)
        output2 = list(output)
        top = sorted(range(len(output2)), key=lambda i: output2[i], reverse=True)[:100]
        # logger.info("Top Candidate: " + str(top))
        recommendation = pd.DataFrame(columns=['ApplicantID', 'CandidateID'])
        count = 0
        candIds = []
        for i in top:
            candIds.append(df['id'][i])
            count += 1

        queryset = Candidates.objects.filter(id__in=candIds)
        logger.info('Query Best Matching....')
        logger.info(queryset.query)

        # serializer = CandidateSerializer(queryset, many=True)
        # return Response(serializer.data)

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CandidateSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CandidateSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def get_object(self, pk):
        try:
            return jobModel.objects.get(pk=pk)
        except jobModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class RecommendedJobsViewSet(viewsets.ModelViewSet):
    queryset = jobModel.objects.all()
    serializer_class = JobDescriptionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, ]  # SearchFilter,
    ordering_fields = ['client_name__company_name', 'created_at']
    ordering = ['client_name__company_name', 'created_at']
    filter_fields = ["client_name__company_name", "job_title", "created_at", ]
    search_fields = ['client_name__company_name', 'priority', 'job_id', 'job_title', 'nice_to_have_skills',
                     'key_skills']
    filter_class = JDFilter
    permission_classes = [DjangoModelPermissions]

    def list(self, request):
        candidate_id = request.query_params.get('candidate_id')
        candObj = User.objects.get(pk=request.user.id)
        serializeObj = UserSerializer(candObj)
        # print(serializeObj.data)
        groups = dict(serializeObj.data)
        # print(groups)
        # print(len(groups))
        userGroupDict = None
        userGroup = None
        if len(groups['groups']) > 0:
            # print(groups['groups'])
            # print(groups['groups'][0])
            # userGroupDict = None
            userGroupDict = dict(groups['groups'][0])
        if userGroupDict is not None:
            userGroup = userGroupDict['name']
        # print(userGroup)
        logger.info('userGroup Data: %s' % userGroup)
        logger.info("candidate_id: " + str(candidate_id))
        candidateObj = self.get_object(candidate_id)
        candidateSer = CandidateSerializer(candidateObj)
        resume_path = ""
        if candidateSer.is_valid:
            resume_path = candidateSer.data['resume']
        logger.info("resume_path: " + str(resume_path))

        dir_path = r'/home/admin/projectDir/staffingapp/'

        fileName = dir_path + resume_path
        logger.info("fileName: " + fileName)
        ext = os.path.splitext(fileName)[-1].lower()
        print(ext)
        content = "NA"
        if ext == '.pdf':
            content = readPdf(fileName)
            # dataList.append(content)
        elif ext == '.docx':
            content = readDocx(fileName)
            # dataList.append([fileName, content])
            # dataList.append(content)
        elif ext == '.doc':
            content = readDoc(fileName)
            # dataList.append([fileName, content])
            # dataList.append(content)
        else:
            print('File format not matched')
            # dataList.append([fileName, content])
            # dataList.append(content)

        logger.info('File number ' + str(fileName) + ' Completed')

        try:
            # text = await preprocess_text(text)
            text = preprocess_text(content)
            text = clean_doc(text)
            # print("clean_doc completed")
            text = remove_punctuations(text)
            # print("remove_punctuations completed")
            text = remove_html(text)
            # print("remove_html completed")
            text = remove_url(text)
            # print("remove_url completed")
            text = remove_all_special(text)
            # print("remove_newline completed")
            # text = await remove_stopwords(text)
            # print("remove_emoji completed")
            text = remove_hyperlinks(text)
            text = remove_cases(text)
            text = remove_achor_tag(text)
            text = remove_extra_spaces(text)
            text = remove_numbers(text)
            text = remove_digits(text)
            text = remove_non_alphabetic(text)
            # text = lemma_traincorpus(text)
            # text = await remove_short_tokens(text)
        except:
            print("Oops! Error occurred. File not formated.")

        logger.info("Extract content: " + str(text))

        model = SentenceTransformer('bert-base-nli-mean-tokens')

        loaded_model = pickle.load(open("/home/admin/projectDir/staffingapp/static/jobs-embedding.pkl", 'rb'))
        # final_jobs = get_training_data("/home/admin/projectDir/staging/staffingapp/static/job_description_1697.csv")
        final_jobs = pd.read_csv("/home/admin/projectDir/staffingapp/static/job_description_1697.csv")
        # listing out the first 5 rows of the data set
        sen = [text]
        sen_embedding = model.encode(sen)

        output = map(lambda x: cosine_similarity(sen_embedding, [x]), loaded_model)
        output2 = list(output)
        top = sorted(range(len(output2)), key=lambda i: output2[i], reverse=True)[:100]
        # logger.info("Top Candidate: " + str(top))
        recommendation = pd.DataFrame(columns=['ApplicantID', 'JobID'])
        count = 0
        jobIds = []
        for i in top:
            recommendation.at[count, 'JobID'] = final_jobs['id'][i]
            jobIds.append(final_jobs['id'][i])
            count += 1

        #candIds = recommendation['CandidateID']
        # logger.info("Top Candidate candIds: " + str(jobIds))
        # queryset = Candidates.objects.raw("SELECT * FROM osms_candidates WHERE id IN %s", [candIds])
        queryset = jobModel.objects.filter(id__in=jobIds)
        logger.info('Query Best Matching....')
        logger.info(queryset.query)

        # serializer = CandidateSerializer(queryset, many=True)
        # return Response(serializer.data)

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = JobDescriptionSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = JobDescriptionSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def get_object(self, pk):
        try:
            return Candidates.objects.get(pk=pk)
        except Candidates.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)


