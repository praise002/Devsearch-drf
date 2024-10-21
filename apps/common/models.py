from django.db import models

class Publisher(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name
    
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='books')
    pages = models.IntegerField()
    published_date = models.DateField()
    language = models.CharField(max_length=50)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return self.title

