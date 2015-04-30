from datetime import timedelta, datetime

from sqlalchemy import or_, case, desc, func
from sqlalchemy.orm import aliased

from radar.users.roles import UNIT_VIEW_PATIENT_ROLES, DISEASE_GROUP_VIEW_PATIENT_ROLES, UNIT_VIEW_DEMOGRAPHICS_ROLES, \
    DISEASE_GROUP_VIEW_DEMOGRAPHICS_ROLES
from radar.database import db
from radar.models import UnitPatient, Unit, DiseaseGroupPatient, DiseaseGroup
from radar.patients.models import Patient
from radar.users.models import UnitUser, DiseaseGroupUser
from radar.ordering import DESCENDING
from radar.sda.models import SDAPatient, SDABundle, SDAPatientNumber, SDAPatientAlias
from radar.services import is_user_in_disease_group

class PatientQueryBuilder():
    def __init__(self, user):
        self.query = Patient.query
        self.user = user

        # True if the query is filtering on demographics
        self.filtering_by_demographics = False

    def first_name(self, first_name):
        self.filtering_by_demographics = True
        self.query = self.query.filter(filter_by_first_name(first_name))
        return self

    def last_name(self, last_name):
        self.filtering_by_demographics = True
        self.query = self.query.filter(filter_by_last_name(last_name))
        return self

    def date_of_birth(self, date_of_birth):
        self.filtering_by_demographics = True
        self.query = self.query.filter(filter_by_date_of_birth(date_of_birth))
        return self

    def gender(self, gender):
        self.filtering_by_demographics = True
        self.query = self.query.filter(filter_by_gender(gender))
        return self

    def patient_number(self, patient_number):
        self.filtering_by_demographics = True
        self.query = self.query.filter(filter_by_patient_number(patient_number))
        return self

    def radar_id(self, radar_id):
        self.query = self.query.filter(filter_by_radar_id(radar_id))
        return self

    def year_of_birth(self, value):
        self.query = self.query.filter(filter_by_year_of_birth(value))
        return self

    def unit(self, unit_id):
        unit = Unit.query.get(unit_id)

        # Unit exists
        if unit is not None:
            self.query = self.query.join(UnitPatient).filter(UnitPatient.unit == unit)

        return self

    def disease_group(self, disease_group_id):
        # Get the disease group with this id
        disease_group = DiseaseGroup.query.get(disease_group_id)

        # Disease group exists
        if disease_group is not None:
            # If the user doesn't belong to the disease group they need unit permissions
            if not is_user_in_disease_group(self.user, disease_group):
                self.filtering_by_demographics = True

            # Filter by disease group
            self.query = self.query.join(DiseaseGroupPatient).filter(DiseaseGroupPatient.disease_group == disease_group)

        return self

    def order_by(self, column, direction):
        self.query = self.query.order_by(*order_patients(self.user, column, direction))

    def build(self):
        query = self.query

        if not self.user.is_admin:
            if self.filtering_by_demographics:
                permission_filter = filter_by_demographics_permissions(self.user)
            else:
                permission_filter = filter_by_view_patient_permissions(self.user)

            # Filter the patients based on the user's permissions and the type of query
            query = query.filter(permission_filter)

        return query

def sda_patient_sub_query(*args):
    patient_alias = aliased(Patient)
    sub_query = db.session.query(SDAPatient)\
        .join(SDABundle)\
        .join(patient_alias)\
        .filter(Patient.id == patient_alias.id)\
        .filter(*args)\
        .exists()
    return sub_query

def sda_patient_name_sub_query(*args):
    patient_alias = aliased(Patient)
    sub_query = db.session.query(SDAPatientAlias)\
        .join(SDAPatient)\
        .join(SDABundle)\
        .join(patient_alias)\
        .filter(Patient.id == patient_alias.id)\
        .filter(*args)\
        .exists()
    return sub_query

def sda_patient_number_sub_query(*args):
    patient_alias = aliased(Patient)
    sub_query = db.session.query(SDAPatientNumber)\
        .join(SDAPatient)\
        .join(SDABundle)\
        .join(patient_alias)\
        .filter(Patient.id == patient_alias.id)\
        .filter(*args)\
        .exists()
    return sub_query

def filter_by_first_name(first_name):
    first_name_like = first_name + '%'

    patient_filter = sda_patient_sub_query(SDAPatient.first_name.ilike(first_name_like))
    alias_filter = sda_patient_name_sub_query(SDAPatientAlias.first_name.ilike(first_name_like))

    return or_(patient_filter, alias_filter)

