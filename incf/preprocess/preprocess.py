import random
import string
# import numpy as np

IDS = []


def create_uuid(length=5):
    choices = string.ascii_letters + string.digits
    return check_uuid(''.join(random.choices(choices, k=length)))


def check_uuid(new_id):
    if new_id in IDS:
        print('Retrying to create a new UUID')
        check_uuid(create_uuid())

    IDS.append(new_id)
    return new_id


