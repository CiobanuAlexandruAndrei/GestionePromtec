"""
Default Schools Data Module.

This module defines the initial set of schools that should be created in the database
when the application is first set up. It provides a function to create these default
schools if they don't already exist in the database.

The list includes schools from across Ticino that may participate in the enrollment program.
"""

# List of default school names to be created in the system
INITIAL_SCHOOLS = [
    "Scuola Arti e Mestieri di Trevano",
    "Scuola media di Acquarossa",
    "Scuola media di Agno",
    "Scuola media di Ambrì",
    "Scuola media di Balerna",
    "Scuola media di Barbengo",
    "Scuola media di Bedigliora",
    "Scuola media di Bellinzona 1",
    "Scuola media di Bellinzona 2",
    "Scuola media di Biasca",
    "Scuola media di Breganzona",
    "Scuola media di Cadenazzo",
    "Scuola media di Camignolo",
    "Scuola media di Canobbio",
    "Scuola media di Caslano",
    "Scuola media di Castione",
    "Scuola media di Cevio",
    "Scuola media di Chiasso",
    "Scuola media di Giornico",
    "Scuola media di Giubiasco",
    "Scuola media di Gordola",
    "Scuola media di Gravesano",
    "Scuola media di Locarno (Via Chiesa)",
    "Scuola media di Locarno (Via Varesi)",
    "Scuola media di Lodrino",
    "Scuola media di Losone",
    "Scuola media di Lugano (Besso)",
    "Scuola media di Lugano Centro",
    "Scuola media di Massagno",
    "Scuola media di Mendrisio",
    "Scuola media di Minusio",
    "Scuola media di Morbio Inferiore",
    "Scuola media di Pregassona",
    "Scuola media di Riva San Vitale",
    "Scuola media di Stabio",
    "Scuola media di Tesserete",
    "Scuola media di Viganello"
]

def create_default_schools(db, School):
    """
    Create default schools in the database if they don't already exist.
    
    This function is called during application initialization to ensure
    that the database contains a base set of schools. It checks if each
    school already exists before creating it to avoid duplicates.
    
    Args:
        db: The SQLAlchemy database instance
        School: The School model class
        
    Returns:
        None: The function prints status messages but does not return a value
    """
    # Iterate through the list of default schools
    for school_name in INITIAL_SCHOOLS:
        # Check if the school already exists before creating it
        if not School.query.get(school_name):
            school = School(name=school_name)
            db.session.add(school)
    try:
        # Commit all the new schools to the database in a single transaction
        db.session.commit()
        print("Default schools created successfully")
    except Exception as e:
        # Roll back the transaction if any error occurs
        db.session.rollback()
        print(f"Error creating default schools: {str(e)}")