from django.contrib import admin
from django.urls import path

from fire.views import HomePageView, ChartView, PieCountbySeverity
from fire import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('stations', views.map_station, name='map-station'),
    path('incidents', views.map_incident, name='map-incident'),
    path('dashboard_chart', ChartView.as_view(), name='dashboard-chart'),
    path('chart/', PieCountbySeverity, name='chart'),
]