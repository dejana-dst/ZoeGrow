from django.shortcuts import render,get_list_or_404, get_object_or_404
from .serializers import *
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions,viewsets,generics,exceptions
from .permissions import *
from django.http import HttpResponse, JsonResponse
from datetime import date,timedelta

# Create your views here.





class UserListView(generics.ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    queryset = User.objects.all()
    serializer_class = UserSerializer




class UserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly]
    queryset=User.objects.all()
    serializer_class=UserSerializer
    


class UserAdminManageView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAdminUser,)
    queryset=User.objects.all()
    serializer_class=UserSerializer


class PlantListView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,IsAdminOrReadOnly,)
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer


class PlantRecommendedView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,IsAdminOrReadOnly,)
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer

    def get_queryset(self, *args, **kwargs):
        try:
            user = User.objects.get(pk=self.request.user.pk)
            zone = user.profile.location_zone
        except User.DoesNotExist:
            raise exceptions.NotFound() 

        queryset_list = Plant.objects.filter(climatezones__overlap=[user.profile.location_zone])
        return queryset_list

class PlantDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,IsAdminOrReadOnly,)
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer


class CalendarListView(generics.ListCreateAPIView):
    permission_classes = (IsOwnerOrReadOnly,)
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer

    def get_queryset(self, *args, **kwargs):
        try:
            user = User.objects.get(pk=self.request.user.pk)
        except User.DoesNotExist:
            raise exceptions.NotFound() 

        queryset_list = Calendar.objects.filter(user=user)
        return queryset_list


    def perform_create(self, serializer):
        

        plant_id=self.request.data['plant_id']

        if not plant_id:
            raise exceptions.NotFound() 
        plant = Plant.objects.get(pk=plant_id)

        if not plant:
            raise exceptions.NotFound() 

        serializer.save(user=self.request.user,plant=plant)

    

class CalendarDetailView(generics.RetrieveUpdateDestroyAPIView):


    permission_classes = (IsOwner,)
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer

    def get_object(self):
        
        try:
            user = User.objects.get(pk=self.request.user.pk)
        except User.DoesNotExist:
            raise exceptions.NotFound()


        plant_id=self.kwargs.get("plant_id")
        if not plant_id:
            raise exceptions.NotFound() 
        plant = Plant.objects.get(pk=plant_id)
        if not plant:
            raise exceptions.NotFound() 

        try:
            calendar = (Calendar.objects.get( user=user, plant=plant))
        except Calendar.DoesNotExist:
            raise exceptions.NotFound()

        return calendar

    def put(self, request, *args, **kwargs):
        serializer_class = CalendarSerializer
        calendar = self.get_object()
        serializer_class.update(self, instance=calendar,validated_data=self.request.data)
        return super(CalendarDetailView, self).update(request, *args, **kwargs)

      


class EventRecommendedView(generics.ListAPIView):
    permission_classes = (IsOwner,)
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self, *args, **kwargs):
        calendar = CalendarDetailView.get_object(self)
        plant = calendar.plant
        
        past_events = Event.objects.filter(calendar_id=calendar.id)
        future_events=[]
        
        inside_event=Event.objects.filter(calendar_id=calendar.id,status="INSIDE").last()
        outside_event=Event.objects.filter(calendar_id=calendar.id,status="OUTSIDE").last()

        last_harvest_event=Event.objects.filter(calendar_id=calendar.id,status="HARVEST").last()
        last_feed_event=Event.objects.filter(calendar_id=calendar.id,status="FEED").last()

        last_water_event=Event.objects.filter(calendar_id=calendar.id,status="WATER").last()
        if last_water_event:
            delta=date.today()-last_water_event.day
            if(delta>timedelta(days=plant.water_every_X_days)):
                #add new event to array for today
                next_day=date.today()
            else:
                next_day=last_water_event.day+timedelta(days=plant.water_every_X_days)
            for i in range(1,30):
                future_event={'day':next_day,'status':"WATER"}
                next_day=next_day+timedelta(days=plant.water_every_X_days)
                future_events.append(future_event)
        elif calendar.status!="NOT PLANTED" :
            next_day=date.today()
            for i in range(1,30):
                future_event={'day':next_day,'status':"WATER"}
                next_day=next_day+timedelta(days=plant.water_every_X_days)
                future_events.append(future_event)

            #add new event on   

        if last_harvest_event and plant.harvest_every_X_days:
            delta=date.today()-last_harvest_event.day
            if(delta>timedelta(days=plant.harvest_every_X_days)):
                #add new event to array for today
                next_day=date.today()
            else:
                next_day=last_harvest_event.day+timedelta(days=plant.harvest_every_X_days)
            for i in range(1,4):
                future_event={'day':next_day,'status':"HARVEST"}
                next_day=next_day+timedelta(days=plant.harvest_every_X_days)
                future_events.append(future_event)
        
        elif (not last_harvest_event) and plant.harvest_in_X_days and calendar.status!="NOT PLANTED":
            #first harvest
            if inside_event:
                next_day=inside_event.day+timedelta(days=plant.harvest_in_X_days)
            elif outside_event:
                next_day=outside_event.day+timedelta(days=plant.harvest_in_X_days)
            delta=next_day-date.today()
            if delta<timedelta(days=0):
                next_day=date.today()
            
            future_event={'day':next_day,'status':"HARVEST"}
            
            future_events.append(future_event)

            if plant.harvest_every_X_days:
                for i in range(1,3):
                    next_day=next_day+timedelta(days=plant.harvest_every_X_days)
                    future_event={'day':next_day,'status':"HARVEST"}
                    
                    future_events.append(future_event)
       
       
       
        if last_feed_event:
            delta=date.today() - last_feed_event.day
            if(delta>timedelta(days=plant.feed_every_X_months*30)):
                #add new event to array for today
                next_day=date.today()
            else:
                next_day=last_feed_event.day+timedelta(days=plant.feed_every_X_months*30)
            for i in range(1,5):
                future_event={'day':next_day,'status':"FEED"}
                next_day=next_day+timedelta(days=plant.feed_every_X_months*30)
                future_events.append(future_event)

        elif calendar.status!="NOT PLANTED" :
            next_day=date.today()
            for i in range(1,5):
                future_event={'day':next_day,'status':"FEED"}
                next_day=next_day+timedelta(days=plant.feed_every_X_months*30)
                future_events.append(future_event)
       
        future_events = sorted(future_events, key=lambda k: k['day'])
        return future_events










