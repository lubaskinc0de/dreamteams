from pydantic_extra_types.phone_numbers import PhoneNumber


class RussianPhoneNumber(PhoneNumber):
    """Phone number in russian region."""

    supported_regions = ["ru"]  # noqa: RUF012
