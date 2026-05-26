from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import uuid

from checklist.views import CheckListViewSet, IdeaViewSet
from file.views import FileViewSet
from note.views import IdeaOfTheDayViewSet, NoteViewSet, TagViewSet


@csrf_exempt
def create_session(request):
    """Создает уникальный идентификатор пользователя"""
    if request.method == 'POST':
        user_id = str(uuid.uuid4())
        return JsonResponse({
            'user_id': user_id,
            'message': 'Session created successfully'
        })
    return JsonResponse({'error': 'POST required'}, status=405)


router = DefaultRouter()
router.register(r"notes", NoteViewSet, basename="note")
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"ideas", IdeaOfTheDayViewSet, basename="idea-of-the-day")
router.register(r"checklist/ideas", IdeaViewSet, basename="checklist-ideas")
router.register(r"checklists", CheckListViewSet, basename="checklist")
router.register(r"files", FileViewSet, basename="files")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/", include('apps.users.urls')), 
    path("api/create-session/", create_session, name="create-session"),
]

# Статические файлы в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # В продакшне отдавать через nginx или whitenoise
    pass

# ВАЖНО: Должен быть ПОСЛЕДНИМ — отдает index.html для всех SPA-маршрутов
# Исключаем: api/, admin/, static/
urlpatterns += [
    re_path(r'^(?!api/|admin/|static/).*$', TemplateView.as_view(template_name="index.html")),
]