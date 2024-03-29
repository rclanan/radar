from sqlalchemy import Column, Integer, ForeignKey, Boolean, String
from sqlalchemy.orm import relationship

from radar.lib.database import db
from radar.models.common import MetadataMixin


class SaltWastingClinicalFeatures(db.Model, MetadataMixin):
    __tablename__ = 'salt_wasting_clinical_features'

    id = Column(Integer, primary_key=True)

    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    patient = relationship('Patient')

    normal_pregnancy = Column(Boolean)
    abnormal_pregnancy_text = Column(String)
    neurological_problems = Column(Boolean)
    seizures = Column(Boolean)
    abnormal_gait = Column(Boolean)
    deafness = Column(Boolean)
    other_neurological_problem = Column(Boolean)
    other_neurological_problem_text = Column(String)
    joint_problems = Column(Boolean)
    join_problems_age = Column(Integer)
    x_ray_abnormalities = Column(Boolean)
    chondrocalcinosis = Column(Boolean)
    other_x_ray_abnormality = Column(Boolean)
    other_x_ray_abnormality_text = Column(String)

    def can_view(self, user):
        return self.patient.can_view(user)

    def can_edit(self, user):
        return self.patient.can_edit(user)
