import os
import sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from docxtpl import DocxTemplate
from app import create_app
from app.slots.models import (
    Student, 
    StudentEnrollment, 
    Slot, 
    OrganizationInfo, 
    TimePeriod, 
    DetailedTimePeriod,
    DepartementDayActivity,
    Department
)
import tempfile
import subprocess
from PyPDF2 import PdfMerger


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


def convert_to_pdf(input_docx, output_pdf):
    """
    Convert a .docx file to a PDF using LibreOffice.
    Args:
        input_docx: Path to the input .docx file
        output_pdf: Path to the output PDF file
    """
    # Use LibreOffice in headless mode to convert the document
    subprocess.run([
        'soffice',
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', os.path.dirname(output_pdf),
        input_docx
    ], check=True)
    
    # LibreOffice creates the PDF with the same name as input but .pdf extension
    # Rename it to the desired output path if needed
    generated_pdf = os.path.join(
        os.path.dirname(output_pdf),
        os.path.splitext(os.path.basename(input_docx))[0] + '.pdf'
    )
    if generated_pdf != output_pdf:
        os.rename(generated_pdf, output_pdf)

def generate_letter_as_pdf(student, slot, template_path, output_pdf_path):
    """
    Generate a PDF letter for a student using the template.
    Args:
        student: Student model instance
        slot: Slot model instance
        template_path: Path to the template .docx file
        output_pdf_path: Path where to save the generated PDF
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        doc = DocxTemplate(template_path)
        
        day_en = slot.date.strftime('%A')
        month_en = slot.date.strftime('%B')

        # Create a mapping of Department to DepartementDayActivity
        department_activity = {
            Department.TECH: DepartementDayActivity.TECH,
            Department.CONSTRUCTION: DepartementDayActivity.CONSTRUCTION,
            Department.CHEMISTRY: DepartementDayActivity.CHEMISTRY
        }

        # Create time period mapping
        time_periods = {
            TimePeriod.MORNING: DetailedTimePeriod.MORNING.value,
            TimePeriod.AFTERNOON: DetailedTimePeriod.AFTERNOON.value
        }

        current_time_period = time_periods[slot.time_period]
        start_time, end_time = current_time_period.split('-')

        # Create the context dictionary for template rendering
        context = {
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
            'ATTIVITA_GIORNATA_SETTORE': department_activity[slot.department].value,
            'GIORNO': weekday_map[day_en],
            'DATA': slot.date.strftime('%d/%m/%Y'),
            'ORA_INIZIO': start_time,
            'ORA_FINE': end_time,
            'DATA_ATTUALE': f"{datetime.now().strftime('%d')} {month_map[month_en].lower()} {datetime.now().strftime('%Y')}"
        }
        
        # Render the template with the context
        doc.render(context)
        
        # Save temporary docx
        temp_docx = os.path.join(temp_dir, "temp.docx")
        doc.save(temp_docx)
        
        # Convert to PDF using LibreOffice
        convert_to_pdf(temp_docx, output_pdf_path)

def merge_pdfs(pdf_files, output_path):
    """
    Merge multiple PDF files into a single PDF.
    Args:
        pdf_files: List of paths to PDF files to merge
        output_path: Path where to save the merged PDF
    """
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    merger.write(output_path)
    merger.close()

def generate_letters_for_slot(template_path, output_dir):
    """
    Generate PDF letters for all enrolled students in a slot (not in waiting list)
    and combine them into a single PDF file.
    Args:
        template_path: Path to the template .docx file
        output_dir: Directory where to save the generated PDFs
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get slot and its active enrollments
    slot = Slot.query.first()
    
    enrollments = StudentEnrollment.query.filter_by(
        slot_id=slot.id,
        is_in_waiting_list=False
    ).all()
    
    pdf_files = []  # Store paths of generated PDFs
    
    # Generate PDF for each enrolled student
    for enrollment in enrollments:
        print(f"Generating PDF for {enrollment.student.first_name} {enrollment.student.last_name}")
        student = enrollment.student
        output_pdf_path = os.path.join(
            output_dir,
            f"letter_{slot.id}_{student.id}_{student.last_name}_{student.first_name}.pdf"
        )
        generate_letter_as_pdf(student, slot, template_path, output_pdf_path)
        pdf_files.append(output_pdf_path)
        print(f"Generated PDF letter for {student.first_name} {student.last_name}")
    
    # Combine all PDFs into one file
    if pdf_files:
        combined_pdf_path = os.path.join(output_dir, f"combined_letters_slot_{slot.id}.pdf")
        merge_pdfs(pdf_files, combined_pdf_path)
        print(f"Created combined PDF at {combined_pdf_path}")
        
        # Optionally, remove individual PDFs
        for pdf_file in pdf_files:
            os.remove(pdf_file)
        print("Removed individual PDF files")

if __name__ == '__main__':
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Example usage - replace with actual values
        template_path = "template_conferma.docx"  # Replace with actual template path
        output_dir = "generated_pdfs"  # Replace with desired output directory
        
        try:
            generate_letters_for_slot(template_path, output_dir)
            print(f"Successfully generated PDF letters in {output_dir}")
        except Exception as e:
            print(f"Error generating letters: {str(e)}")