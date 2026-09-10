from datetime import datetime

def validate_sa_id(id_num: str) -> dict:

    # length and number check
    if not (isinstance(id_num, str) and len(id_num) == 13 and id_num.isdigit()):
        raise ValueError("ID number needs to be 13 digits long")

    id_num = id_num.strip(" ", "")
    
    # date verification oldest year to accept will be 1926 100 year window 
    yy, mm, dd = int(id_num[:2]), int(id_num[2:4]), int(id_num[4:6])

    current_year = datetime.today().year % 100
    century = 1900 if yy > current_year else 2000

    try:
        birth_date = datetime(year=century + yy, month=mm, day=dd)
    except ValueError:
        raise ValueError("ID number contains an invalid date of birth")

    if birth_date > datetime.now():
            raise ValueError("ID contains a future birthday")

    # citezenship
    if id_num[10] not in ('0', '1'):
        raise ValueError("ID contains an invalid citizenship digit.")

    # Luhn checksum
    total = 0
    for idx, char in enumerate(id_num):
        digit = int(char)
        # double every second digit from left 
        if idx % 2 != 0:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit

    if total % 10 != 0:
        raise ValueError("ID number is not valid. Please check and try again")

    return {
        "id_number": id_num,
        "date_of_birth": birth_date,
        "gender": "F" if int(id_num[6:10]) < 5000 else "M",
        "citizenship": "citizen" if id_num[10] == "0" else "permanent_resident",
    }


def is_valid_id(id_num: str) -> bool:
    try:
        validate_sa_id(id_num)
        return True
    except ValueError:
        False
