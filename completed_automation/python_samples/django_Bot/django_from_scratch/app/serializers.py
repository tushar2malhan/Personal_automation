from attr import field
from numpy import require
from rest_framework import serializers
from app.models import Queries

class StudentSerializer(serializers.ModelSerializer):
    # do validations on name column 
    name = serializers.CharField(max_length=100, required=True)
    class Meta :
        model = Queries
        fields = '__all__'



class MySerializer(serializers.Serializer):
    id = serializers.IntegerField(default=-1)
    name = serializers.CharField(max_length=100,  required=True)
    roll = serializers.IntegerField( required = True)
    city = serializers.CharField(max_length=100, required = False)

    def create(self, validated_data):
        return Queries.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.age = validated_data.get('age', instance.age)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance
    
    def validate_id(self, value):
        if value < 0:
            raise serializers.ValidationError("Roll number cannot be negative")
        elif value > 100:
            print('value\t\n\t\t', value)
            raise serializers.ValidationError(value)
        return value
    
    def validate(self, attrs):
        return super().validate(attrs)