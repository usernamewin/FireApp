from django.shortcuts import render
from django.views.generic.list import ListView
from fire.models import Locations, Incident, FireStation


class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"

def map_station(request):
    fireStations = FireStation.objects.values('name', 'latitude', 'longitude')

    for fs in fireStations:
        fs['latitude'] = float(fs['latitude'])
        fs['longitude'] = float(fs['longitude'])
        
    fireStations_list = list(fireStations)

    context = {
    'fireStations': fireStations_list,
    }

    return render(request, 'map_station.html', context)

def map_incident(request):
    incidents = Incident.objects.select_related('location').all()
    incident_data = []
    cities = set()
    
    for incident in incidents:
        incident_data.append({
            'id': incident.id,
            'description': incident.description,
            'severity_level': incident.severity_level,
            'date_time': incident.date_time.strftime('%Y-%m-%d %H:%M:%S') if incident.date_time else '',
            'latitude': float(incident.location.latitude),
            'longitude': float(incident.location.longitude),
            'address': incident.location.address,
            'city': incident.location.city,
        })
        cities.add(incident.location.city)

    return render(request, 'map_incident.html', {'incidentData': incident_data, 'cities': list(cities)})

class ChartView(ListView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        pass