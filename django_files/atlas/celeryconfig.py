CELERY_IMPORTS = ('atlas.celery_tasks',)

BROKER_URL = "redis://localhost:6379/3"
CELERY_RESULT_BACKEND = "redis://localhost:6379/3"
CELERY_TASK_SERIALIZER = "msgpack"

CELERYD_CONCURRENCY = 3
