import random
from datetime import date, timedelta
from radar.lib.database import db
from radar.models.facilities import Facility
from radar.models.patients import Patient, PatientDemographics
from radar.models.units import Unit
from radar.models.users import User

FEMALE = 'F'
MALE = 'M'

FIRST_NAMES = {
    MALE: [
        'JACK',
        'JOSHUA',
        'THOMAS',
        'JAMES',
        'OLIVER',
        'DANIEL',
        'SAMUEL',
        'WILLIAM',
        'HARRY',
        'JOSEPH',
        'BENJAMIN',
        'CHARLIE',
        'LUKE',
        'CALLUM',
        'MATTHEW',
        'JAKE',
        'GEORGE',
        'ETHAN',
        'LEWIS',
        'MOHAMMED',
        'JACOB',
        'ALEXANDER',
        'ALFIE',
        'DYLAN',
        'RYAN',
    ],
    FEMALE: [
        'JESSICA',
        'EMILY',
        'SOPHIE',
        'OLIVIA',
        'ELLIE',
        'CHLOE',
        'GRACE',
        'LUCY',
        'CHARLOTTE',
        'ELLA',
        'KATIE',
        'RUBY',
        'MEGAN',
        'HANNAH',
        'AMELIA',
        'LILY',
        'AMY',
        'MIA',
        'HOLLY',
        'ABIGAIL',
        'MILLIE',
        'MOLLY',
        'EMMA',
        'ISABELLA',
        'LEAH',
    ]
}

LAST_NAMES = [
    'SMITH',
    'JONES',
    'TAYLOR',
    'WILLIAMS',
    'BROWN',
    'DAVIES',
    'EVANS',
    'WILSON',
    'THOMAS',
    'ROBERTS',
    'JOHNSON',
    'LEWIS',
    'WALKER',
    'ROBINSON',
    'WOOD',
    'THOMPSON',
    'WHITE',
    'WATSON',
    'JACKSON',
    'WRIGHT',
    'GREEN',
    'HARRIS',
    'COOPER',
    'KING',
    'LEE',
]


def generate_gender():
    if random.random() > 0.5:
        return MALE
    else:
        return FEMALE


def generate_first_name(gender):
    return random.choice(FIRST_NAMES[gender])


def generate_last_name():
    return random.choice(LAST_NAMES)


def generate_date_of_birth():
    return random_date(date(1920, 1, 1), date(2000, 12, 31))


def generate_date_of_death():
    return random_date(date(1980, 1, 1), date(2014, 12, 31))


def random_date(start_date, end_date):
    days = (end_date - start_date).days
    random_date = start_date + timedelta(days=random.randint(1, days))
    return random_date


def generate_email_address(first_name, last_name):
    return '%s.%s@example.org' % (first_name.lower(), last_name.lower())


def generate_phone_number():
    return '0%d%s %s' % (
        random.randint(1, 2),
        ''.join(str(random.randint(0, 9)) for _ in range(3)),
        ''.join(str(random.randint(0, 9)) for _ in range(6)),
    )


def generate_mobile_number():
    return '07' + ''.join(str(random.randint(0, 9)) for _ in range(9))


def generate_nhs_no():
    while True:
        number = "".join(str(random.randint(0, 9)) for _ in range(9))

        check_digit = 0

        for i in range(9):
            check_digit += int(number[i]) * (10 - i)

        check_digit = 11 - (check_digit % 11)

        if check_digit == 11:
            check_digit = 0
        elif check_digit == 10:
            continue

        number += str(check_digit)

        return int(number)


def generate_chi_no():
    return generate_nhs_no()


def create_fixtures():
    admin = User(username='admin', email='admin@example.org', is_admin=True)
    admin.set_password('password')
    db.session.add(admin)

    # http://en.wikipedia.org/wiki/List_of_fictional_institutions#Hospitals
    units = [
        Unit(
            name='All Saints Hospital',
            facility=Facility(code='A', name='All Saints Hospital'),
        ),
        Unit(
            name='Chelsea General Hospital',
            facility=Facility(code='B', name='Chelsea General Hospital'),
        ),
        Unit(
            name='Chicago Hope',
            facility=Facility(code='C', name='Chicago Hope'),
        ),
        Unit(
            name='County General Hospital',
            facility=Facility(code='D', name='County General Hospital'),
        ),
        Unit(
            name='Community General Hospital',
            facility=Facility(code='E', name='Community General Hospital'),
        ),
    ]

    for unit in units:
        db.session.add(unit)

    for _ in range(1000):
        patient = Patient()

        unit = random.choice(units)
        facility = unit.facility

        gender = generate_gender()
        d = PatientDemographics()
        d.patient = patient
        d.facility = facility
        d.first_name = generate_first_name(gender)
        d.last_name = generate_last_name()
        d.gender = gender
        d.date_of_birth = generate_date_of_birth()

        # 10% chance of being dead :(
        if random.random() < 0.1:
            d.date_of_death = generate_date_of_death()

        d.home_number = generate_phone_number()
        d.mobile_number = generate_mobile_number()
        d.work_number = generate_phone_number()
        d.email_address = generate_email_address(d.first_name, d.last_name)

        r = random.random()

        if r > 0.9:
            d.nhs_no = generate_nhs_no()
            d.chi_no = generate_chi_no()
        elif r > 0.8:
            d.chi_no = generate_chi_no()
        elif r > 0.1:
            d.nhs_no = generate_nhs_no()

        db.session.add(patient)