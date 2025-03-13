import os
import glob
import xml.etree.ElementTree as ET
import json
from typing import List, Dict, Any

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Required package 'beautifulsoup4' missing\nRun: pip install beautifulsoup4")
    exit(1)

def parse_cdata_content(cdata: str) -> Dict[str, Any]:
    """
    Parse HTML content from CDATA sections with hierarchy preservation
    
    Args:
        cdata: CDATA content containing HTML markup
        
    Returns:
        Dictionary with structured content extracted from HTML
    """
    if not cdata or not cdata.strip():
        return {}
    
    # Extract actual content from CDATA wrapper if present
    if '<![CDATA[' in cdata and ']]>' in cdata:
        start = cdata.find('<![CDATA[')
        end = cdata.rfind(']]>')
        if start != -1 and end != -1:
            cdata = cdata[start+9:end]
    
    try:
        soup = BeautifulSoup(cdata, 'html.parser')
        structure = {"sections": {}}
        current_section = "main"
        
        # Process all relevant HTML elements
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'li', 'div']):
            # Headers define new sections
            if element.name in ['h1', 'h2', 'h3', 'h4']:
                current_section = element.get_text().strip()
                structure["sections"][current_section] = []
            # Process paragraphs
            elif element.name == 'p' and current_section in structure["sections"]:
                text = element.get_text().strip()
                if text:
                    structure["sections"][current_section].append(text)
            # Process lists
            elif element.name == 'ul' and current_section in structure["sections"]:
                items = [li.get_text().strip() for li in element.find_all('li')]
                if items:
                    structure["sections"][current_section].extend(items)
        
        # If no sections were found, extract all text
        if not structure["sections"] and soup.get_text().strip():
            structure["text"] = soup.get_text().strip()
            
        return structure
    except Exception as e:
        print(f"CDATA parsing error: {str(e)}")
        return {"error": str(e)}

def process_xml_files(directory: str) -> List[Dict]:
    """
    Process all XML files in a directory and extract structured data
    
    Args:
        directory: Path to directory containing XML files
    
    Returns:
        List of dictionaries containing extracted data
    """
    results = []
    xml_files = glob.glob(os.path.join(directory, '*.xml'))
    
    for xml_file in xml_files:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Get document name as title or fallback to filename
            doc_name = root.get('name') or os.path.basename(xml_file).replace('.xml', '')
            
            # Extract CDATA sections from properties
            body_text = None
            summary = None
            regulatory = None
            
            for prop in root.findall('.//property'):
                prop_name = prop.get('name')
                if prop_name == 'gsb:bodyText':
                    text_elem = prop.find('text')
                    if text_elem is not None and text_elem.text:
                        body_text = text_elem.text
                elif prop_name == 'gsb:summary':
                    text_elem = prop.find('text')
                    if text_elem is not None and text_elem.text:
                        summary = text_elem.text
                elif prop_name == 'gsb:regulatoryFWork':
                    text_elem = prop.find('text')
                    if text_elem is not None and text_elem.text:
                        regulatory = text_elem.text
            
            # Find all links
            links = []
            for link in root.findall('.//link'):
                href = link.get('{http://www.w3.org/1999/xlink}href')
                if href:
                    links.append(href)
            
            # Create reference URL by combining base URL with document title
            reference_url = f"https://www.foerderdatenbank.de/FDB/Content/DE/Foerderprogramm/Bund/BMWi/{doc_name}.html"
            
            entry = {
                'file_name': os.path.basename(xml_file),
                'title': doc_name,
                'referncetofdbwebsite': reference_url,
                'content': parse_cdata_content(body_text) if body_text else {},
                'funding_details': parse_cdata_content(summary) if summary else {},
                'eligibility': parse_cdata_content(regulatory) if regulatory else {},
                'links': links
            }
            
            results.append(entry)
        except ET.ParseError as e:
            print(f"Error parsing {xml_file}: {e}")
        except Exception as e:
            print(f"Error processing {xml_file}: {e}")
    
    return results

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Process XML files in a directory')
    parser.add_argument('directory', help='Path to directory containing XML files')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    args = parser.parse_args()
    
    data = process_xml_files(args.directory)
    
    if args.output:
        def export_to_json(data: List[Dict], output_file: str):
            """Export extracted data to JSON file"""
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        export_to_json(data, args.output)
        print(f"Exported {len(data)} records to {args.output}")
    else:
        for entry in data:
            print(f"Title: {entry['title']}")
            print(f"Content: {str(entry['content'])[:1000]}...")
            print(f"Links: {entry['links']}")
            print("-" * 50)
