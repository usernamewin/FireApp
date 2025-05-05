from django.contrib import admin
from django.urls import path

from fire import views as a
from fire import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', a.HomePageView.as_view(), name='home'),
    path('stations', views.map_station, name='map-station'),
    path('incidents', views.map_incident, name='map-incident'),

    path('dashboard_chart', a.ChartView.as_view(), name='dashboard-chart'),
    path('chart/', a.PieCountbySeverity, name='chart'),
    path('lineChart/', a.LineCountbyMonth, name='chart'),
    path('multilineChart/', a.MultilineIncidentTop3Country, name='chart'),
    path('multiBarChart/', a.multipleBarbySeverity, name='chart'),

    path('location_list/', a.LocationsList.as_view(), name='location-list'),
    path('location_list/add', a.LocationsCreateView.as_view(), name='location-add'),
    path('location_list/<pk>', a.LocationsUpdateView.as_view(), name='location-update'),
    path('location_list/<pk>/delete', a.LocationsDeleteView.as_view(), name='location-delete'),

    path('incident_list/', a.IncidentList.as_view(), name='incident-list'),
    path('incident_list/add/', a.IncidentCreateView.as_view(), name='incident-add'),
    path('incident_list/<pk>', a.IncidentUpdateView.as_view(), name='incident-update'),
    path('incident_list/<pk>/delete', a.IncidentDeleteView.as_view(), name='incident-delete'),
]