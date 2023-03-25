from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase,APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import *
import tempfile
from PIL import Image
from datetime import date   




class testProfileModel(TestCase):
 
    def test_profile_creation(self):
        User = get_user_model()
        user = User.objects.create(username="thisisauser", password="thisisapassword")
        # Check that a Profile instance has been crated
        self.assertIsInstance(user.profile, Profile)
        # Call the save method of the user to activate the signal
        user.save()
        self.assertIsInstance(user.profile, Profile)


class userProfileTestCase(APITestCase):
    
    def setUp(self):
        self.body = {'username':'auser','password':'apassword', 'email':'thisis@an.email'}
    


    def test_create_user_api(self):
        response = self.client.post('/api/auth/users/', self.body, format='json')
        self.assertEqual(201, response.status_code)
        self.assertEqual(User.objects.count(), 1)
        

    def test_userlist_unauthenticated(self):
        response=self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code,401)



    def test_api_authentication(self):
        #response=self.client.post('/api/auth/jwt/create/',{'username':'auser','password':'apassword'})
        #self.token=response.data["access"] if access else resp.data["refresh"]
        #self.client.credentials(HTTP_AUTHORIZATION='JWT '+self.token)
        response = self.client.post('/api/auth/users/', self.body, format='json')
        response=self.client.post('/api/auth/token/login/',{'username':'auser','password':'apassword'})

        self.token=response.data["auth_token"]
        self.client.credentials(HTTP_AUTHORIZATION='Token '+self.token)


        response=self.client.get('/api/auth/users/me/')
        self.assertEqual(response.status_code,200)

        profile_data= {'profile':{'location':'point (14.01 50.76)'}}
        response = self.client.patch('/api/auth/users/me/', profile_data, format='json')
        self.assertEqual(200, response.status_code)
        




class PlantTestCase(APITestCase):

     


    def test_create_plant_api_unauth(self):
        self.body = {'min_temperature':13,'max_temperature':31, 'water_every_X_days':12,
        'pet_safe':False,'name':'Bromeliad','feed_every_X_months':3,'light':'HIGH'}
   
        response = self.client.post('/api/v1/plants/', self.body, format='json')
        self.assertEqual(401, response.status_code)
        
    def test_plant_api_adminauth(self):    

        self.adminuser = User.objects.create_superuser('admin', 'admin@an.email', 'password')
        response=self.client.post('/api/auth/token/login/',{'username':'admin','password':'password'})
        self.token=response.data["auth_token"]
        self.client.credentials(HTTP_AUTHORIZATION='Token '+self.token)

        self.tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg',delete=False)
        image = Image.new('RGB', (100, 100))
        
        image.save(self.tmp_file.name)
        
        data = {'min_temperature':13,'max_temperature':31, 'water_every_X_days':12,
        'pet_safe':False,'name':'Bromeliad','feed_every_X_months':3,'light':'HIGH',
        'repot_every_X_years':0, 'image':self.tmp_file}   
        response = self.client.post('/api/v1/plants/', data=data, format='multipart')
        self.tmp_file.close()
        self.assertEqual(201, response.status_code)
        self.assertEqual(Plant.objects.count(), 1)
        returned_id=str(response.data["id"])
        data=response.data

        self.body = {'min_temperature':16,   'pet_safe':True}   
        response = self.client.patch('/api/v1/plants/'+returned_id+'/',self.body, format='json')
        self.assertEqual(200, response.status_code)

        data["min_temperature"]=16
        data["pet_safe"]=True
        response = self.client.get('/api/v1/plants/'+returned_id+'/', format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data, data)

        response = self.client.delete('/api/v1/plants/'+returned_id+'/', format='json')
        self.assertEqual(204, response.status_code)
        self.assertEqual(Plant.objects.count(), 0)

    def test_create_plant_api_auth(self):    
     
        self.body = {'username':'auser','password':'apassword', 'email':'thisis@an.email'}
        response = self.client.post('/api/auth/users/', self.body, format='json')
        response=self.client.post('/api/auth/token/login/',{'username':'auser','password':'apassword'})
        self.token=response.data["auth_token"]
        self.client.credentials(HTTP_AUTHORIZATION='Token '+self.token)
        
        self.body = {'min_temperature':13,'max_temperature':31, 'water_every_X_days':12,
        'pet_safe':False,'name':'Bromeliad','feed_every_X_months':3,'light':'HIGH',
        'repot_every_X_years':0, 'harvest_every_X_days':0, 'harvest_in_X_days':0,'image':'imageurlhere.jpg'}   
        response = self.client.post('/api/v1/plants/', self.body, format='json')
     
        self.assertEqual(403, response.status_code)
        self.assertEqual(Plant.objects.count(), 0) 



