from django.core.management.base import BaseCommand
from core.models import Bahia, Servicio


class Command(BaseCommand):
    help = 'Seed initial data: 6 bays (4 car, 2 moto) and 4 services'

    def handle(self, *args, **options):
        # Create bays: 4 for cars (1-4), 2 for motos (5-6)
        bays_data = [
            {'numero': 1, 'tipo': 'Carro'},
            {'numero': 2, 'tipo': 'Carro'},
            {'numero': 3, 'tipo': 'Carro'},
            {'numero': 4, 'tipo': 'Carro'},
            {'numero': 5, 'tipo': 'Moto'},
            {'numero': 6, 'tipo': 'Moto'},
        ]
        for bay in bays_data:
            Bahia.objects.get_or_create(numero=bay['numero'], defaults=bay)
        self.stdout.write(self.style.SUCCESS('6 bahías creadas (4 Carro, 2 Moto)'))

        # Create services
        services_data = [
            {
                'nombre': 'Lavado en Seco',
                'descripcion': 'Limpieza rápida sin agua',
                'duracion_minutos': 15,
                'precio': 15000,
                'icono': 'bi-wind',
            },
            {
                'nombre': 'Lavado Normal',
                'descripcion': 'Lavado completo exterior',
                'duracion_minutos': 30,
                'precio': 25000,
                'icono': 'bi-droplet-fill',
            },
            {
                'nombre': 'Lavado Platinum',
                'descripcion': 'Lavado completo + encerado',
                'duracion_minutos': 45,
                'precio': 45000,
                'icono': 'bi-stars',
            },
            {
                'nombre': 'Lavado Premium',
                'descripcion': 'Lavado completo + interior + detalles',
                'duracion_minutos': 60,
                'precio': 60000,
                'icono': 'bi-star-fill',
            },
        ]
        for svc in services_data:
            Servicio.objects.get_or_create(nombre=svc['nombre'], defaults=svc)
        self.stdout.write(self.style.SUCCESS('4 servicios creados'))
