from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from fire.models import Locations, Incident, FireStation, Firefighters, FireTruck, WeatherConditions, Boat
from fire.forms import LocationsForm, IncidentForm, FireStationForm, FirefighterForm, FireTruckForm, WeatherConditionForm
from django.urls import reverse_lazy

from django.db.models.query import QuerySet
from django.db.models import Q
from django.contrib import messages

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

def MultilineIncidentTop3Country(request):

    query = '''
        SELECT
        fl.country,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM
        fire_incident fi
    JOIN
        fire_locations fl ON fi.location_id = fl.id
    WHERE
        fl.country IN (
            SELECT
                fl_top.country
            FROM
                fire_incident fi_top
            JOIN
                fire_locations fl_top ON fi_top.location_id = fl_top.id
            WHERE
                strftime('%Y', fi_top.date_time) = strftime('%Y', 'now')
            GROUP BY
                fl_top.country
            ORDER BY
                COUNT(fi_top.id) DESC
            LIMIT 3
        )
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now')
    GROUP BY
        fl.country, month
    ORDER BY
        fl.country, month;
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        
    # Initialize a dictionary to store the result
    result = {}

    # Initialize a set of months from January to December
    months = set(str(i).zfill(2) for i in range(1, 13))
        
    # Loop through the query results
    for row in rows:
        country = row[0]
        month = row[1]
        total_incidents = row[2]

        # If the country is not in the result dictionary, initialize it with all months set to zero
        if country not in result:
            result[country] = {month: 0 for month in months}
        
        # Update the incident count for the corresponding month
        result[country][month] = total_incidents
        
    # Ensure there are always 3 countries in the result
    while len(result) < 3:
        # Placeholder name for missing countries
        missing_country = f"Country {len(result) + 1}"
        result[missing_country] = {month: 0 for month in months}
        
    for country in result:
        result[country] = dict(sorted(result[country].items()))
    
    return JsonResponse(result)

def multipleBarbySeverity(request):
    query = '''
    SELECT 
        fi.severity_level,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    GROUP BY fi.severity_level, month
    '''
 
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
 
    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))
 
    for row in rows:
        level = str(row[0])  # Ensure the severity level is a string
        month = row[1]
        total_incidents = row[2]
 
        if level not in result:
            result[level] = {month: 0 for month in months}
 
        result[level][month] = total_incidents
 
    # Sort months within each severity level
    for level in result:
        result[level] = dict(sorted(result[level].items()))

    return JsonResponse(result)

class LocationsList(ListView):
    model = Locations
    context_object_name = 'locations'
    template_name = 'location_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(LocationsList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) |
                        Q(description__icontains=query))
        return qs
    
class LocationsCreateView(CreateView):
    model = Locations
    form_class = LocationsForm
    template_name = 'location_add.html'
    success_url = reverse_lazy('location-list')

    def form_valid(self, form):
        incident_location = form.instance.name
        messages.success(self.request, f'{incident_location} has been successfully added.')

        return super().form_valid(form)

class LocationsUpdateView(UpdateView):
    model = Locations
    form_class = LocationsForm
    template_name = 'location_edit.html'
    success_url = reverse_lazy('location-list')

    def form_valid(self, form):
        incident_location = form.instance.name
        messages.success(self.request, f'{incident_location} has been successfully updated.')

        return super().form_valid(form)

class LocationsDeleteView(DeleteView):
    model = Locations
    template_name = 'location_del.html'
    success_url = reverse_lazy('location-list')

    def form_valid(self, form):
        obj = self.get_object()
        incident_location = obj.name
        messages.success(self.request, f'{incident_location} has been successfully deleted.')

        return super().form_valid(form)

class IncidentList(ListView):
    model = Incident
    context_object_name = 'incident'
    template_name = 'incident_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(IncidentList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) |
                        Q(description__icontains=query))
        return qs
    
class IncidentCreateView(CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'incident_add.html'
    success_url = reverse_lazy('incident-list')

    def form_valid(self, form):
        incident_location = form.instance.location
        messages.success(self.request, f'{incident_location} has been successfully added.')

        return super().form_valid(form)

class IncidentUpdateView(UpdateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'incident_edit.html'
    success_url = reverse_lazy('incident-list')

    def form_valid(self, form):
        incident_location = form.instance.location
        messages.success(self.request, f'{incident_location} has been successfully updated.')

        return super().form_valid(form)

class IncidentDeleteView(DeleteView):
    model = Incident
    template_name = 'incident_del.html'
    success_url = reverse_lazy('incident-list')

    def form_valid(self, form):
        obj = self.get_object()
        incident_location = obj.location
        messages.success(self.request, f'{incident_location} has been successfully deleted.')

        return super().form_valid(form)

class FireStationList(ListView):
    model = FireStation
    context_object_name = 'firestation'
    template_name = 'firestation_list.html'
    paginate_by = 5
 
    def get_queryset(self, *args, **kwargs):
        qs = super(FireStationList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) |
                        Q(description__icontains=query))
        return qs
     
class FireStationCreateView(CreateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'firestation_add.html'
    success_url = reverse_lazy('firestation-list')

    def form_valid(self, form):
        firestation_name = form.instance.name
        messages.success(self.request, f'{firestation_name} has been successfully added.')

        return super().form_valid(form)
 
class FireStationUpdateView(UpdateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'firestation_edit.html'
    success_url = reverse_lazy('firestation-list')

    def form_valid(self, form):
        firestation_name = form.instance.name
        messages.success(self.request, f'{firestation_name} has been successfully updated.')

        return super().form_valid(form)
 
class FireStationDeleteView(DeleteView):
    model = FireStation
    template_name = 'firestation_del.html'
    success_url = reverse_lazy('firestation-list')

    def form_valid(self, form):
        obj = self.get_object()
        firestation_name = obj.name
        messages.success(self.request, f'{firestation_name} has been successfully deleted.')

        return super().form_valid(form)

class FirefighterList(ListView):
    model = Firefighters
    context_object_name = 'firefighter'
    template_name = 'firefighter_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(FirefighterList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) |
                        Q(description__icontains=query))
        return qs
     
class FirefighterCreateView(CreateView):
    model = Firefighters
    form_class = FirefighterForm
    template_name = 'firefighter_add.html'
    success_url = reverse_lazy('firefighter-list')

    def form_valid(self, form):
        firefighters_name = form.instance.name
        messages.success(self.request, f'{firefighters_name} has been successfully added.')

        return super().form_valid(form)

class FirefighterUpdateView(UpdateView):
    model = Firefighters
    form_class = FirefighterForm
    template_name = 'firefighter_edit.html'
    success_url = reverse_lazy('firefighter-list')

    def form_valid(self, form):
        firefighters_name = form.instance.name
        messages.success(self.request, f'{firefighters_name} has been successfully updated.')

        return super().form_valid(form)
 
class FirefighterDeleteView(DeleteView):
    model = Firefighters
    template_name = 'firefighter_del.html'
    success_url = reverse_lazy('firefighter-list')

    def form_valid(self, form):
        obj = self.get_object()
        firefighters_name = obj.name
        messages.success(self.request, f'{firefighters_name} has been successfully deleted.')

        return super().form_valid(form)
 
class FireTruckList(ListView):
    model = FireTruck
    context_object_name = 'firetruck'
    template_name = 'firetruck_list.html'
    paginate_by = 5
 
    def get_queryset(self, *args, **kwargs):
        qs = super(FireTruckList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) |
                        Q(description__icontains=query))
        return qs
     
class FireTruckCreateView(CreateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'firetruck_add.html'
    success_url = reverse_lazy('firetruck-list')

    def form_valid(self, form):
        firetruck_name = form.instance.truck_number
        messages.success(self.request, f'{firetruck_name} has been successfully added.')

        return super().form_valid(form)
 
class FireTruckUpdateView(UpdateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'firetruck_edit.html'
    success_url = reverse_lazy('firetruck-list')

    def form_valid(self, form):
        firetrucks_name = form.instance.truck_number
        messages.success(self.request, f'{firetrucks_name} has been successfully updated.')

        return super().form_valid(form)
 
class FireTruckDeleteView(DeleteView):
    model = FireTruck
    template_name = 'firetruck_del.html'
    success_url = reverse_lazy('firetruck-list')

    def form_valid(self, form):
        obj = self.get_object()
        firetrucks_name = obj.truck_number
        messages.success(self.request, f'{firetrucks_name} has been successfully deleted.')

        return super().form_valid(form)

class WeatherConditionList(ListView):
    model = WeatherConditions
    context_object_name = 'weather'
    template_name = 'weather_list.html'
    paginate_by = 5
 
    def get_queryset(self, *args, **kwargs):
        qs = super(WeatherConditionList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) |
                        Q(description__icontains=query))
        return qs
     
class WeatherConditionCreateView(CreateView):
    model = WeatherConditions
    form_class = WeatherConditionForm
    template_name = 'weather_add.html'
    success_url = reverse_lazy('weather-list')

    def form_valid(self, form):
        weather_temperature = form.instance.temperature 
        messages.success(self.request, f'{weather_temperature} has been successfully added.')

        return super().form_valid(form)
 
class WeatherConditionUpdateView(UpdateView):
    model = WeatherConditions
    form_class = WeatherConditionForm
    template_name = 'weather_edit.html'
    success_url = reverse_lazy('weather-list')

    def form_valid(self, form):
        weather_temperature = form.instance.temperature 
        messages.success(self.request, f'{weather_temperature} has been successfully updated.')

        return super().form_valid(form)
 
class WeatherConditionDeleteView(DeleteView):
    model = WeatherConditions
    template_name = 'weather_del.html'
    success_url = reverse_lazy('weather-list')

    def form_valid(self, form):
        obj = self.get_object()
        weather_temperature = obj.temperature
        messages.success(self.request, f'{weather_temperature} has been successfully deleted.')

        return super().form_valid(form)
    
class BoatCreateView(CreateView):
    model = Boat
    fields = "__all__"
    template_name = "boat_form.html"
    success_url = reverse_lazy('boat-list')

    def post(self, request, *args, **kwargs):
        length = request.POST.get('length')
        width = request.POST.get('width')
        height = request.POST.get('height')

        #Validate dimensions
        errors = []
        for field_name, value in [('length', length), ('width', width), ('height', height)]:
            try:
                if float (value) <= 0:
                    errors.append(f"{field_name.capitalize()} must be greater than 0.")
            except (ValueError, TypeError):
                    errors.append(f" {field_name.capitalize()} must be a valid number.")
                
        # If errors exist, display them and return to the form
        if errors:
            for error in errors:
                messages.error(request, error)
            return self.form_invalid(self.get_form())
        
        # Call the parent's post() if validation passes
        return super().post(request, *args, **kwargs)
    
class BoatUpdateView(UpdateView):
    model = Boat
    fields = "all"
    template_name = "boat_form.html"
    success_url = reverse_lazy('boat-list')

    def post(self, request, *args, **kwargs):
        length = request.POST.get('length')
        width = request.POST.get('width')
        height = request.POST.get('height')

        #Validate dimensions
        errors = []
        for field_name, value in [('length', length), ('width', width), ('height', height)]:
            try:
                if float(value) <= 0:
                    errors.append(f"{field_name.capitalize()} must be greater than 0.")
            except (ValueError, TypeError):
                errors.append(f"{field_name.capitalize()} must be a valid number.")

        # If errors exist, display them and return to the form
        if errors:
            for error in errors:
                messages.error(request, error)
            return self.form_invalid(self.get_form())

        #Call the parent's post() if validation passes
        return super().post(request, *args, **kwargs)