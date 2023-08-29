from rest_framework import serializers


class CandidateWebsiteSerializer(serializers.Serializer):
    candidate_name = serializers.CharField(max_length=240)
    client_name = serializers.CharField(max_length=240)
    client_phone = serializers.CharField(max_length=240)
    client_email = serializers.CharField(max_length=240)
    client_message = serializers.CharField(max_length=1000 , allow_blank=True, allow_null=True)


class PostalRequestSerializer(serializers.Serializer):
    maildata = serializers.CharField(max_length=240)
    created_at = serializers.CharField(max_length=240)
    updated_at = serializers.CharField(max_length=240)


class JobWebsiteSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=240)
    last_name = serializers.CharField(max_length=240)
    job_title = serializers.CharField(max_length=240)
    date_of_birth = serializers.CharField(max_length=240 ,allow_blank=True, allow_null=True)
    qualification = serializers.CharField(max_length=400 , allow_blank=True, allow_null=True)
    primary_email = serializers.CharField(max_length=240)
    secondary_email = serializers.CharField(max_length=240 , allow_blank=True, allow_null=True)
    primary_phone_number = serializers.CharField(max_length=240)
    secondary_phone_number = serializers.CharField(max_length=240 , allow_blank=True, allow_null=True)
    designation = serializers.CharField(max_length=240)
    salary_Rate = serializers.CharField(max_length=240)
    visa = serializers.CharField(max_length=240)
    company_name = serializers.CharField(max_length=240, allow_blank=True, allow_null=True)
    total_experience = serializers.CharField(max_length=240)
    total_exp_usa = serializers.CharField(max_length=240 , allow_blank=True, allow_null=True)
    any_offer_in_hand = serializers.CharField(max_length=240 , allow_blank=True, allow_null=True)
    current_location = serializers.CharField(max_length=240 , allow_blank=True, allow_null=True)
    skills1 = serializers.CharField(max_length=400 , allow_blank=True, allow_null=True)
    skills2 = serializers.CharField(max_length=400 , allow_blank=True, allow_null=True)
    remarks = serializers.CharField(max_length=1000 , allow_blank=True, allow_null=True)
    resume = serializers.FileField(max_length=None, allow_empty_file=False)


