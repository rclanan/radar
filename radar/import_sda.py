from datetime import datetime
import xml.etree.ElementTree as ET

from radar.database import configure_engine, db_session
from radar.models import Facility, SDAContainer, Patient, SDAPatient, SDAImport, SDAPatientNumber, SDAMedication, \
    SDAPatientAddress, SDAPatientAlias

def set_float(data, key, node):
    if node is not None:
        data[key] = parse_float(node)

def parse_float(node):
    return float(node.text)

def set_text(data, key, node):
    if node is not None:
        data[key] = parse_text(node)

def parse_text(node):
    return node.text

def set_datetime(data, key, node):
    if node is not None:
        data[key] = parse_datetime(node)

def parse_datetime(node):
    return datetime.strptime(node.text, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%dT%H:%M:%SZ")

def set_code_description(data, key, node):
    if node is not None:
        data[key] = parse_code_description(node)

def parse_code_description(node):
    data = dict()
    set_text(data, 'coding_standard', node.find('./CodingStandard'))
    set_text(data, 'code', node.find('./Code'))
    set_text(data, 'description', node.find('./Description'))
    return data

def parse_container(node):
    sda_container = SDAContainer()

    patient_node = node.find('./Patient')

    sda_patient = parse_patient(patient_node)
    sda_container.sda_patient = sda_patient

    for medication_node in node.findall('./Medications/Medication'):
        sda_medication = parse_medication(medication_node)
        sda_container.sda_medications.append(sda_medication)

    return sda_container

def parse_base(node):
    data = dict()
    set_datetime(data, 'entered_on', node.find('./EnteredOn'))
    set_datetime(data, 'updated_on', node.find('./EnteredOn'))
    set_text(data, 'encounter_number', node.find('./EncounterNumber'))
    set_text(data, 'external_id', node.find('./ExternalId'))
    set_datetime(data, 'from_time', node.find('./FromTime'))
    set_datetime(data, 'to_time', node.find('./ToTime'))
    return data

def parse_order(node):
    data = parse_base(node)
    set_text(data, 'placer_id', node.find('./PlacerId'))
    set_text(data, 'filler_id', node.find('./FillerId'))
    set_code_description(data, 'order_item', node.find('./OrderItem'))
    set_code_description(data, 'order_category', node.find('./OrderCategory'))
    set_text(data, 'order_quantity', node.find('./OrderQuantity'))
    set_text(data, 'specimen', node.find('./Specimen'))
    set_datetime(data, 'specimen_collection_time', node.find('./Specimen'))
    set_datetime(data, 'specimen_received_time', node.find('./SpecimenReceivedTime'))
    set_datetime(data, 'reassessmentTime', node.find('./ReassessmentTime'))
    set_code_description(data, 'frequency', node.find('./Frequency'))
    set_code_description(data, 'duration', node.find('./Duration'))
    set_text(data, 'status', node.find('./Status'))
    set_code_description(data, 'priority', node.find('./Priority'))
    set_code_description(data, 'confidentiality_code', node.find('./ConfidentialityCode'))
    set_text(data, 'condition', node.find('./Condition'))
    set_text(data, 'text_instruction', node.find('./TextInstruction'))
    set_text(data, 'order_group', node.find('./OrderGroup'))
    set_text(data, 'comments', node.find('./Comments'))
    set_datetime(data, 'authorization_time', node.find('./AuthorizationTime'))
    set_text(data, 'verified_comments', node.find('./VerifiedComments'))
    set_text(data, 'group_id', node.find('./GroupId'))
    return data

def parse_medication(node):
    sda_medication = SDAMedication()

    data = parse_order(node)

    set_float(data, 'strength_volume', node.find('./StrengthVolume'))
    set_text(data, 'strength_volume_units', node.find('./StrengthVolumeUnits'))
    set_float(data, 'rate_amount', node.find('./RateAmount'))
    set_code_description(data, 'rate_units', node.find('./RateUnits'))
    set_text(data, 'rate_time_unit', node.find('./RateTimeUnit'))
    set_float(data, 'dose_quantity', node.find('./DoseQuantity'))
    set_float(data, 'max_dose_quantity', node.find('./MaxDoseQuantity'))
    set_text(data, 'number_of_refills', node.find('./NumberOfRefills'))
    set_code_description(data, 'dose_uom', node.find('./DoseUoM'))
    set_code_description(data, 'dosage_form', node.find('./DosageForm'))
    set_text(data, 'indication', node.find('./Indication'))
    set_text(data, 'pharmacy_status', node.find('./PharmacyStatus'))
    set_text(data, 'prescription_number', node.find('./PrescriptionNumber'))

    sda_medication.data = data

    return sda_medication

def parse_name(node):
    data = dict()
    set_text(data, 'name_prefix', node.find('./NamePrefix'))
    set_text(data, 'given_name', node.find('./GivenName'))
    set_text(data, 'middle_name', node.find('./MiddleName'))
    set_text(data, 'family_name', node.find('./FamilyName'))
    set_text(data, 'preferred_name', node.find('./PreferredName'))
    return data

def parse_patient_alias(node):
    sda_patient_alias = SDAPatientAlias()
    sda_patient_alias.data = parse_name(node)
    return sda_patient_alias

def parse_patient_address(node):
    sda_patient_address = SDAPatientAddress()

    data = dict()
    set_datetime(data, 'from_time', node.find('./FromTime'))
    set_datetime(data, 'to_time', node.find('./ToTime'))
    set_text(data, 'street', node.find('./Street'))
    set_code_description(data, 'city', node.find('./City'))
    set_code_description(data, 'state', node.find('./State'))
    set_code_description(data, 'zip', node.find('./Zip'))
    set_code_description(data, 'country', node.find('./Country'))

    sda_patient_address.data = data

    return sda_patient_address

def parse_patient(node):
    sda_patient = SDAPatient()
    sda_patient.data = dict()

    name_node = node.find('./Name')

    if name_node is not None:
        sda_patient.data['name'] = parse_name(name_node)

    set_code_description(sda_patient.data, 'gender', node.find('./Gender'))
    set_code_description(sda_patient.data, 'ethnic_group', node.find('./EthnicGroup'))

    set_datetime(sda_patient.data, 'birth_time', node.find('./BirthTime'))
    set_datetime(sda_patient.data, 'death_time', node.find('./DeathTime'))

    for patient_name_node in node.findall('./Aliases/Name'):
        sda_patient_alias = parse_patient_alias(patient_name_node)
        sda_patient.aliases.append(sda_patient_alias)

    for patient_number_node in node.findall('./PatientNumbers/PatientNumber'):
        sda_patient_number = parse_patient_number(patient_number_node)
        sda_patient.numbers.append(sda_patient_number)

    for patient_address_node in node.findall('./Addresses/Address'):
        sda_patient_address = parse_patient_address(patient_address_node)
        sda_patient.addresses.append(sda_patient_address)

    return sda_patient

def parse_patient_number(node):
    sda_patient_number = SDAPatientNumber()

    sda_patient_number.data = dict()
    set_text(sda_patient_number.data, 'number', node.find('Number'))
    set_text(sda_patient_number.data, 'number_type', node.find('NumberType'))

    organization_node = node.find('Organization')

    if organization_node is not None:
        sda_patient_number.data['organization'] = parse_organization(organization_node)

    return sda_patient_number

def parse_organization(node):
    data = dict()
    set_text(data, 'code', node.find('./Code'))
    set_text(data, 'description', node.find('./Description'))
    return data

def import_sda(facility_code, xml_data):
    root = ET.fromstring(xml_data)

    facility = Facility.query.filter(Facility.code == facility_code).first()

    patient_node = root.find('./Patient')

    mpiid_node = patient_node.find('./MPIID')
    mpiid = mpiid_node.text

    print 'MPIID', mpiid

    radar_id = None

    for patient_number_node in patient_node.findall('./PatientNumbers/PatientNumber'):
        organization_code_node = patient_number_node.find('./Organization/Code')

        if organization_code_node is None:
            continue

        organization_code = organization_code_node.text

        if organization_code == 'RADAR':
            radar_id = int(patient_number_node.find('Number').text)
            break

    print "RADAR ID", radar_id

    patient = Patient.query.get(radar_id)

    sda_container = parse_container(root)
    sda_container.patient = patient
    sda_container.facility = facility
    sda_container.mpiid = mpiid

    sda_import = SDAImport.query.filter(SDAImport.facility == facility, SDAImport.patient == patient).first()

    if sda_import is None:
        sda_import = SDAImport()
        sda_import.facility = facility
        sda_import.patient = patient

    sda_import.sda_container = sda_container

    db_session.add(sda_import)
    db_session.commit()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('facility_code')
    parser.add_argument('xml_filename')
    args = parser.parse_args()

    configure_engine('postgresql://postgres:password@localhost:5432/radar')

    facility_code = args.facility_code
    xml_data = open(args.xml_filename, 'rb').read()

    import_sda(facility_code, xml_data)