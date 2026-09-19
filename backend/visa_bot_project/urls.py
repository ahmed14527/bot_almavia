import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve
from django.http import HttpResponse

dist_dir = settings.BASE_DIR / 'frontend' / 'dist'

def serve_spa(request):
    index_file = dist_dir / 'index.html'
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    return HttpResponse("<h1>Italian Embassy Visa Bot API is running.</h1><p>To view the React dashboard, run 'npm run dev' or build the frontend.</p>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('booking.urls')),
]

if (dist_dir / 'assets').exists():
    urlpatterns += [
        re_path(r'^assets/(?P<path>.*)$', serve, {'document_root': str(dist_dir / 'assets')}),
    ]

urlpatterns += [
    path('', serve_spa, name='spa-home'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
