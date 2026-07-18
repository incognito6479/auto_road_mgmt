"""
management/urls.py

URL patterns for the management app.
All view functions and viewsets are imported from management.views.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from management import views

router = DefaultRouter()
router.register(r"categories", views.CategoryViewSet, basename="category")
router.register(r"users", views.UserViewSet, basename="user")
router.register(r"students", views.StudentViewSet, basename="student")
router.register(r"enrollments", views.EnrollmentViewSet, basename="enrollment")
router.register(r"payments", views.PaymentViewSet, basename="payment")
router.register(r"groups", views.GroupViewSet, basename="group")
router.register(r"learning-places", views.LearningPlaceViewSet, basename="learning-place")

urlpatterns = [
    path("", include(router.urls)),
]
