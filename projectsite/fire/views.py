from django.shortcuts import render
from django.views.generic.list import ListView
from fire.models import Locations, Incident, FireStation

from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth

from django.db.models import Count
from datetime import datetime

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

def PieCountbySeverity(request):
    query = '''
    SELECT severity_level, COUNT(*) as count
    FROM fire_incident
    GROUP BY severity_level
    '''
    data = {}
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    if rows:
        # Construct the dictionary with severity level as keys and count as values
        data = {severity: count for severity, count in rows}
    else:
        data = {}
    
    return JsonResponse(data)

def LineCountbyMonth(request):

    current_year = datetime.now().year

    result = {month: 0 for month in range(1, 13)}

    incidents_per_month = Incident.objects.filter(date_time__year=current_year) \
        .values_list('date_time', flat=True)
    
    # Counting the number of incidents per month
    for date_time in incidents_per_month:
        month = date_time.month
        result[month] += 1
    
    # If you want to convert month numbers to month names, you can use a dictionary mapping
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    
    result_with_month_names = {
        month_names[int(month)]: count for month, count in result.items()}
    
    return JsonResponse(result_with_month_names)