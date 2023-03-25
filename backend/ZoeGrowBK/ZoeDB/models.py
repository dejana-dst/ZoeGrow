from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField

class Climate(models.Model): 
    """ 
    objectid = models.IntegerField()
    koppengeig = models.IntegerField()
    koppenge_1 = models.IntegerField()
    gridcode_c = models.CharField(max_length=3)
    gridcode_1 = models.CharField(max_length=14)
    gridcode_2 = models.CharField(max_length=11)
    gridcode_3 = models.CharField(max_length=21)
    koppenge_2 = models.IntegerField()
    geom = models.PolygonField(srid=4326)
#ogrinspect mapping

climate_mapping = {
    'objectid': 'OBJECTID',
    'koppengeig': 'KoppenGeig',
    'koppenge_1': 'KoppenGe_1',
    'gridcode_c': 'GRIDCODE_C',
    'gridcode_1': 'GRIDCODE_1',
    'gridcode_2': 'GRIDCODE_2',
    'gridcode_3': 'GRIDCODE_3',
    'koppenge_2': 'KoppenGe_2',
    'geom': 'POLYGON',
} 
"""
    ogc_fid=models.IntegerField( null=True,blank=True)
    gridcode=models.IntegerField( null=True,blank=True)
    climatecode=models.CharField(max_length=10, null=True,blank=True)
    wkb_geometry = models.PolygonField(srid=4326)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.PointField(srid=4326, null=True,blank=True)
    location_zone = models.CharField(max_length=10,null=True,blank=True)
    profile_image = models.ImageField(upload_to='uploads/profile', blank=True)



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    
    instance.profile.save()





class FAQ(models.Model):
    answer=models.TextField()
    question=models.TextField()

class Plant(models.Model):
    HUMIDITY_CHOICES = [
        ('LOW', 'Low humidity'),
        ('MEDIUM', 'Medium humidity'),
        ('HIGH', 'High humidity'),
    ]
    LIGHT_CHOICES = [
        ('LOW', 'Low light'),
        ('MEDIUM', 'Medium light'),
        ('HIGH', 'High light'),
    ]    


    image = models.ImageField(upload_to='uploads/plants',null=True, blank=True)
    min_temperature=models.IntegerField()
    max_temperature=models.IntegerField()
    water_every_X_days=models.IntegerField()
    name=models.CharField(max_length=100)
    pet_safe=models.BooleanField()
    harvest_every_X_days=models.IntegerField(null=True, blank=True)
    repot_every_X_years=models.IntegerField(null=True, blank=True)
    feed_every_X_months=models.IntegerField(null=True, blank=True)
    harvest_in_X_days=models.IntegerField(null=True, blank=True)
    light = models.CharField(
        max_length=6,
        choices=LIGHT_CHOICES,
        default='MEDIUM',
    )
    humidity = models.CharField(
        max_length=6,
        choices=HUMIDITY_CHOICES,
        default='MEDIUM',
    )
    tracked = models.ManyToManyField(
        User,
        through='Calendar',
        through_fields=('plant', 'user'),
    )
    climatezones = ArrayField(models.CharField(max_length=10),null=True, blank=True)
    

    
class Calendar(models.Model):
    STATUS_CHOICES = [
        ('NOT PLANTED', 'Not planted yet'),
        ('OUTSIDE', 'Planted outside'),
        ('INSIDE', 'Planted inside'),
    ] 
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='NOT PLANTED',
    )






class Event(models.Model):
    ACTIVITY_CHOICES = [
        ('WATER', 'Watered the plant'),
        ('GRAFTED', 'Planted from cutting'),
        ('SOW', 'Sowed from seed'),
        ('FEED', 'Fertilized the plant'),
        ('REPOT', 'Plant repotted'),
        ('MOVE', 'Move outside/inside'),
        ('HARVEST', 'Harvested'),
        ('TRANSPLANT', 'Transplanted'),
        ('PRUNE','Prunned'),
        ('OUTSIDE', 'Planted outside'),
        ('INSIDE', 'Planted inside'),
        ('SOW', 'Sowed from seed'),
    ]
    day=models.DateField() #YYYY-MM-DD
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE, blank=True)
    status = models.CharField(
        max_length=30,
        choices=ACTIVITY_CHOICES,
    )


class Category(models.Model):
    name=models.CharField(max_length=200)


class Thread(models.Model):
    title=models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=True, blank=True)
    createdBy= models.ForeignKey(User, on_delete=models.CASCADE)
    created=models.DateTimeField(auto_now_add=True)
    edited=models.DateTimeField(auto_now=True)
    locked=models.BooleanField(default=False)



class Post(models.Model):
    content=models.TextField()
    created=models.DateTimeField(auto_now_add=True)
    edited=models.DateTimeField(auto_now=True)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE,null=True, blank=True)
    parentPost = models.IntegerField(null=True, blank=True)
    postedBy = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)
    likesCount=models.IntegerField(default=0)

""" @receiver(post_save, sender=Thread)
def create_first_post(sender, instance, created, **kwargs):
    if created:
        Post.objects.create(thread=instance)

@receiver(post_save, sender=Thread)
def save_first_post(sender, instance, **kwargs):
    instance.posts.save() """
   
""" class Message(models.Model):
    content=models.TextField()
    created=models.DateTimeField(auto_now_add=True)
    edited=models.DateTimeField(auto_now=True)  
    toUser = models.ForeignKey(User)
    fromUser = models.ForeignKey(User)  """


