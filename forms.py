from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileRequired, FileAllowed
class PatientForm(FlaskForm):
    patient_name = StringField('Patient Name', validators=[Optional()])
    csv_file = FileField('CSV File', validators=[Optional(), FileAllowed(['csv'], 'CSV files only!')])
    ctp_file = FileField('CTP File', validators=[Optional(), FileAllowed(['dicom', 'nifti', 'tiff', 'nii', 'nii.gz'], 'Image files only!')])
    mri_file = FileField('MRI File', validators=[Optional(), FileAllowed(['dicom', 'nifti', 'tiff', 'nii', 'nii.gz'], 'Image files only!')])
    mtt_file = FileField('MTT File', validators=[Optional(), FileAllowed(['dicom', 'nifti', 'tiff', 'nii', 'nii.gz'], 'Image files only!')])
    cbv_file = FileField('CBV File', validators=[Optional(), FileAllowed(['dicom', 'nifti', 'tiff', 'nii', 'nii.gz'], 'Image files only!')])
    cbf_file = FileField('CBF File', validators=[Optional(), FileAllowed(['dicom', 'nifti', 'tiff', 'nii', 'nii.gz'], 'Image files only!')])
    tmax_file = FileField('TMAX File', validators=[Optional(), FileAllowed(['dicom', 'nifti', 'tiff', 'nii', 'nii.gz'], 'Image files only!')])
    ground_truth_file = FileField('Ground Truth File', validators=[Optional(), FileAllowed(['dicom', 'nifti', 'tiff', 'nii', 'nii.gz'], 'Image files only!')])
    submit = SubmitField('Add Patient Data')