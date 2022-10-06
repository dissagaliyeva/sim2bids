IDS = []
start = 1


def create_uuid(numbers=False):
    global start

    if start in IDS:
        start += 1

    IDS.append(start)

    if not numbers:
        new = f'sub-0{start}' if start < 10 else f'sub-{start}'
        return new
    return str(start)


def reset_index():
    global start, IDS
    start = 1
    IDS = []

