# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base                  # noqa
from app.models.event import Event                  # noqa
from app.models.person import Person                # noqa
from app.models.person_events import PersonEvents   # noqa
