"""Utility script to seed the Coffee Matcher database with sample data."""

from datetime import datetime, timedelta

from sqlmodel import select

from app.db.session import init_db, session_scope
from app.models.match_request import MatchRequest
from app.models.timeslot import TimeSlot
from app.models.user import User
from app.models.user_preference import UserPreference
from app.models.venue import Venue


USERS = [
    {"name": "Alice Chen", "email": "alice@example.com", "bio": "AI engineer focused on ML infrastructure."},
    {"name": "Ben Liu", "email": "ben@example.com", "bio": "Product manager passionate about user research."},
    {"name": "Carla Wong", "email": "carla@example.com", "bio": "Design lead exploring immersive experiences."},
]

VENUES = [
    {
        "name": "Downtown Roasters",
        "type": "coffee",
        "price_range": "$$",
        "location": "123 Main Street",
        "description": "Calm ambiance with plenty of outlets.",
    },
    {
        "name": "The Night Market",
        "type": "restaurant",
        "price_range": "$$$",
        "location": "88 Sunset Blvd",
        "description": "Modern Asian fusion ideal for evening meetups.",
    },
]

PREFERENCES = [
    {"user_email": "alice@example.com", "preference_type": "interest", "preference_value": "Machine Learning"},
    {"user_email": "ben@example.com", "preference_type": "sport", "preference_value": "Basketball"},
    {"user_email": "carla@example.com", "preference_type": "hobby", "preference_value": "Photography"},
]


def seed() -> None:
    init_db()
    with session_scope() as session:
        has_users = session.exec(select(User)).first()
        if has_users:
            print("Existing data detected; skipping seeding.")
            return

        user_models = []
        for payload in USERS:
            user = User(**payload)
            session.add(user)
            user_models.append(user)
        session.flush()

        base_time = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)
        for user in user_models:
            for day_offset in range(1, 4):
                start = base_time + timedelta(days=day_offset)
                slot = TimeSlot(
                    user_id=user.id,
                    start_time=start,
                    end_time=start + timedelta(hours=2),
                    status="available",
                )
                session.add(slot)

        venue_models = []
        for payload in VENUES:
            venue = Venue(**payload)
            session.add(venue)
            venue_models.append(venue)
        session.flush()

        email_to_user = {user.email: user for user in user_models}
        for payload in PREFERENCES:
            user = email_to_user[payload.pop("user_email")]
            preference = UserPreference(user_id=user.id, **payload)
            session.add(preference)

        requester = email_to_user["alice@example.com"]
        target = email_to_user["ben@example.com"]
        sample_slot = session.exec(
            select(TimeSlot).where(TimeSlot.user_id == target.id)
        ).first()
        if sample_slot:
            match = MatchRequest(
                requester_id=requester.id,
                target_id=target.id,
                time_slot_id=sample_slot.id,
                proposed_time=sample_slot.start_time,
                venue_id=venue_models[0].id,
                message="Would love to chat about ML platforms!",
            )
            session.add(match)

        print("Seed data inserted successfully.")


if __name__ == "__main__":
    seed()
