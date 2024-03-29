from sqlalchemy import or_
from sqlalchemy.orm import aliased

from radar.lib.database import db
from radar.models.disease_groups import DiseaseGroup, DiseaseGroupUser
from radar.models.units import Unit, UnitUser
from radar.models.users import User
from radar.lib.roles import UNIT_VIEW_USER_ROLES
from radar.lib.roles import DISEASE_GROUP_VIEW_USER_ROLES


class UserQueryBuilder(object):
    def __init__(self, user):
        self.query = User.query
        self.user = user

    def username(self, username):
        self.query = self.query.filter(User.username.ilike(username + '%'))

    def email(self, email):
        self.query = self.query.filter(User.email.ilike(email + '%'))

    def first_name(self, first_name):
        self.query = self.query.filter(User.first_name.ilike(first_name + '%'))

    def last_name(self, last_name):
        self.query = self.query.filter(User.last_name.ilike(last_name + '%'))

    def unit(self, unit_id):
        self.query = self.query\
            .outerjoin(User.unit_users)\
            .filter(or_(User.is_admin, UnitUser.unit_id == unit_id))

    def disease_group(self, disease_group_id):
        self.query = self.query\
            .outerjoin(User.disease_group_users)\
            .filter(or_(User.is_admin, DiseaseGroupUser.disease_group_id == disease_group_id))

    def build(self):
        query = self.query

        # Show all users if the user is an admin or if the user can manage group membership
        if not self.user.is_admin and not self.user.has_edit_user_membership_permission:
            query = query.filter(filter_by_view_user_permissions(self.user))

        return query


def filter_by_view_user_permissions(user):
    return or_(
        filter_by_unit_roles(user, UNIT_VIEW_USER_ROLES),
        filter_by_disease_group_roles(user, DISEASE_GROUP_VIEW_USER_ROLES),
    )


def filter_by_unit_roles(user, roles):
    user_alias = aliased(User)
    unit_user_alias = aliased(UnitUser)

    sub_query = db.session.query(user_alias)\
        .join(unit_user_alias, user_alias.unit_users)\
        .join(unit_user_alias.unit)\
        .join(Unit.users)\
        .filter(
            user_alias.id == User.id,
            UnitUser.user_id == user.id,
            UnitUser.role.in_(roles)
        )\
        .exists()

    return sub_query


def filter_by_disease_group_roles(user, roles):
    user_alias = aliased(User)
    disease_group_user_alias = aliased(DiseaseGroupUser)

    sub_query = db.session.query(user_alias)\
        .join(disease_group_user_alias, user_alias.disease_group_users)\
        .join(disease_group_user_alias.disease_group)\
        .join(DiseaseGroup.users)\
        .filter(
            user_alias.id == User.id,
            DiseaseGroupUser.user_id == user.id,
            DiseaseGroupUser.role.in_(roles)
        )\
        .exists()

    return sub_query
