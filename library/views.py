from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Book, Borrowing
from .serializers import BookSerializer, BorrowingSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @action(detail=True, methods=['post'])
    def borrow(self, request, pk=None):
        book = self.get_object()
        if not book.available:
            return Response({'error': 'Not available'}, status=400)
        book.available = False
        book.save()
        Borrowing.objects.create(user=request.user, book=book)
        return Response({'status': 'borrowed'})

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        book = self.get_object()
        book.available = True
        book.save()
        Borrowing.objects.filter(book=book, returned=False).update(returned=True)
        return Response({'status': 'returned'})
