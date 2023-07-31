from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    # Both host and topic are foreign keys, because they have a one to many relationship with the room. one host can have many rooms, and one topic can be related to many rooms
    host = models.ForeignKey(User, on_delete= models.SET_NULL, null=True) #if user is deleted, set host to null
    topic = models.ForeignKey(Topic, on_delete= models.SET_NULL, null=True) #if topic is deleted, set topic to null
    participants = models.ManyToManyField(User, related_name='participants', blank=True) #many to many relationship with user, related name is used to access the participants of a room
    name = models.CharField(max_length=200)
    description = models.TextField(null= True, blank=True)
    updated = models.DateTimeField(auto_now=True) #everytime an entry is saved
    created = models.DateTimeField(auto_now_add= True) #when the model "Entry" was created
    
    class Meta:
        ordering = ['-updated', '-created'] # order by updated and created in descending order, so the most recent is at the top (NOTE: MINUS means descending)

    def __str__(self):
        return self.name
    


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete= models.CASCADE) #if room is deleted, delete all messages
    user = models.ForeignKey(User, on_delete= models.CASCADE) #if user is deleted, delete all messages
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True) #everytime an entry is saved
    created = models.DateTimeField(auto_now_add= True) #when the model "Entry" was created

    class Meta:
        ordering = ['-updated', '-created'] # order by updated and created in descending order, so the most recent is at the top (NOTE: MINUS means descending)

    def __str__(self):
        return self.body[:50]
    
