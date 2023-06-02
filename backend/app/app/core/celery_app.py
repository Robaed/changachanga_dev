import sentry_sdk
from celery import Celery, signals
from celery.utils.log import get_logger
from redis import Redis
from sentry_sdk.integrations.celery import CeleryIntegration

from app.core.config import settings

redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=3)
logger = get_logger(__name__)

celery_app = Celery(__name__)

celery_config = settings.celery.dict()
celery_app.conf.update(**celery_config)


@signals.celeryd_init.connect
def init_sentry(**_kwargs):
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            CeleryIntegration(),
        ],

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production,
        traces_sample_rate=1.0,
    )