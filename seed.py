from faker import Faker

from app import app
from extensions import db
from models import User, Note

fake = Faker()
Faker.seed(42)

USERS_TO_SEED = 5
NOTES_PER_USER = 3


def seed_data():
    with app.app_context():
        # generate all usernames up front so the random sequence stays the
        # same on every run, even when some users get skipped below
        usernames = [fake.user_name() for _ in range(USERS_TO_SEED)]

        for username in usernames:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"User '{username}' already exists, skipping.")
                continue

            user = User(username=username)
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

            for _ in range(NOTES_PER_USER):
                note = Note(
                    title=fake.sentence(nb_words=4),
                    content=fake.paragraph(nb_sentences=3),
                    user_id=user.id,
                )
                db.session.add(note)

            db.session.commit()
            print(f"Created user '{username}' with {NOTES_PER_USER} notes.")


if __name__ == "__main__":
    seed_data()
