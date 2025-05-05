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

    path('firestation_list/', a.FireStationList.as_view(), name='firestation-list'),
    path('firestation_list/add/', a.FireStationCreateView.as_view(), name='firestation-add'),
    path('firestation_list/<pk>', a.FireStationUpdateView.as_view(), name='firestation-update'),
    path('firestation_list/<pk>/delete', a.FireStationDeleteView.as_view(), name='firestation-delete'),

    path('firefighter_list/', a.FirefighterList.as_view(), name='firefighter-list'),
    path('firefighter_list/add/', a.FirefighterCreateView.as_view(), name='firefighter-add'),
    path('firefighter_list/<pk>', a.FirefighterUpdateView.as_view(), name='firefighter-update'),
    path('firefighter_list/<pk>/delete', a.FirefighterDeleteView.as_view(), name='firefighter-delete'),

    path('firetruck_list/', a.FireTruckList.as_view(), name='firetruck-list'),
    path('firetruck_list/add/', a.FireTruckCreateView.as_view(), name='firetruck-add'),
    path('firetruck_list/<pk>', a.FireTruckUpdateView.as_view(), name='firetruck-update'),
    path('firetruck_list/<pk>/delete', a.FireTruckDeleteView.as_view(), name='firetruck-delete'),

    path('weather_list/', a.WeatherConditionList.as_view(), name='weather-list'),
    path('weather_list/add/', a.WeatherConditionCreateView.as_view(), name='weather-add'),
    path('weather_list/<pk>', a.WeatherConditionUpdateView.as_view(), name='weather-update'),
    path('weather_list/<pk>/delete', a.WeatherConditionDeleteView.as_view(), name='weather-delete'),
]