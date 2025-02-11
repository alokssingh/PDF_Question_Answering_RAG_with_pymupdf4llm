import os
import sys
import pandas as pd
from QA_without_runnable_ollama import get_question_answers
import os
import pandas as pd
import pymupdf
import pymupdf4llm
from multi_column import column_boxes
import fitz  # PyMuPDF library
import re
from datetime import datetime, timedelta 

def parse_pdf_date_with_timezone(date_string):
    """
    Parses a PDF date string in the format D:YYYYMMDDHHmmSS+TZ'HZ' or D:YYYYMMDDHHmmSS-TZ'HZ'
    and returns it as 'Month Day, Year, HH:mm:ss (UTC+TZ)'
    """
    if date_string.startswith("D:"):
        date_string = date_string[2:]  # Remove the "D:" prefix

    # Extract the main date part (YYYYMMDDHHmmSS)
    date_part = date_string[:14]

    # Extract the timezone part (+TZ'HZ' or -TZ'HZ')
    tz_part = date_string[14:]

    try:
        # Parse the main date part
        parsed_date = datetime.strptime(date_part, "%Y%m%d%H%M%S")
    except ValueError:
        raise ValueError(f"Invalid date part: {date_part}. Expected format: YYYYMMDDHHmmSS.")

    # Handle the timezone part if present
    if tz_part:
        # Validate timezone part using regex
        if re.match(r"[+-]\d{2}'\d{2}'", tz_part):
            sign = 1 if tz_part[0] == '+' else -1
            try:
                hours = int(tz_part[1:3])
                minutes = int(tz_part[4:6])
                offset = timedelta(hours=sign * hours, minutes=sign * minutes)
                parsed_date += offset
            except ValueError:
                raise ValueError(f"Invalid numeric values in timezone part: {tz_part}")
        else:
            raise ValueError(f"Invalid timezone format: {tz_part}. Expected format: +TZ'HZ' or -TZ'HZ'")
    else:
        # If no timezone is present, assume UTC
        tz_part = "+00'00'"

    # Format the date
    formatted_date = parsed_date.strftime("%B %d, %Y, %H:%M:%S")
    timezone_formatted = f"UTC{tz_part[0]}{tz_part[1:3]}:{tz_part[4:6]}"
    return f"{formatted_date} ({timezone_formatted})"

def get_pdf_metadata(pdf_path):
    """
    Extracts metadata from a PDF file using PyMuPDF.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        dict: A dictionary containing the metadata of the PDF.
    """
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    # Retrieve the metadata
    metadata = pdf_document.metadata
    # Close the PDF file
    pdf_document.close()

    # Parse creation and modification dates if available
    if 'creationDate' in metadata and metadata['creationDate']:
        try:
            metadata['creationDate'] = parse_pdf_date_with_timezone(metadata['creationDate'])
        except ValueError as e:
            print(f"Error: {e}") 
    if 'modDate' in metadata and metadata['modDate']:   
        try:
            metadata['modDate'] = parse_pdf_date_with_timezone(metadata['modDate'])
        except ValueError as e:
            print(f"Error: {e}") 

    return metadata




def remove_images_from_pdf(pdf_document):
    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        images = page.get_images(full=True)
        
        for image in images:
            xref = image[0]
            rect = page.get_image_rects(xref)
            if rect:
                for area in rect:
                    page.add_redact_annot(area, fill=(1, 1, 1))
                    page.apply_redactions()
    return pdf_document

def format_text(raw_text):
    heading_pattern = re.compile(r"^[A-Z ]{3,}.*$")
    subheading_pattern = re.compile(r"^\s*[•-]\s.*$")
    formatted_lines = []
    lines = raw_text.splitlines()
    
    for line in lines:
        if heading_pattern.match(line.strip()):
            formatted_lines.append(f"\n{line.strip()}\n{'-' * len(line.strip())}")
        elif subheading_pattern.match(line.strip()):
            formatted_lines.append(f"- {line.strip()[2:]}")
        elif line.strip():
            formatted_lines.append(f"  {line.strip()}")
    return "\n".join(formatted_lines)




