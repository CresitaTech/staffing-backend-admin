from rest_framework import serializers
from interviews.models import interviewsModel
from interviews.models import sourceModel
from interviews.models import feedbackModel

class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = sourceModel
        fields="__all__"

class InterviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = interviewsModel
        fields="__all__"
        depth = 1
        
class InterviewsWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = interviewsModel
        fields="__all__"

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = feedbackModel
        fields="__all__"
        depth = 1
        
class FeedbackWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = feedbackModel
        fields="__all__"