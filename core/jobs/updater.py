from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import expiracion_cobranzas
from datetime import datetime, time

def notificar_cobranzas():
        # Crear un planificador en segundo plano
    job_defaults = {
    'coalesce': False,
    'max_instances': 1
    }
    scheduler = BackgroundScheduler(job_defaults=job_defaults)

        # Programar la tarea para que se ejecute todos los días a las 10:00 AM
    scheduler.add_job(expiracion_cobranzas, 'interval', days=1)

        # Iniciar el planificador en segundo plano
    scheduler.start()