def information_extraction(file_path,j):

    if not os.path.exists(file_path):
        print("File does not exist.")
        return
    pdf_file_name = file_path.split("/")[-1]
    data_centername = file_path.split("/")[-2]
    data_center = data_centername.split("_")[-1]
    data_provider =  data_centername.split("_")[-2]
    data_folder =  data_centername.split("_")[-3]

    metadata = get_pdf_metadata(file_path)

    pdf_data = metadata['creationDate']
    data_c_info = [data_folder,pdf_file_name, pdf_data, data_center, data_provider]    
    
    # pymupdf4llm it is llm based. Which extract the text based on markdown

    formatted_text = pymupdf4llm.to_markdown(file_path)
    if formatted_text == ' ':
        return
    
    """
    # if you want to extrect text using bounding boxes
    doc = pymupdf.open(file_path)
    #doc = remove_images_from_pdf(doc)
    formatted_text = ''
    formatted_text = ''
    for page_num, page in enumerate(doc):
        print(f"Processing page {page_num + 1}...")
        bboxes = column_boxes(page, footer_margin=0, no_image_text=True)
        if not bboxes:
            #print(f"No text boxes found on page {page_num + 1}.")
            text = page.get_text()
            formatted_text += format_text(text) + '\n' + "-" * 80 + '\n'
        else:
            for rect in bboxes:
                text = page.get_text(clip=rect, sort=True)
                if text.strip():  # Ensure non-empty text
                    formatted_text += format_text(text) + '\n' + "-" * 80 + '\n'
    
"""

