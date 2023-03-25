from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *

class ClimateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Climate
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Profile
        fields = ('location', 'profile_image','location_zone')


class UserSerializer(serializers.ModelSerializer):
    
    profile = ProfileSerializer()
    class Meta:
        model = User
        fields = ['username', 'email','password', 'profile']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        #profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        #Profile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')

        profile = (instance.profile)
        
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        
        
        profile.location = profile_data.get('location', profile.location)
        profile.profile_image = profile_data.get('profile_image', profile.profile_image)
        polygons = Climate.objects.filter(wkb_geometry__contains=profile.location)

        profile.location_zone = polygons[0].climatecode

        profile.save()


        return instance



class FAQSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FAQ
        fields = ('answer', 'question')


class PlantSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Plant

        exclude = ('tracked', )

class EventSerializer(serializers.ModelSerializer):
    
    #calendar = CalendarSerializer()
    class Meta:
        model = Event
        fields = "__all__" #do we need to retrieve the detailed calendar info for every event?
        #exclude = ('calendar', )
    
    def create(self, validated_data):
        #profile_data = validated_data.pop('profile')
        
        status = validated_data['status']
        event = Event(**validated_data)
        event.save()
        if  status=="INSIDE" or status == "OUTSIDE":
            calendar = Calendar.objects.get(id=validated_data['calendar_id'])
            calendar.status = status
            calendar.save()

        if  status=="MOVE":
            calendar = Calendar.objects.get(id=validated_data['calendar_id'])
            old_status = calendar.status
            if old_status=="INSIDE":
                calendar.status="OUTSIDE"
            else:
                calendar.status="INSIDE"
            calendar.save()

        return event

    def update(self, instance, validated_data):
        
        instance.status = validated_data['status']
        instance.save()

        if  instance.status=="MOVE":
            calendar = Calendar.objects.get(id=instance.calendar.id)
            status = calendar.status
            if status=="INSIDE":
                calendar.status="OUTSIDE"
            else:
                calendar.status="INSIDE"
            calendar.save()

        return instance

class CalendarSerializer(serializers.ModelSerializer):
    
    events = EventSerializer(read_only=True)
    plant = PlantSerializer(required=False)
    
    user = UserSerializer(required=False)
    class Meta:
        model = Calendar
        fields = ('plant','user','status','events','id')

    def update(self, instance, validated_data):
        #plant_data = validated_data.pop('plant')
        #user_data = validated_data.pop('user')
        instance.status = validated_data['status']
        instance.save()

        return instance


class PostSerializer(serializers.ModelSerializer):

    postedBy = UserSerializer(required=False)

    class Meta:
        model = Post
        fields = ('content','created','id','edited','thread','parentPost',
        'postedBy','likesCount')

class ThreadDetailSerializer(serializers.ModelSerializer):
    posts = PostSerializer(read_only=True)
    
    
    createdBy = UserSerializer(required=False)
    class Meta:
        model = Thread
        fields = ('posts','locked','category','title','createdBy','created','id','edited')

class ThreadSerializer(serializers.ModelSerializer):
    
    createdBy = UserSerializer(required=False)
    class Meta:
        model = Thread
        fields = "__all__"
    
    def create(self, validated_data):
        #profile_data = validated_data.pop('profile')
        
        content = validated_data.pop('content')
        
        thread = Thread(**validated_data)
        thread.save()
        Post.objects.create(thread=thread,postedBy=thread.createdBy, content=content)
        
        #Profile.objects.create(user=user, **profile_data)
        return thread

class CategorySerializer(serializers.ModelSerializer):
    threads = ThreadSerializer(read_only=True)
    class Meta:
        model = Category
        fields = ('name','id','threads')