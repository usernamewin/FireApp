from django.core.management.base import BaseCommand
from faker import Faker
import random
from fire.models import Locations, Incident, FireStation, Firefighters, FireTruck, WeatherConditions

class Command(BaseCommand):
    help = 'Create initial data for the application'

    def handle(self, *args, **kwargs):
        self.create_locations(10)
        self.create_stations(5)
        self.create_firefighters(20)
        self.create_firetrucks(10)
        self.create_incidents(15)
        self.create_weather()

    def create_locations(self, count):
        fake = Faker()
        for _ in range(count):
            Locations.objects.create(
                name=fake.company(),
                latitude=fake.latitude(),
                longitude=fake.longitude(),
                address=fake.address(),
                city=fake.city(),
                country=fake.country()
            )
        self.stdout.write(self.style.SUCCESS('Initial data for locations created successfully.'))

    def create_stations(self, count):
        fake = Faker()
        for _ in range(count):
            FireStation.objects.create(
                name=f"{fake.city()} Fire Station",
                latitude=fake.latitude(),
                longitude=fake.longitude(),
                address=fake.address(),
                city=fake.city(),
                country=fake.country()
            )
        self.stdout.write(self.style.SUCCESS('Initial data for fire stations created successfully.'))

    def create_firefighters(self, count):
        fake = Faker()
        xp_levels = [
            'Probationary Firefighter', 'Firefighter I', 'Firefighter II',
            'Firefighter III', 'Driver', 'Captain', 'Battalion Chief'
        ]
        for _ in range(count):
            Firefighters.objects.create(
                name=fake.name(),
                rank=random.choice(xp_levels),
                experience_level=random.choice(['Beginner', 'Intermediate', 'Advanced']),
                station=FireStation.objects.order_by('?').first()
            )
        self.stdout.write(self.style.SUCCESS('Initial data for firefighters created successfully.'))

    def create_firetrucks(self, count):
        fake = Faker()
        for _ in range(count):
            FireTruck.objects.create(
                truck_number=f"TRK-{fake.unique.random_number(digits=4)}",
                model=fake.word().title(),
                capacity=f"{random.randint(1000, 5000)}L",
                station=FireStation.objects.order_by('?').first()
            )
        self.stdout.write(self.style.SUCCESS('Initial data for fire trucks created successfully.'))

    def create_incidents(self, count):
        fake = Faker()
        levels = ['Minor Fire', 'Moderate Fire', 'Major Fire']
        for _ in range(count):
            Incident.objects.create(
                location=Locations.objects.order_by('?').first(),
                date_time=fake.date_time_this_year(),
                severity_level=random.choice(levels),
                description=fake.sentence()
            )
        self.stdout.write(self.style.SUCCESS('Initial data for incidents created successfully.'))

    def create_weather(self):
        fake = Faker()
        for incident in Incident.objects.all():
            WeatherConditions.objects.create(
                incident=incident,
                temperature=round(random.uniform(20.0, 45.0), 2),
                humidity=round(random.uniform(30.0, 90.0), 2),
                wind_speed=round(random.uniform(1.0, 15.0), 2),
                weather_description=random.choice([
                    "Clear", "Cloudy", "Rainy", "Windy", "Stormy", "Humid"
                ])
            )
        self.stdout.write(self.style.SUCCESS('Initial data for weather conditions created successfully.'))
