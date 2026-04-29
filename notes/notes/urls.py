from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from django.conf import settings
from django.views.static import serve
import os

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

static_root = os.path.join(settings.BASE_DIR, 'static', 'frontend')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': static_root}),
    path("", TemplateView.as_view(template_name="index.html")),
]