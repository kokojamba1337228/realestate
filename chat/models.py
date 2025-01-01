from django.db import models
from polls.models import CustomUser  
from properties.models import Property  

class Chat(models.Model):
    participants = models.ManyToManyField(CustomUser)  
    property = models.ForeignKey(Property, related_name='chats', on_delete=models.CASCADE, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"Чат о {self.property.title if self.property else 'a Property'}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE) 
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  
    content = models.TextField() 
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"Сообщение от {self.sender.first_name}: {self.content[:50]}..."  
