from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from checklist.views import CheckListViewSet, IdeaViewSet
from file.views import FileViewSet
from note.views import IdeaOfTheDayViewSet, NoteViewSet, TagViewSet

router = DefaultRouter()
router.register(r"notes", NoteViewSet)
router.register(r"tags", TagViewSet)
router.register(r"ideas/today", IdeaOfTheDayViewSet, basename="idea-of-the-day")
router.register(r"checklist/ideas", IdeaViewSet, basename="checklist-ideas")
router.register(r"checklists", CheckListViewSet, basename="checklists")
router.register(r"files", FileViewSet, basename="files")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
