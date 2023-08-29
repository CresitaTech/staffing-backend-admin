from rest_framework import serializers
from vendors.models import vendorModel , vendorEmailTemplateModel , emailConfigurationModel , VendorListModel , VendorListDataModel


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = vendorModel
        fields="__all__"

class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = vendorEmailTemplateModel
        fields="__all__"

class EmailConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = emailConfigurationModel
        fields="__all__"
        
class VendorListSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorListModel
        fields="__all__"
        depth = 2
        
class VendorListWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorListModel
        fields="__all__"
        
class VendorListDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorListDataModel
        fields = "__all__"
        depth = 2