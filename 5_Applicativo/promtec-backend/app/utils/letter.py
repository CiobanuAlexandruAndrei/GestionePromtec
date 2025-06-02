import os
import tempfile
import subprocess
from datetime import datetime
from docxtpl import DocxTemplate
from PyPDF2 import PdfMerger
from io import BytesIO
from ..slots.models import (
    Student,
    Gender,
    StudentEnrollment,
    Slot,
    OrganizationInfo,
    TimePeriod,
    DetailedTimePeriod,
    Department
)

# Language mappings
weekday_map = {
    'Monday': 'Lunedì',
    'Tuesday': 'Martedì',
    'Wednesday': 'Mercoledì',
    'Thursday': 'Giovedì',
    'Friday': 'Venerdì',
    'Saturday': 'Sabato',
    'Sunday': 'Domenica'
}

month_map = {
    'January': 'Gennaio',
    'February': 'Febbraio',
    'March': 'Marzo',
    'April': 'Aprile',
    'May': 'Maggio',
    'June': 'Giugno',
    'July': 'Luglio',
    'August': 'Agosto',
    'September': 'Settembre',
    'October': 'Ottobre',
    'November': 'Novembre',
    'December': 'Dicembre'
}

def convert_to_pdf(input_docx):
    """
    Convert a .docx file to PDF content using LibreOffice.
    Args:
        input_docx: Path to the input .docx file
    Returns:
        bytes: The PDF file content
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Use LibreOffice in headless mode to convert the document
        subprocess.run([
            'soffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', temp_dir,
            input_docx
        ], check=True)
        
        # LibreOffice creates the PDF with the same name as input but .pdf extension
        output_pdf = os.path.join(
            temp_dir,
            os.path.splitext(os.path.basename(input_docx))[0] + '.pdf'
        )
        
        # Read and return the PDF content
        with open(output_pdf, 'rb') as f:
            return f.read()

def generate_letter_as_pdf(student, slot):
    """
    Generate a PDF letter for a student using the template.
    Args:
        student: Student model instance
        slot: Slot model instance
    Returns:
        bytes: The PDF file content
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Map departments to their template files
        department_template_map = {
            Department.TECH: 'template_conferma_TEC.docx',
            Department.CONSTRUCTION: 'template_conferma_DIS.docx',
            Department.CHEMISTRY: 'template_conferma_CHI.docx'
        }

        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_file = department_template_map[slot.department]
        template_path = os.path.join(current_dir, template_file)
        doc = DocxTemplate(template_path)
        
        day_en = slot.date.strftime('%A')
        month_en = slot.date.strftime('%B')

        time_periods = {
            TimePeriod.MORNING: DetailedTimePeriod.MORNING.value,
            TimePeriod.AFTERNOON: DetailedTimePeriod.AFTERNOON.value
        }

        current_time_period = time_periods[slot.time_period]
        start_time, end_time = current_time_period.split('-')


        # Create the context dictionary for template rendering
        context = {
            'FORMA': 'Al ragazzo' if student.gender == Gender.BOY else 'Alla ragazza',
            'SEDE_SCUOLA': student.school.name,
            'ORGANIZZATORE': f"{OrganizationInfo.FIRST_NAME.value} {OrganizationInfo.LAST_NAME.value}",
            'NoCo': f"{OrganizationInfo.FIRST_NAME.value[:2].capitalize()}{OrganizationInfo.LAST_NAME.value[:2].capitalize()}",
            'TEL': OrganizationInfo.TELEPHONE.value,
            'EMAIL': OrganizationInfo.EMAIL.value,
            'COGNOME': student.last_name,
            'NOME': student.first_name,
            'INDIRIZZO': student.address,
            'NAP': student.postal_code,
            'LUOGO': student.city,
            'SETTORE': slot.department.value.upper(),
            'GIORNO': weekday_map[day_en],
            'DATA': slot.date.strftime('%d/%m/%Y'),
            'ORA_INIZIO': start_time,
            'ORA_FINE': end_time,
            'DATA_ATTUALE': datetime.now().strftime('%d/%m/%Y')
        }
        
        # Render the template with the context
        doc.render(context)
        
        # Save temporary docx and convert to PDF
        temp_docx = os.path.join(temp_dir, "temp.docx")
        doc.save(temp_docx)
        
        return convert_to_pdf(temp_docx)

def merge_pdfs_in_memory(pdf_contents):
    """
    Merge multiple PDF contents into a single PDF.
    Args:
        pdf_contents: List of PDF contents in bytes
    Returns:
        bytes: The merged PDF content
    """
    merger = PdfMerger()
    for content in pdf_contents:
        merger.append(BytesIO(content))
    
    output = BytesIO()
    merger.write(output)
    merger.close()
    
    output.seek(0)
    return output.read()

def generate_letters_for_slot(slot_id):
    """
    Generate PDF letters for all enrolled students in a slot (not in waiting list)
    and combine them into a single PDF file.
    Args:
        slot_id: ID of the slot to generate letters for
    Returns:
        bytes: The combined PDF content, or None if no letters were generated
    """
    # Get slot and its active enrollments
    slot = Slot.query.get(slot_id)
    if not slot:
        raise ValueError(f"Slot with ID {slot_id} not found")
    
    enrollments = StudentEnrollment.query.filter_by(
        slot_id=slot.id,
        is_in_waiting_list=False
    ).all()
    
    if not enrollments:
        return None
    
    # Generate PDF for each enrolled student
    pdf_contents = []
    for enrollment in enrollments:
        student = enrollment.student
        pdf_content = generate_letter_as_pdf(student, slot)
        pdf_contents.append(pdf_content)
    
    # Combine all PDFs into one file if there are any
    if pdf_contents:
        return merge_pdfs_in_memory(pdf_contents)
    
    return None