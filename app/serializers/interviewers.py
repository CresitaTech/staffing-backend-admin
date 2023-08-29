from rest_framework import serializers
from interviewers.models import designationModel
from interviewers.models import timeslotsModel
from interviewers.models import interviewersModel

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = designationModel
        fields="__all__"

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = timeslotsModel
        fields="__all__"

class InterviewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = interviewersModel
        fields="__all__"
        depth = 1
        
class InterviewerWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = interviewersModel
        fields="__all__"