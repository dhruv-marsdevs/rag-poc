from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa

# Import all models that should be included in create_all
# This ensures they are registered with SQLAlchemy before creating tables
