def dept_name(elem):
    """Standardize department names for consistency."""
    dept_mappings = {
        "computer science": [
            "computer science", 
            "khoury college of computer sciences", 
            "khoury", 
            "computer", 
            "phd in computer science"
        ],
        "economics": ["economics", "econ"],
        "english": ["english", "english phd"],
        "marine and environmental sciences": [
            "marine and environmental science", 
            "marine and environmental sciences"
        ],
        "sociology and anthropology": [
            "sociology and anthropology", 
            "sociology"
        ],
        "mechanical and industrial engineering": [
            "mechanical and industrial engineering", 
            "mechanical engineering",
            "industrial engineering", 
            "college of engineering"
        ],
        "psychology": [
            "psychology",
            "counseling psychology",
            "applied psychology"
        ]
    }
    
    elem_lower = elem.lower() if isinstance(elem, str) else elem
    
    for standard_name, variations in dept_mappings.items():
        if elem_lower in variations:
            return standard_name
    
    return elem

benefit_icons = {
    # Financial/Cost Benefits
    'Deductible': '💰',
    'Out-of-Pocket Maximum': '💸',
    
    # Basic Medical Services
    'Preventive Care': '🏥',
    'Primary Care Visit': '👨‍⚕️',
    'Specialist Visit': '👩‍⚕️',
    'Telehealth Services': '💻',
    
    # Emergency Services
    'Emergency Room': '🚑',
    'Emergency Transportation': '🚨',
    'Urgent Care': '🏥',
    
    # Diagnostic Services
    'Diagnostic Tests (X-ray/Blood)': '🩸',
    'Imaging (CT/MRI/PET)': '📷',
    
    # Hospital Services
    'Outpatient Surgery': '🏥',
    'Hospital Admission': '🏨',
    
    # Mental Health
    'Mental Health Outpatient': '🧠',
    'Mental Health Inpatient': '🛏️',
    'Substance Abuse Treatment': '💊',
    
    # Prescriptions
    'Prescription Drugs (Generic)': '💊',
    'Prescription Drugs (Brand)': '💉',
    'Prescription Drugs (Specialty)': '🧪',
    
    # Home/Extended Care
    'Home Health Care': '🏠',
    'Skilled Nursing Facility': '🏢',
    'Hospice Services': '🕊️',
    
    # Therapy Services
    'Rehabilitation Services': '🦽',
    'Rehabilitation (PT/OT/Speech)': '💪',
    'Habilitation Services': '🤸',
    
    # Medical Equipment
    'Durable Medical Equipment': '🦽',
    
    # Maternity/Family
    'Maternity Care': '🤰',
    'Childbirth/Delivery': '👶',
    'Birth Control': '💊',
    'Infertility Treatment': '👨‍👩‍👧',
    
    # Alternative Medicine
    'Acupuncture': '📍',
    'Chiropractic Care': '🦴',
    
    # Vision Services
    'Vision Exam (Adult)': '👁️',
    'Vision Exam (Pediatric)': '👓',
    'Eyeglasses (Adult)': '👓',
    'Eyeglasses (Pediatric)': '🥽',
    'Contact Lenses': '👁️',
    'Vision Additional Benefits': '✨',
    'Vision Services at Fenway Health': '🏥',
    'LASIK/PRK': '👁️‍🗨️',
    
    # Dental Services
    'Dental (Adult)': '🦷',
    'Dental (Pediatric)': '🦷',
    'Dental Services Detail': '📋',
    'Dental Maximum Rollover': '🔄',
    'Dental (Emergency/Medical)': '🦷',
    
    # Specialized Services
    'Hearing Aids': '👂',
    'Gender-Affirming Care': '⚧️',
    'TMJ Treatment': '😬',
    'Immunizations': '💉',
    'Allergy Services': '🤧',
    
    # Other Coverage
    'Bariatric Surgery': '⚖️',
    'Weight Loss Programs': '🏃',
    'Routine Foot Care': '🦶',
    'International Coverage': '🌍'
}

def verify_figure_mappings(pdf_link_mapping, hotspot_dict):
    """
    Verify that all figures in pdf_link_mapping have corresponding hotspots
    and all hotspots have corresponding figures.
    
    Parameters:
    -----------
    pdf_link_mapping : dict
        Dictionary mapping hotspot IDs to figure objects
    hotspot_dict : dict
        Dictionary mapping page indices to lists of hotspot coordinates
    
    Raises:
    -------
    ValueError
        If there are missing mappings or orphaned hotspots
    """
    # Extract all hotspot IDs from hotspot_dict
    all_hotspot_ids = set()
    for page_index, hotspots in hotspot_dict.items():
        for hotspot in hotspots:
            all_hotspot_ids.add(hotspot["id"])
    
    # Get all figure IDs from pdf_link_mapping
    all_figure_ids = set(pdf_link_mapping.keys())
    
    # Check for figures without hotspots
    figures_without_hotspots = all_figure_ids - all_hotspot_ids
    
    # Check for hotspots without figures
    hotspots_without_figures = all_hotspot_ids - all_figure_ids
    
    # Prepare error messages
    error_messages = []
    
    if figures_without_hotspots:
        error_messages.append(
            f"Figures defined in pdf_link_mapping but missing hotspots: {sorted(figures_without_hotspots)}"
        )
    
    if hotspots_without_figures:
        error_messages.append(
            f"Hotspots defined in hotspot_dict but missing figures: {sorted(hotspots_without_figures)}"
        )
    
    # Check for None/null figures in mapping
    null_figures = [hotspot_id for hotspot_id, fig in pdf_link_mapping.items() if fig is None]
    if null_figures:
        error_messages.append(
            f"Hotspot IDs with None/null figures: {sorted(null_figures)}"
        )
    
    # Raise error if any issues found
    if error_messages:
        raise ValueError(
            "Figure and hotspot mapping verification failed:\n" + 
            "\n".join(f"  - {msg}" for msg in error_messages)
        )
    
    # Success message
    print(f"✓ Verification passed: {len(all_figure_ids)} figures mapped to {len(all_hotspot_ids)} hotspots")
    
    # Optional: print summary
    print("\nMapping summary:")
    for page_index, hotspots in sorted(hotspot_dict.items()):
        print(f"  Page {page_index}: {len(hotspots)} hotspots")
        for hotspot in hotspots:
            hotspot_id = hotspot["id"]
            has_figure = "✓" if hotspot_id in pdf_link_mapping else "✗"
            print(f"    {hotspot_id} {has_figure}")
