import os
import re
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
from collections import defaultdict

class PdfPlanSorter:

    def __init__(self, weights_file_path, batches_file_path, can1, hydro,
                 line3):
        self.weights_file_path = weights_file_path
        self.batches_file_path = batches_file_path
        self.can1 = can1.split('\r\n')
        self.hydro = hydro.split('\r\n')
        self.line3 = line3.split('\r\n')
        self.weights_plans_and_pages = {}
        self.batches_plans_and_pages = {}
    
    def extract_weights_plans_and_pages(self):
        weights_plan_number_re = re.compile(r'^2\d{6}')
        weights_page_number_re = re.compile(r'(Page)\s\-\s([0-9]+)')
    
        with pdfplumber.open(self.weights_file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                for line in text.split('\n'):
                    page_match = weights_page_number_re.search(line)
                    plan_match = weights_plan_number_re.search(line)
    
                    if page_match:
                        found_page = page_match.group(2)
                    elif plan_match:
                        found_plan = plan_match.group()
                        self.weights_plans_and_pages[found_page] = found_plan
    
    def extract_batches_plans_and_pages(self):
        batches_plan_number_re = re.compile(r'(Production Plan)\s\:\s([0-9]+)')
        batches_page_number_re = re.compile(r'(Page)\s\:\s([0-9]+)')
        flex_list_re = re.compile(r'(Production Plan)(.*)(Pouch)')
    
        with pdfplumber.open(self.batches_file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                for line in text.split('\n'):
                    # Check for flex
                    flex_match = flex_list_re.search(line)
                    if flex_match:
                        continue
    
                    # Extract page and plan numbers
                    page_match = batches_page_number_re.search(line)
                    plan_match = batches_plan_number_re.search(line)
    
                    if page_match:
                        found_page = page_match.group(2)
                    elif plan_match:
                        found_plan = plan_match.group(2)
                        self.batches_plans_and_pages[found_page] = found_plan
    
    def combine_plans_and_pages(self):
        combined_plans_with_pages = defaultdict(list)
        for d in (self.weights_plans_and_pages, self.batches_plans_and_pages):
            for key, value in d.items():
                combined_plans_with_pages[value].append(key)
        return combined_plans_with_pages
    
    def add_pages_to_pdf(self, combined_plans_with_pages):
        weights_input_pdf = PdfReader(self.weights_file_path)
        batches_input_pdf = PdfReader(self.batches_file_path)
        pdf_writer = PdfWriter()
    
        for items_list in [self.can1, self.hydro, self.line3]:
                # Add a blank page
            pdf_writer.add_blank_page(width=792,
                                      height=612)  # Standard US Letter size
            for items in items_list:
                try:
                    findpage2 = int(combined_plans_with_pages[items][1]) - 1
                    findpage1 = int(combined_plans_with_pages[items][0]) - 1
                    page2 = batches_input_pdf.pages[findpage2]
                    pdf_writer.add_page(page2)
                    page1 = weights_input_pdf.pages[findpage1]
                    pdf_writer.add_page(page1)
                except Exception as e:
                    print(f"An error occurred:{e}")
                    continue
    
        output_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                       "plans_in_order.pdf")
        with open(output_pdf_path, "wb") as output_file:
            pdf_writer.write(output_file)
    
        return output_pdf_path