class CaledarTestCase(APITestCase):
    
    def setUp(self):
        plant = Plant.objects.create(min_temperature=13,max_temperature=31, 
        water_every_X_days=12, pet_safe=False,name='Bromeliad',
        feed_every_X_months=3)
        plant.save()
        self.body = {'username':'auser','password':'apassword', 'email':'thisis@an.email'}
        response = self.client.post('/api/auth/users/', self.body, format='json')
        response=self.client.post('/api/auth/token/login/',{'username':'auser','password':'apassword'})
        self.token=response.data["auth_token"]
        self.client.credentials(HTTP_AUTHORIZATION='Token '+self.token)


    def test_calendar_api_auth(self):
        self.body = {'plant_id':1}
        response = self.client.post('/api/v1/plantCalendar/',self.body,format='json')
        self.assertEqual(201, response.status_code)
        self.assertEqual(Calendar.objects.count(), 1) 
        response = self.client.get('/api/v1/plantCalendar/', format='json')
        self.assertEqual(200, response.status_code)
        response = self.client.get('/api/v1/plantCalendar/1', format='json')
        self.assertEqual(200, response.status_code)
        response = self.client.put('/api/v1/plantCalendar/1', data={'status':'OUTSIDE'},format='json')
        self.assertEqual(200, response.status_code)
        response = self.client.delete('/api/v1/plantCalendar/1', format='json')
        self.assertEqual(204, response.status_code)
        self.assertEqual(Calendar.objects.count(), 0) 

class EventTestCase(APITestCase):
    
    def setUp(self):
        plant = Plant.objects.create(min_temperature=23,max_temperature=31, 
        water_every_X_days=12, pet_safe=False,name='Spider Plant',
        feed_every_X_months=3)
        plant.save()
        self.body = {'username':'auser','password':'apassword', 'email':'thisis@an.email'}
        response = self.client.post('/api/auth/users/', self.body, format='json')
        response=self.client.post('/api/auth/token/login/',{'username':'auser','password':'apassword'})
        self.token=response.data["auth_token"]
        self.client.credentials(HTTP_AUTHORIZATION='Token '+self.token)
        self.body = {'plant_id':2}
        response = self.client.post('/api/v1/plantCalendar/',self.body,format='json')
      

    def test_event_api_auth(self):
        self.body = {'status':'WATER', 'day':date.today().isoformat()}
        response = self.client.post('/api/v1/plantCalendar/2/events/',self.body,format='json')
        self.assertEqual(201, response.status_code)
        self.assertEqual(Event.objects.count(), 1) 
        response = self.client.get('/api/v1/plantCalendar/2/events/',format='json')
        self.assertEqual(200, response.status_code)
        response = self.client.get('/api/v1/plantCalendar/2/events/1/',format='json')
        self.assertEqual(200, response.status_code)
        response = self.client.delete('/api/v1/plantCalendar/2/events/1/',format='json')
        self.assertEqual(204, response.status_code)


class PostTestCase(APITestCase):
    
    def setUp(self):
        self.body = {'username':'auser','password':'apassword', 'email':'thisis@an.email'}
        response = self.client.post('/api/auth/users/', self.body, format='json')
        response=self.client.post('/api/auth/token/login/',{'username':'auser','password':'apassword'})
        self.token=response.data["auth_token"]
        self.client.credentials(HTTP_AUTHORIZATION='Token '+self.token)
        
        


    def comunnity_test(self):
        self.body = {'name':'Categ #1'}
        response = self.client.post('/api/v1/categories/',self.body,format='json')
        self.assertEqual(403, response.status_code)
        category = Category.objects.create(name='Categ #1')
        self.assertEqual(Category.objects.count(), 1) 
        self.body= {'title':'My Snake Plant is wilting!!','content':'Leaves are all yellow :('}
        response = self.client.post('/api/v1/categories/'+str(category["id"])+'/threads/',self.body,format='json')
        self.assertEqual(201, response.status_code)

        self.body= {'content':'Pls help :('}
        response = self.client.post('/api/v1/categories/'+str(category["id"])+'/threads/1/posts/',self.body,format='json')
        self.assertEqual(201, response.status_code)