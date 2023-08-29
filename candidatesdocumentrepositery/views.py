from django.shortcuts import render

# Create your views here.
from candidatesdocumentrepositery.models import candidatesRepositeryModel
from candidatesdocumentrepositery.serializers import CandidateDocumentSerializer , CandidateDocumentWriteSerializer
from rest_framework import viewsets
from candidates.models import Candidates
from candidatesdocumentrepositery.utils import sendBDMMail
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, filters , generics
from rest_framework.permissions import DjangoModelPermissions
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class CandidatesDocumentRepoSet(viewsets.ModelViewSet):

    queryset = candidatesRepositeryModel.objects.all()
    serializer_class = CandidateDocumentSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ("repo_name", "candidate_name__first_name", "created_at")
    search_fields = ('repo_name', 'candidate_name__first_name')
    ordering_fields = ['repo_name' , 'created_at' ,'candidate_name__first_name']
    ordering = ['repo_name' , 'created_at' , 'candidate_name__first_name']
    permission_classes = [DjangoModelPermissions]

    def list(self, request):
        #candidateDocObj = candidatesRepositeryModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CandidateDocumentSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CandidateDocumentSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = CandidateDocumentWriteSerializer(data=request.data)
        logger.info('New Repo Create data: ' + str(request.data))
        if serializeObj.is_valid():
            serializeObj.save(created_by_id = request.user.id , updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        logger.error('Repo Post Serialized Error: ' + str(serializeObj.errors))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return candidatesRepositeryModel.objects.get(pk=pk)
        except candidatesRepositeryModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        candidateDocObj = self.get_object(pk)
        serializeObj = CandidateDocumentWriteSerializer(candidateDocObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        candidateDocObj = self.get_object(pk)
        serializeObj = CandidateDocumentWriteSerializer(candidateDocObj, data=request.data)
        if serializeObj.is_valid():
            if 'resume' in serializeObj.validated_data:
                candidate_id  = str(candidateDocObj.candidate_name_id).replace('UUID', '').replace('(\'', '').replace('\')', '').replace('-', '')
                Candidates.objects.filter(id = candidate_id).update(resume = serializeObj.validated_data['resume'])
            serializeObj.save(updated_by_id=request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def partial_update(self, request, pk):
        candObj = self.get_object(pk)
        print(candObj)
        logger.info('Update Repo Data: ' + str(request.data))
        serializeObj = CandidateDocumentWriteSerializer(candObj, data=request.data , partial=True)
        if serializeObj.is_valid():
            if 'resume' in serializeObj.validated_data:
                candidate_id  = str(candObj.candidate_name_id).replace('UUID', '').replace('(\'', '').replace('\')', '').replace('-', '')
                obj = Candidates.objects.get(id = candidate_id)
                obj.resume = serializeObj.validated_data['resume']
                obj.save()
            serializeObj.save(updated_by_id=request.user.id)
            #sendBDMMail(request ,candObj.candidate_name_id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        logger.error('Repo Update Serialized Error: ' + str(serializeObj.errors))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        candidateDocObj = self.get_object(pk)
        candidateDocObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
class GetRepoList(generics.ListAPIView):
    serializer_class = CandidateDocumentSerializer
    queryset = candidatesRepositeryModel.objects.all()

    def get(self, request, format=None):
        if request.query_params.get('candidate_id'):
            candidate_id = str(request.query_params.get('candidate_id')).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')

            repoObj = candidatesRepositeryModel.objects.filter(candidate_name_id=candidate_id)
            serializer = CandidateDocumentWriteSerializer(repoObj, many=True)
            logger.info('Repo List For Candidate: ' + str(candidate_id))
            logger.info('Repo List For Candidate: ' + str(serializer.data))
            return Response(serializer.data)
    
    
    
    
    