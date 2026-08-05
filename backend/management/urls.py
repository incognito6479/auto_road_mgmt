"""
management/urls.py

URL patterns for the management app.
All view functions and viewsets are imported from management.views.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from management import views

router = DefaultRouter()
router.register(r"branches", views.BranchViewSet, basename="branch")
router.register(r"categories", views.CategoryViewSet, basename="category")
router.register(r"users", views.UserViewSet, basename="user")
router.register(r"students", views.StudentViewSet, basename="student")
router.register(r"enrollments", views.EnrollmentViewSet, basename="enrollment")
router.register(r"payments", views.PaymentViewSet, basename="payment")
router.register(r"groups", views.GroupViewSet, basename="group")
router.register(r"learning-places", views.LearningPlaceViewSet, basename="learning-place")
router.register(r"agents", views.AgentViewSet, basename="agent")
router.register(r"holidays", views.HolidaysViewSet, basename="holiday")
router.register(r"cars", views.CarViewSet, basename="car")
router.register(r"driving-lessons", views.DrivingLessonsViewSet, basename="driving-lesson")
router.register(r"autodrome-grants", views.AutodromeAccessGrantViewSet, basename="autodrome-grant")
router.register(r"notifications", views.NotificationViewSet, basename="notification")
router.register(r"teacher-reviews", views.TeacherReviewViewSet, basename="teacher-review")
router.register(r"student-certificates", views.StudentCertificateViewSet, basename="student-certificate")
router.register(r"attendance", views.AttendanceViewSet, basename="attendance")

urlpatterns = [
    path("import-excel/", views.import_excel_upload, name="import-excel-upload"),
    path("import-excel/status/<str:task_id>/", views.import_excel_status, name="import-excel-status"),
    path("", include(router.urls)),
]
