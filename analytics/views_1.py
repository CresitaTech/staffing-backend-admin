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

from analytics.utils import get_training_data, remove_stop_word
from candidates.filters import CandidateFilter
from candidates.models import Candidates
from candidates.serializers import CandidateSerializer
from jobdescriptions.models import jobModel
from jobdescriptions.serializers import JobDescriptionWriteSerializer
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


class BestMatchCandidatesViewSet(viewsets.ModelViewSet):
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
        logger.info("job_id: " + str(job_id))
        jobdescriptionObj = self.get_object(job_id)
        jobserializeObj = JobDescriptionWriteSerializer(jobdescriptionObj)
        jobdesc = ""
        if jobserializeObj.is_valid:
            # logger.info("===========: " + str(jobserializeObj))
            jobdesc = jobserializeObj.data['job_description']

        final_jobs = get_training_data("/home/admin/projectDir/staffingapp/static/Last100Resume.csv")
        # listing out the first 5 rows of the data set
        # adding the featured column back to pandas
        final_jobs['text'] = remove_stop_word(final_jobs)
        tfidf_vectorizer = TfidfVectorizer()
        # jobdesc = remove_stop_word(jobdesc)
        logger.info("jobdesc: ===== " + str(jobdesc))

        tfidf_model = tfidf_vectorizer.fit_transform((final_jobs['text']))  # fitting and transforming the vector

        vectorizer = CountVectorizer(decode_error="replace")
        transformer = TfidfTransformer()
        tfidf = transformer.fit_transform(vectorizer.fit_transform(final_jobs['text']))

        user_tfidf = tfidf_vectorizer.transform([jobdesc])
        output = map(lambda x: cosine_similarity(user_tfidf, x), tfidf)
        output2 = list(output)
        top = sorted(range(len(output2)), key=lambda i: output2[i], reverse=True)[:100]
        logger.info("Top Candidate: " + str(top))
        recommendation = pd.DataFrame(columns=['ApplicantID', 'CandidateID'])
        count = 0
        candIds = []
        for i in top:
            # recommendation.set_value(count, 'ApplicantID',u)
            # recommendation.set_value(count,'JobID' ,final_all['id'][i])
            # recommendation.at[count, 'ApplicantID'] = i
            recommendation.at[count, 'CandidateID'] = final_jobs['id'][i]
            candIds.append(final_jobs['id'][i])
            count += 1

        #candIds = recommendation['CandidateID']
        logger.info("Top Candidate candIds: " + str(candIds))
        # queryset = Candidates.objects.raw("SELECT * FROM osms_candidates WHERE id IN %s", [candIds])
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


    def create(self, request):
        serializeObj = ParserSerializer(data=request.data)
        if serializeObj.is_valid():
            obj = serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id)
            logger.info(obj.resume)
            file_path = '/home/admin/projectDir/staging/staffingapp/media/'+str(obj.resume)  # full path to text.
            logger.info(file_path)

            text = "None"


            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return jobModel.objects.get(pk=pk)
        except jobModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        jobdescriptionObj = self.get_object(pk)
        serializeObj = JobDescriptionWriteSerializer(jobdescriptionObj)
        return Response(serializeObj.data)
    def update(self, request, pk):
        vendorObj = self.get_object(pk)
        serializeObj = ParserSerializer(vendorObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        vendorObj = self.get_object(pk)
        vendorObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

