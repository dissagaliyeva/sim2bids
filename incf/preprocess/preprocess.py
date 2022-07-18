import os
from incf.convert import convert

IDS = []
start = 1


# def create_uuid():
#     output = convert.OUTPUT
#
#     if not os.path.exists(output):


def create_uuid():
    global start

    new = f'0{start}' if start < 10 else start
    start += 1
    IDS.append(new)
    return new


# def create_uuid(length=5):
#     """
#     Create unique id of specified length.
#
#     Parameters
#     ----------
#     length : int
#         Length of the alphanumeric identifier (Default value = 5)
#
#     Returns
#     -------
#         A unique identifier that gets checked through the uniqueness verification step.
#     """
#     choices = string.ascii_letters + string.digits
#     return check_uuid(''.join(random.choices(choices, k=length)))
#
#
# def check_uuid(new_id):
#     """
#
#     Parameters
#     ----------
#     new_id :
#         return:
#
#     Returns
#     -------
#
#     """
#     if new_id in IDS:
#         # print('Retrying to create a new UUID')
#         check_uuid(create_uuid())
#
#     IDS.append(new_id)
#     return new_id


