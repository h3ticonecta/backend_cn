from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "PlayHub — Super Admin"
admin.site.site_title = "PlayHub Admin"
admin.site.index_title = "Jogos, promoções e conteúdo ao vivo"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("playhub.urls")),
]
