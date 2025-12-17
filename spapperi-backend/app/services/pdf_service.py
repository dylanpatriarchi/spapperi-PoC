import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from datetime import datetime
from typing import Dict, Any

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
EXPORT_DIR = os.path.join(os.path.dirname(BASE_DIR), "exports")
SOURCE_DIR = os.path.join(os.path.dirname(BASE_DIR), "source")

# Ensure export directory exists
os.makedirs(EXPORT_DIR, exist_ok=True)

# Initialize Jinja2 environment
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def generate_report(config_data: Dict[str, Any], filename_prefix: str = "spapperi_config", recommendation: str = None) -> str:
    """
    Generate a PDF report from the configuration data.
    
    Args:
        config_data: Dictionary containing configuration details
        filename_prefix: Prefix for the output filename
        
    Returns:
        str: Absolute path to the generated PDF file
    """
    try:
        # Prepare data for template
        template = env.get_template("report_template.html")
        
        # Logo path - WeasyPrint needs absolute file path
        logo_path = os.path.join(SOURCE_DIR, "logo_spapperi.svg")
        # If svg doesn't work with WeasyPrint nicely without cairosvg (which requires external libs), 
        # we might need png. Let's try svg first, but check if we have a png.
        # Based on previous find, we have source/logo_spapperi.svg
        # Let's use file:// protocol for safety
        logo_url = f"file://{logo_path}"
        
        # Convert Markdown recommendation to HTML if present
        recommendation_html = None
        if recommendation:
            import markdown
            recommendation_html = markdown.markdown(recommendation)

        # Render HTML
        html_content = template.render(
            config=config_data,
            logo_path=logo_url,
            recommendation=recommendation_html,
            generation_time=datetime.now()
        )
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.pdf"
        output_path = os.path.join(EXPORT_DIR, filename)
        
        # Generate PDF
        HTML(string=html_content, base_url=SOURCE_DIR).write_pdf(output_path)
        
        return output_path
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        # Return None or raise? Let's return None and handle in caller
        return None
