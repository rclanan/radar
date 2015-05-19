from flask import Blueprint, render_template
from radar.patients.models import Patient
from radar.patients.views import get_patient_data


bp = Blueprint('pathology', __name__)


@bp.route('/')
def view_pathology_list(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    context = dict(
        patient=patient,
        patient_data=get_patient_data(patient),
    )

    return render_template('patient/pathology.html', **context)