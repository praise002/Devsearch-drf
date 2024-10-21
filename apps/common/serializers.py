import datetime
from rest_framework import serializers

from apps.common.models import Book, Publisher

# class BookSerializer(serializers.Serializer):
#     title = serializers.CharField(max_length=200)
#     author = serializers.CharField(max_length=200)
#     pages = serializers.IntegerField()
    
# data = {'title': 'Django for APIs', 'author': 'William Vincent', 'pages': 200}
# serializer = BookSerializer(data=data)
# if serializer.is_valid():
#     print(serializer.data)

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'address']
        
class BookSerializer(serializers.ModelSerializer):
    is_long_book = serializers.SerializerMethodField()
    publisher = PublisherSerializer()
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'publisher', 'pages', 'published_date', 'language', 'is_long_book']
        # read_only_fields = ['id', 'is_long_book']
    
    def get_is_long_book(self, obj):
        return obj.pages > 300
    
    def validate_pages(self, value):
        if value <= 0:
            raise serializers.ValidationError('Page count must be greater than 0.')
        return value
    
    def validate_published_date(self, value):
        if value > datetime.date.today():
            raise serializers.ValidationError('Published date cannot be in the future.')
        return value
    
    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError('Title must be at least 5 characters long.')
        return value
    
    def create(self, validated_data):
        publisher_data = validated_data.pop('publisher')
        publisher_name = publisher_data.get('name')
        # publisher, created = Publisher.objects.get_or_create(**publisher_data)
        
        publisher, created = Publisher.objects.get_or_create(
        name__iexact=publisher_name,
            defaults={'name': publisher_name, 
                      'address': publisher_data.get('address')}
        )
        
        book = Book.objects.create(publisher=publisher, **validated_data)
        return book