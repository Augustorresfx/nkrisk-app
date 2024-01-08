from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import expiracion_cobranzas, eliminar_tokens
from datetime import datetime, time

def configurar_planificador():
    # Crear un planificador en segundo plano
    job_defaults = {
        'coalesce': False,
        'max_instances': 1
    }
    scheduler = BackgroundScheduler(job_defaults=job_defaults)

    # Programar la tarea para notificar cobranzas todos los días a las 10:00 AM
    scheduler.add_job(expiracion_cobranzas, 'interval', days=1, start_date='2023-11-08 10:00:00')

    # Programar la tarea para eliminar tokens almacenados todos los días a la medianoche
    scheduler.add_job(eliminar_tokens, 'cron', hour=0, minute=0)

    # Iniciar el planificador en segundo plano
    scheduler.start()