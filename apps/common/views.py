from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status, generics
from .models import Book
from .serializers import BookSerializer

@api_view(['GET', 'POST'])
def book_list(request):
    if request.method == 'GET':
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
class BookListAPIView(APIView):
    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = BookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class BookDetailAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # book = get_object_or_404(Book, id=kwargs.get('pk'))
        try:
            book = Book.objects.get(pk=kwargs.get('pk'))
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BookSerializer(book)
        return Response(serializer.data)
    
    # def put(self, request, *args, **kwargs):
    #     try:
    #         book = Book.objects.get(pk=kwargs.get('pk'))
    #     except Book.DoesNotExist:
    #         return Response({'error': 'Book not found'}, 
    #                         status=status.HTTP_404_NOT_FOUND)
        
    #     serializer = BookSerializer(book, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data)
    
    def patch(self, request, *args, **kwargs):
        try:
            book = Book.objects.get(pk=kwargs.get('pk'))
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, 
                            status=status.HTTP_404_NOT_FOUND)
        
        serializer = BookSerializer(book, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def delete(self, request, *args, **kwargs):
        try:
            book = Book.objects.get(pk=kwargs.get('pk'))
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, 
                            status=status.HTTP_404_NOT_FOUND)
            
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class BookListCreateAPIView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer