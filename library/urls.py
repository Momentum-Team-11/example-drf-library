"""library URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from api import views as api_views
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

router = DefaultRouter(trailing_slash=False)
router.register("books", api_views.BookViewSet, basename="books")
books_router = NestedSimpleRouter(router, "books", lookup="book")
books_router.register(
    "book_records",
    api_views.BookRecordViewSet,
    basename="book_records",
)
users_router = DefaultRouter()
users_router.register("users", api_views.UserViewSet, basename="users")

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/", include(books_router.urls)),
    path("api/search", api_views.BookTitleSearchView.as_view(), name="title_search"),
    path(
        "api/books/<int:book_pk>/reviews",
        api_views.BookReviewListCreateView.as_view(),
        name="book_reviews",
    ),
    path(
        "api/book-reviews/<int:pk>",
        api_views.BookReviewDetailView.as_view(),
        name="book_review_detail",
    ),
    path("admin/", admin.site.urls),
    path("api/auth/", include(users_router.urls)),
    path("api/auth/", include("djoser.urls.authtoken")),
]
