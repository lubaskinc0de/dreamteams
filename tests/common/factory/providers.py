from faker import Faker


def generate_ru_phone_number(faker: Faker) -> str:
    """Generate a Russian-format phone number: +79 followed by 9 digits."""
    return "+79" + faker.numerify("#########")