#"Extract and list all certifications explicitly mentioned in the text. If no certifications are found, respond only with 'not available.' Do not provide explanations, additional information, or fabricated content.",

    list_questions  = [ "Is this pdf contains information about the "+ data_center +"  If yes respond with 'Yes' otherwise say 'No' do not provide explination ",
    "Is this pdf contains information about the"+" "+ data_provider +"  If yes respond with 'Yes' otherwise say 'No' do not provide explination ",
     "Is this pdf Sustainability Report/ ESG Report/ Annual Report .  If yes respond with 'Yes (ESG report/ Sustainability Report/ Annual Report)' otherwise say 'No' do not provide explination ",
    "Is this pdf Specification/technical Report.  If yes respond with 'Yes' otherwise say 'No' do not provide explination",
    "Give me only the name(s)  of the datacenter. Provide the name exactly as mentioned in the text. If none are mentioned, respond with 'not available' do not provide explination",
    "Extract and return only the full address of the data center mentioned in the text. Provide the address exactly as stated in the document. If no address is mentioned, respond only with 'not available'. Do not include explanations, additional details, or reformatted text.",
    "Just Give me only the name of the datacenter operator. Provide the operator as mentioned in the text.If none are mentioned, respond with 'not available' do not provide explination",
    "Just Give me only the city name where the "+ data_center +" datacenter located.  If none are mentioned, respond with 'not available' do not provide explination",
        "Give me only the country name where the" + data_center +"  datacenter located.  If none are mentioned, respond with 'not available' do not provide explination",
"Give me only the  operating status of the datacenter. If active respond with 'Active' otherwise 'Inactive'. If none are mentioned, respond with 'not available' do not provide explination",
    "Give me only the year (number only)  when was the datacenter built. Provide the year as mentioned in the text.If none are mentioned, respond with 'not available' do not provide explination",
    
    "Does the datacenter have SERVICES Full Cabinets, if yes say 'Yes', otherwise say 'No' do not provide explination",
    "Does the datacenter have SERVICES Shared Rackspace , if yes say 'Yes', otherwise say 'No' do not provide explination",
    "IS the  "+ data_center +" is ISO 27001  Certified , if yes say 'Yes', otherwise say 'No' do not provide explination",
    "IS the  "+ data_center +" is ISO 9001  Certified , if yes say 'Yes', otherwise say 'No' do not provide explination",
    "IS the  "+ data_center +" is ISO 14001  Certified , if yes say 'Yes', otherwise say 'No' do not provide explination",
    "IS the  "+ data_center +" is ISO 22301  Certified , if yes say 'Yes', otherwise say 'No' do not provide explination",
    "IS the  "+ data_center +" is ISO 45001  Certified , if yes say 'Yes', otherwise say 'No' do not provide explination",
    "IS the  "+ data_center +" is ISO 50001  Certified , if yes say 'Yes', otherwise say 'No' do not provide explination",
    "IS the  "+ data_center +" is SOC 1 Type I, Type II, or Type 2 security Certified , if yes say 'Yes', otherwise say 'No' do not provide explination",
    "IS the  "+ data_center +" is SOC 2 Type I, Type II, or Type 2 security Certified , if yes say 'Yes', otherwise say 'No' do not provide explination",
    "IS the  "+ data_center +" is SOC 3 Type I, Type II, or Type 2 security Certified , if yes say 'Yes', otherwise say 'No' do not provide explination",
    "IS the  "+ data_center +" is SAS 70  Certified , if yes say 'Yes', otherwise say 'No' do not provide explination",
    "Does the "+ data_center +" have COMPLIANCE DSS PCI Certified or Certifications , if yes say 'Yes', otherwise say 'No' do not provide explanation",

    "Does the "+ data_center +"  have Automatic Firesupression , if yes say 'Yes', otherwise say 'No' do not provide explanation",
    "Does the "+ data_center +"  have SECURITY Fenced Perimeter if yes respond with 'Yes'.only If none are mentioned, respond with 'not available'do not provide explanation  ",
    "Does the "+ data_center +"  have SECURITY CCTV surveillance if yes respond with 'Yes'.only If none are mentioned, respond with 'not available' do not provide explanation ",
    "Does the "+ data_center +"  have SECURITY Onsite Security Staff if yes respond with 'Yes and how many hours such as 24/7'.only If none are mentioned, respond with 'not available' do not provide explination ",
    "Does the "+ data_center +"  have SECURITY Biometric Access Control if yes respond with 'Yes'.only If none are mentioned, respond with 'not available' do not provide explanation ",
    "Does the "+ data_center +"  have SECURITY Card Access Control if yes respond with 'Yes'.only If none are mentioned, respond with 'not available'do not provide explanation  ",
    "Does the "+ data_center +"  have SECURITY Mantrap Entry if yes respond with 'Yes'.only If none are mentioned, respond with 'not available' do not provide explanation ",
   
   "Give me the number only of Total Critical Power, of "+ data_center +" . If none are mentioned, respond with 'not available'do not provide explanation ",
    "Does the datacenter have POWER UPS Redundancy if yes the give me only number (for example n+1). If none are mentioned, respond with 'not available'do not provide explination  ",
    "Does the datacenter have POWER Cooling Redundancy if yes the give me only number (for example n+1). If none are mentioned, respond with 'not available' do not provide explination ",
   
    
    "Give me only the floor type of the facility/building only mentioned in the text. Provide the type only as mentioned in the text (such as Raised Floor,Mixed). If none are mentioned, respond with 'not available' do not provide explination'",
    "Give me only the size of colocation space or technical or IT space of the facility or building mentioned in the text (just value such as 153,000 m sq) .  If none are mentioned, respond with 'not available' do not provide explination",
    "Give me only the size of BUILDING Total Whitespace of mentioned in the text (just size such as 153,000 m sq).  If none are mentioned, respond with 'not available' do not provide explination",

    "Give me only the number of Building Floors/Halls  mentioned in the text.  If none are mentioned, respond with 'not available''",
    "Give me only the BUILDING Max Floor Load mentioned in the text number only for example 10 kN/m2.  If none are mentioned, respond with 'not available' do not provide explination",
    "Extract and return only the size of the Building Floor-to-Ceiling Height as mentioned in the text. Provide the value exactly as stated in the document. If no such information is mentioned, respond only with 'not available'. Do not include explanations, additional details, or reformatted text.",
    
    "Give me only  of type of facility/building of  "+ data_center +" . for example if it is bare metal, colocation, enterprise, or hyperscaler, as mentioned in the text.If none are mentioned, respond with 'not available' do not provide explination",
 
    "Give me only the name(s) of the power system is in use by the "+ data_center +"  . Provide the system exactly as mentioned in the text.If none are mentioned, respond with 'not available' do not provide explination",
    "Give me only the renewable energy power generation capacity available on-site. Provide the capacity as mentioned in the text.If none are mentioned, respond with 'not available' do not provide explination",
"Extract and provide only the Power Usage Effectiveness (PUE) value explicitly mentioned for the  data_center . Output only the numeric value (e.g., 1.4). If no PUE is found in the text, respond with 'not available.' Do not generate, assume, or infer values not present in the text.",
    "Extract and list only the cooling techniques mentioned in the text. Provide the cooling techniques exactly as stated in the document. If no cooling techniques are mentioned, respond with 'not available'. Do not include explanations, additional details, or reformat the extracted text.",
    "Give me only number of the WUE or Water Usage Effectiveness (WUE) of the "+ data_center +"  (for example 1.4). If none is  mentioned, respond with 'not available' do not provide explination",  
    "Give me only the name(s) of Who are the reported clients of the  "+ data_provider +"  . List the clients exactly as mentioned in the text.If none are mentioned, respond with 'not available' do not provide explination",  
    "Does the  "+ data_center +"   have sustainability policies in place. State 'yes' or 'no' based on the text.If none are mentioned, respond with 'not available' do not provide explination",  
    "Extract and list all security measures mentioned in the document for  "+ data_center +" . Provide the security measures exactly as stated in the text. If no security measures are mentioned, respond with 'not available'. Do not include explanations, additional details, or reformat the extracted text.",
    "Give me list of all building overview features provide the systems exactly as mentioned in the text.If none are mentioned, respond with 'not available' do not provide explination",
    "Extract and list all power infrastructure details mentioned in the document for  "+ data_center +"  . Provide the power infrastructure details exactly as stated in the text. If no power infrastructure details are mentioned, respond with 'not available'. Do not include explanations, additional details, or reformat the extracted text.",
   "Extract and return only the certifications and awards assigned to the data center as mentioned in the document. List them exactly as they appear in the text. If no certifications or awards are mentioned, respond only with 'not available'. Do not include explanations, interpretations, or repeat previous responses."
]
  
    #list_questions = ['can you list all Amenities in the provided text?']
    new_texts = formatted_text
    data_dict = get_question_answers(new_texts, list_questions)
    
    if not data_dict:
        print("Dct is empty no answer")
    else:
        answer_list = data_dict.get("answers", [])


    # Defining the list of fields for excel 
    
    
    fields = ['Folder_ID', 'pdf_name_from_info' , 'Data pdf published','Data center', 'Data center provider',  "Pdf info about DC", "Pdf info about DC provider", "Sustainability Report",
              "Specification Report", "Data center name from pdf",   "Address",   "Operator",  "City", "Country",  "Operating status",  "Year",     'SERVICES Full Cabinets',
              ' SERVICES Shared Rackspace','ISO27001 Certified','ISO9001  Certified','ISO14001  Certified','ISO22301  Certified', 'ISO45001  Certified',
              'ISO50001  Certified','SOC 1 Type I/II/2  Certified','SOC 2 Type I/II/2 ','SOC 3 Type I/II/2 ','SAS70 Type 2','DSS PCI Certified','Firesupression',
              'Fenced Perimeter', 'CCTV surveillance ','Onsite Security Staff','Biometric Access Control','Card Access Control','Mantrap Entry', 'Total Critical Power',
              'UPS Redundancy','Cooling Redundancy',"Floor type","Colocation space",  "BUILDING Total Whitespace", "Floors Number", "Max Floor Load", "Floor to Ceiling Height" , 
              "Building/facility type",     "Power system in use",   "Renewable energy power capacity", "PUE",    "Cooling system", "WUE", "Reported clients", "Sustainability policies",     
              "Security system in use","Buiding_features", 'Power_all', "certification_awards"]
    
    # Create an empty DataFrame with these headers 
    df_qa = pd.DataFrame(columns=fields)
    data_c_info.extend(answer_list)
    df_qa.loc[0] = data_c_info

    if os.path.exists('DCM_UK_spec.xlsx'):
        # Read the existing file
        existing_data = pd.read_excel('DCM_UK_spec.xlsx')

        # Append the new data
        updated_data = pd.concat([existing_data, df_qa], ignore_index=True)
    else:
        # If the file does not exist, use the new data as the starting point
        updated_data = df_qa


        # Saving question answers to CSV
    updated_data.to_excel("DCM_UK_spec.xlsx",index=False)
    
    
    # Create an empty DataFrame with these headers 
    df_qa_context = pd.DataFrame(columns=fields)
    contexts = data_dict.get("contexts", [])

    data_c_info = [data_folder,pdf_file_name, pdf_data, data_center, data_provider]
    temp_data_c_info = data_c_info
    temp_data_c_info.extend(contexts)
    df_qa_context.loc[0] = temp_data_c_info

    if os.path.exists('DCM_UK_spec_context.xlsx'):
        # Read the existing file
        existing_data = pd.read_excel('DCM_UK_spec_context.xlsx')

        # Append the new data
        updated_data = pd.concat([existing_data, df_qa_context], ignore_index=True)
    else:
        # If the file does not exist, use the new data as the starting point
        updated_data = df_qa_context


        # Saving question answers to CSV
    updated_data.to_excel("DCM_UK_spec_context.xlsx",index=False)

    
def extract_numeric_prefix(folder_name):
    """
    Extracts the leading numeric part of a folder name.
    Example: '0_Iron Mountain Data Centers' -> 0
    """
    match = re.match(r"(\d+)", folder_name)
    return int(match.group(1)) if match else float('inf')  # Use 'inf' if no numeric prefix is found



def main(folder_path):
    
    if not os.path.exists(folder_path):
        print("Folder does not exist.")
        return   
    
    subfolders = sorted([f.path for f in os.scandir(folder_path) if f.is_dir()])
    subfolders = sorted(subfolders, key=lambda x: extract_numeric_prefix(os.path.basename(x)))


    #100
    for i in range(24,25):#49,50
        subfolder = subfolders[i]        

        # Get all files in the current subfolder
        files = [f.name for f in os.scandir(subfolder) if f.is_file()]

        # Loop through files with index `j`
        for j in range(len(files)):#
            file = files[j]
            # Process only PDF files
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(subfolder, file)
                information_extraction(pdf_path,j)
   


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <file_path>")
    else:
        file_path = sys.argv[1]
        main(file_path)


# Run using this command in terminal- python main1.py Copy_for_Google_search.xlsx
