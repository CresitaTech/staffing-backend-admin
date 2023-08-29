from django.shortcuts import render

# Create your views here.
from interviewers.models import designationModel
from interviewers.serializers import DesignationSerializer
from interviewers.models import timeslotsModel
from interviewers.serializers import TimeSlotSerializer
from interviewers.models import interviewersModel
from interviewers.serializers import InterviewerSerializer , InterviewerWriteSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, filters
from rest_framework.permissions import DjangoModelPermissions

class DesignationViewSet(viewsets.ModelViewSet):

    queryset = designationModel.objects.all()
    serializer_class = DesignationSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ("name", "created_at")
    search_fields = ('name', 'created_at')
    ordering_fields = ['name' , 'created_at']
    ordering = ['name' , 'created_at']
    permission_classes = [DjangoModelPermissions]

    def list(self, request):
        #designationObj = designationModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = DesignationSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = DesignationSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = DesignationSerializer(data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(created_by_id = request.user.id , updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return designationModel.objects.get(pk=pk)
        except designationModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        designationObj = self.get_object(pk)
        serializeObj = DesignationSerializer(designationObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        designationObj = self.get_object(pk)
        serializeObj = DesignationSerializer(designationObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        designationObj = self.get_object(pk)
        designationObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TimeSlotViewSet(viewsets.ModelViewSet):

    queryset = timeslotsModel.objects.all()
    serializer_class = TimeSlotSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ("time_slot", "created_at")
    search_fields = ('time_slot', 'created_at')
    ordering_fields = ['time_slot' , 'created_at']
    ordering = ['time_slot' , 'created_at']
    permission_classes = [DjangoModelPermissions]

    def list(self, request):
        #timeslotObj = timeslotsModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TimeSlotSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TimeSlotSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = TimeSlotSerializer(data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(created_by_id = request.user.id , updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return timeslotsModel.objects.get(pk=pk)
        except timeslotsModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        timeslotObj = self.get_object(pk)
        serializeObj = TimeSlotSerializer(timeslotObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        timeslotObj = self.get_object(pk)
        serializeObj = TimeSlotSerializer(timeslotObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        timeslotObj = self.get_object(pk)
        timeslotObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class InterviewerViewSet(viewsets.ModelViewSet):

    queryset = interviewersModel.objects.all()
    serializer_class = InterviewerSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ("first_name", "created_at" , 'designation__name')
    search_fields = ('first_name', 'created_at' , 'designation__name')
    ordering_fields = ['first_name' , 'created_at' , 'designation__name']
    ordering = ['first_name' , 'created_at' , 'designation__name']
    permission_classes = [DjangoModelPermissions]
    

    def list(self, request):
        #interviewerObj = interviewersModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = InterviewerSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = InterviewerSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = InterviewerWriteSerializer(data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(created_by_id = request.user.id , updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return interviewersModel.objects.get(pk=pk)
        except interviewersModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        interviewerObj = self.get_object(pk)
        serializeObj = InterviewerWriteSerializer(interviewerObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        interviewerObj = self.get_object(pk)
        serializeObj = InterviewerWriteSerializer(interviewerObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        interviewerObj = self.get_object(pk)
        interviewerObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)