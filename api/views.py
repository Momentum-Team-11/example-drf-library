from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action, permission_classes
from rest_framework.exceptions import PermissionDenied, ParseError
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveDestroyAPIView,
    get_object_or_404,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Book, BookRecord, BookReview
from .serializers import (
    BookSerializer,
    BookDetailSerializer,
    BookRecordSerializer,
    BookReviewSerializer,
)
from .custom_permissions import (
    IsAdminOrReadOnly,
    IsReaderOrReadOnly,
)


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all().order_by("title")
    serializer_class = BookDetailSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ["list"]:
            return BookSerializer
        return super().get_serializer_class()

    @action(detail=False)
    def featured(self, request):
        featured_books = Book.objects.filter(featured=True)
        serializer = self.get_serializer(featured_books, many=True)
        return Response(serializer.data)


class BookRecordViewSet(ModelViewSet):
    queryset = BookRecord.objects.all()
    serializer_class = BookRecordSerializer
    permission_classes = [IsAuthenticated, IsReaderOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(reader=self.request.user, book=self.kwargs["book_pk"])

    def perform_create(self, serializer):
        serializer.save(reader=self.request.user)


class BookReviewListCreateView(ListCreateAPIView):
    serializer_class = BookReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = BookReview.objects.filter(book_id=self.kwargs["book_pk"])
        search_term = self.request.query_params.get("search")
        if search_term is not None:
            queryset = queryset.filter(
                # Note that using this "search" lookup depends on using full-text search in Postgres
                # https://docs.djangoproject.com/en/4.0/ref/contrib/postgres/search/#the-search-lookup
                body__search=self.request.query_params.get("search")
            )

        return queryset

    def perform_create(self, serializer, **kwargs):
        book = get_object_or_404(Book, pk=self.kwargs["book_pk"])
        serializer.save(reviewed_by=self.request.user, book=book)


class BookReviewDetailView(RetrieveDestroyAPIView):
    serializer_class = BookReviewSerializer
    queryset = BookReview.objects.all()


class BookTitleSearchView(ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer

    def get_queryset(self):
        search_term = self.request.query_params.get("title")
        if search_term is not None:
            return self.queryset.filter(title__icontains=search_term)
