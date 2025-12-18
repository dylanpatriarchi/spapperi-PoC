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
        return output_path
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        # Return None or raise? Let's return None and handle in caller
        return None

def generate_commercial_proposal(config_data: Dict[str, Any], filename_prefix: str = "spapperi_preventivo") -> str:
    """
    Generate a Commercial Proposal PDF.
    Includes mock pricing logic for POC.
    """
    try:
        # 1. Calculate Prices (Mock Logic)
        base_price = 12500.00
        pricing_items = []
        
        # Accessories Cost
        accessories = []
        if config_data.get("accessories_primary"): accessories.extend(config_data["accessories_primary"])
        if config_data.get("accessories_secondary"): accessories.extend(config_data["accessories_secondary"])
        if config_data.get("accessories_element"): accessories.extend(config_data["accessories_element"])
        
        for acc in accessories:
            if acc != "Nessuno":
                # Randomize price slightly based on name length just to vary it, or fixed
                # Mock prices
                price = 0
                if "Spandiconcime" in acc: price = 1850.00
                elif "Microgranulatore" in acc: price = 1200.00
                elif "Innaffiamento" in acc: price = 950.00
                elif "Ruote" in acc: price = 450.00
                else: price = 850.00
                
                pricing_items.append({"name": acc, "price": f"{price:,.2f}"})
                base_price += price

        total_price = base_price
        vat = total_price * 0.22
        grand_total = total_price + vat

        # Prepare context
        template = env.get_template("commercial_template.html")
        logo_path = os.path.join(SOURCE_DIR, "logo_spapperi.svg")
        logo_url = f"file://{logo_path}"

        html_content = template.render(
            config=config_data,
            logo_path=logo_url,
            pricing_items=pricing_items,
            total_price=f"{total_price:,.2f}",
            vat_amount=f"{vat:,.2f}",
            grand_total=f"{grand_total:,.2f}",
            generation_time=datetime.now()
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.pdf"
        output_path = os.path.join(EXPORT_DIR, filename)

        HTML(string=html_content, base_url=SOURCE_DIR).write_pdf(output_path)
        return output_path

    except Exception as e:
        print(f"Error generating Commercial Proposal: {e}")
        return None