class EventListView(generics.ListCreateAPIView):
    permission_classes = (IsOwner,)
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self, *args, **kwargs):
        calendar = CalendarDetailView.get_object(self)
        queryset_list = Event.objects.filter(calendar_id=calendar.id)
        return queryset_list


    def perform_create(self, serializer):
        calendar = CalendarDetailView.get_object(self) 
        serializer.save(calendar_id=calendar.id)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsOwner,)
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_object(self):
        
        calendar = CalendarDetailView.get_object(self)
        event_id=self.kwargs.get("event_id")

        return Event.objects.get(pk=event_id,calendar_id=calendar.id)

    def put(self, request, *args, **kwargs):
        serializer_class = EventSerializer
        event = self.get_object()
        serializer_class.update(self, instance=event,validated_data=self.request.data)
        return super(EventDetailView, self).update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """  serializer_class = EventSerializer
        event = self.get_object() 
        event.delete() """
        #serializer_class.destroy(self,instance=event)
        return super(EventDetailView, self).destroy(request, *args, **kwargs)  


class CategoryListView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,IsAdminOrReadOnly,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,IsAdminOrReadOnly,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ThreadListView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Thread.objects.all( )
    serializer_class = ThreadSerializer


    def get_queryset(self, *args, **kwargs):
        category_id=self.kwargs.get("category_id")
        category = Category.objects.get(pk=category_id)
        queryset_list = Thread.objects.filter(category=category)
        return queryset_list

    def perform_create(self, serializer):
        
        category_id=self.kwargs.get("category_id")
        if not category_id:
            raise exceptions.NotFound() 
        category = Category.objects.get(pk=category_id)
        if not category:
            raise exceptions.NotFound() 
        
        newThread = serializer.save(createdBy=self.request.user,category=category,content=self.request.data['content'])



class ThreadDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,IsOwnerOrReadOnly)
    queryset = Thread.objects.all()
    serializer_class = ThreadDetailSerializer

    def get_object(self):
         
        thread_id=self.kwargs.get("thread_id")

        return Thread.objects.get(pk=thread_id)

    def put(self, request, *args, **kwargs):
        #serializer_class = ThreadSerializer
                
        category_id=self.kwargs.get("category_id")
        if not category_id:
            raise exceptions.NotFound() 
        category = Category.objects.get(pk=category_id)
        if not category:
            raise exceptions.NotFound()
        thread_id=self.kwargs.get("thread_id")
        
        thread = self.get_object()
        serializer_class.update(self, instance=event,validated_data=self.request.data)
        return super(ThreadDetailView, self).update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super(ThreadDetailView, self).destroy(request, *args, **kwargs)  


class PostsListView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self, *args, **kwargs):
        thread = ThreadDetailView.get_object(self)
        queryset_list = Post.objects.filter(thread=thread.id)
        return queryset_list


    def perform_create(self, serializer):
        thread = ThreadDetailView.get_object(self) 
        last_post=Post.objects.filter(thread=thread.id).last()
        serializer.save(thread=thread,postedBy=self.request.user, parentPost=last_post.id)
        thread.save()
    


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,IsOwnerOrReadOnly,)
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_object(self):
         
        post_id=self.kwargs.get("post_id")
        return Post.objects.get(pk=post_id)


    def put(self, request, *args, **kwargs):
        serializer_class = PostSerializer
        post = self.get_object()
        serializer_class.update(self, instance=event,validated_data=self.request.data)
        return super(PostDetailView, self).update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super(PostDetailView, self).destroy(request, *args, **kwargs)  