def filter_by_last_name(last_name):
    last_name_like = last_name + '%'

    patient_filter = sda_patient_sub_query(SDAPatient.last_name.ilike(last_name_like))
    alias_filter = sda_patient_name_sub_query(SDAPatientAlias.last_name.ilike(last_name_like))

    return or_(patient_filter, alias_filter)

def filter_by_date_of_birth(date_of_birth):
    return sda_patient_sub_query(
        SDAPatient.date_of_birth >= date_of_birth,
        SDAPatient.date_of_birth < date_of_birth + timedelta(days=1)
    )

def filter_by_patient_number(number):
    # One of the patient's identifiers matches
    number_like = number + '%'
    number_filter = sda_patient_number_sub_query(SDAPatientNumber.data['number'].astext.like(number_like))

    # RaDaR ID matches
    radar_id_filter = filter_by_radar_id(number)

    return or_(number_filter, radar_id_filter)

def filter_by_radar_id(radar_id):
    return Patient.id == radar_id

def filter_by_gender(gender_code):
    return sda_patient_sub_query(SDAPatient.data[('gender', 'code')].astext == gender_code)

def filter_by_year_of_birth(year):
    return sda_patient_sub_query(
        SDAPatient.date_of_birth >= datetime(year, 1, 1),
        SDAPatient.date_of_birth < datetime(year + 1, 1, 1)
    )

def filter_by_unit_roles(user, roles):
    patient_alias = aliased(Patient)
    sub_query = db.session.query(patient_alias)\
        .join(patient_alias.units)\
        .join(UnitPatient.unit)\
        .join(Unit.users)\
        .filter(
            UnitUser.user_id == user.id,
            patient_alias.id == Patient.id,
            UnitUser.role.in_(roles)
        )\
        .exists()
    return sub_query

def filter_by_disease_group_roles(user, roles):
    patient_alias = aliased(Patient)
    sub_query = db.session.query(patient_alias)\
        .join(patient_alias.disease_groups)\
        .join(DiseaseGroupPatient.disease_group)\
        .join(DiseaseGroup.users)\
        .filter(
            DiseaseGroupUser.user_id == user.id,
            patient_alias.id == Patient.id,
            DiseaseGroupUser.role.in_(roles)
        )\
        .exists()
    return sub_query

def filter_by_view_patient_permissions(user):
    return or_(
        filter_by_unit_roles(user, UNIT_VIEW_PATIENT_ROLES),
        filter_by_disease_group_roles(user, DISEASE_GROUP_VIEW_PATIENT_ROLES),
    )

def filter_by_demographics_permissions(user):
    return or_(
        filter_by_unit_roles(user, UNIT_VIEW_DEMOGRAPHICS_ROLES),
        filter_by_disease_group_roles(user, DISEASE_GROUP_VIEW_DEMOGRAPHICS_ROLES),
    )

def order_by_demographics_field(user, field, direction, else_=None):
    if user.is_admin:
        expression = field
    else:
        demographics_permission_sub_query = filter_by_demographics_permissions(user)
        expression = case([(demographics_permission_sub_query, field)], else_=else_)

    if direction == DESCENDING:
        expression = desc(expression)

    return expression

def order_by_field(field, direction):
    if direction == DESCENDING:
        field = desc(field)

    return field

def order_by_radar_id(direction):
    return order_by_field(Patient.id, direction)

def order_by_first_name(user, direction):
    return order_by_demographics_field(user, Patient.first_name, direction)

def order_by_last_name(user, direction):
    return order_by_demographics_field(user, Patient.last_name, direction)

def order_by_gender(direction):
    return order_by_field(Patient.gender, direction)

def order_by_date_of_birth(user, direction):
    date_of_birth_order = order_by_demographics_field(user, Patient.date_of_birth, direction)

    if user.is_admin:
        return [date_of_birth_order]
    else:
        # Users without demographics permissions can only see the year
        year_order = order_by_field(func.substr(Patient.date_of_birth, 1, 4), direction)

        # Anonymised (year) values first (i.e. treat 1999 as 1999-01-01)
        anonymised_order = order_by_demographics_field(user, 1, direction, else_=0)

        return [year_order, anonymised_order, date_of_birth_order]

def order_patients(user, order_by, direction):
    if order_by == 'first_name':
        clauses = [order_by_first_name(user, direction)]
    elif order_by == 'last_name':
        clauses = [order_by_last_name(user, direction)]
    elif order_by == 'gender':
        clauses = [order_by_gender(direction)]
    elif order_by == 'date_of_birth':
        clauses = order_by_date_of_birth(user, direction)
    else:
        return [order_by_radar_id(direction)]

    # Decide ties using RaDaR ID
    clauses.append(order_by_radar_id(True))

    return clauses