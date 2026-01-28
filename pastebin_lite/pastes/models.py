"""
Models for the pastes app.
"""
import uuid
from django.db import models
from django.utils import timezone




class Paste(models.Model):
   """
   Model representing a paste with optional expiration by time or view count.
   """
   id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
   content = models.TextField()
   created_at = models.DateTimeField(default=timezone.now)
   expires_at = models.DateTimeField(null=True, blank=True)
   max_views = models.PositiveIntegerField(null=True, blank=True)
   remaining_views = models.PositiveIntegerField(null=True, blank=True)


   class Meta:
       db_table = 'pastes'
       ordering = ['-created_at']


   def __str__(self):
       return str(self.id)


   def is_expired(self, now=None):
       if self.expires_at is None:
           return False
       now = now or timezone.now()
       return now >= self.expires_at


   def has_views_left(self):
       if self.remaining_views is None:
           return True
       return self.remaining_views > 0


   def is_available(self, now=None):
       return not self.is_expired(now) and self.has_views_left()


   def register_view(self):
       if self.remaining_views is not None:
           if self.remaining_views <= 0:
               return
           self.remaining_views -= 1
           self.save(update_fields=["remaining_views"])
  
   def decrement_views(self):
        if self.max_views is None:
            return True

        if self.remaining_views is None or self.remaining_views <= 0:
            return False

        self.remaining_views -= 1
        self.save(update_fields=["remaining_views"])
        return True