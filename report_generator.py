import csv
from datetime import datetime
from fpdf import FPDF

class PDFReportGenerator:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.data = []
        self.metadata = {
            'title': 'Data Analysis Report',
            'author': 'Automated Report Generator',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.summary_stats = {}

    def load_data(self):
        """Load data from CSV file"""
        with open(self.input_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            self.data = list(csv_reader)
            
            # Cache the fieldnames for later use
            self.fieldnames = csv_reader.fieldnames

    def analyze_data(self):
        """Calculate summary statistics"""
        if not self.data:
            raise ValueError("No data loaded for analysis")
            
        numeric_fields = [field for field in self.fieldnames if any(
            str(row[field]).replace('.', '').isdigit() for row in self.data if row[field] and row[field].strip())
        ]
        
        for field in numeric_fields:
            values = []
            for row in self.data:
                try:
                    val = float(row[field]) if row[field] else 0
                    values.append(val)
                except ValueError:
                    continue
            
            if values:  # Only proceed if we found numeric values
                self.summary_stats[field] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values)
                }

    def generate_pdf(self):
        """Generate PDF report using fpdf2"""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Add cover page
        pdf.add_page()
        pdf.set_font('helvetica', 'B', 24)
        pdf.cell(0, 40, self.metadata['title'], 0, 1, 'C')
        pdf.set_font('helvetica', '', 14)
        pdf.cell(0, 15, f"Generated on: {self.metadata['date']}", 0, 1, 'C')
        pdf.ln(20)
        
        # Add data summary section
        pdf.set_font('helvetica', 'B', 16)
        pdf.cell(0, 10, 'Data Summary', 0, 1)
        pdf.set_font('helvetica', '', 12)
        
        if not self.summary_stats:
            pdf.cell(0, 10, 'No numeric data available for analysis', 0, 1)
        else:
            pdf.ln(5)
            pdf.set_font('helvetica', 'B', 12)
            pdf.cell(45, 10, 'Metric', 1, 0, 'C')
            pdf.cell(30, 10, 'Count', 1, 0, 'C')
            pdf.cell(30, 10, 'Min', 1, 0, 'C')
            pdf.cell(30, 10, 'Max', 1, 0, 'C')
            pdf.cell(30, 10, 'Average', 1, 1, 'C')
            pdf.set_font('helvetica', '', 10)
            
            for field, stats in self.summary_stats.items():
                pdf.cell(45, 8, field, 1, 0)
                pdf.cell(30, 8, str(stats['count']), 1, 0, 'C')
                pdf.cell(30, 8, f"{stats['min']:.2f}", 1, 0, 'C')
                pdf.cell(30, 8, f"{stats['max']:.2f}", 1, 0, 'C')
                pdf.cell(30, 8, f"{stats['avg']:.2f}", 1, 1, 'C')
        
        # Add sample data section
        if self.data:
            pdf.add_page()
            pdf.set_font('helvetica', 'B', 16)
            pdf.cell(0, 10, 'Sample Data (First 10 Rows)', 0, 1)
            pdf.set_font('helvetica', '', 10)
            
            # Calculate column widths based on content
            col_widths = [pdf.get_string_width(name) + 10 for name in self.fieldnames]
            
            # Header row
            pdf.set_font('helvetica', 'B', 10)
            for name, width in zip(self.fieldnames, col_widths):
                pdf.cell(width, 10, name, 1, 0, 'C')
            pdf.ln()
            
            # Data rows (limited to first 10)
            pdf.set_font('helvetica', '', 8)
            for row in self.data[:10]:
                for i, field in enumerate(self.fieldnames):
                    # Trim long values to prevent overflow
                    value = str(row.get(field, ''))
                    if len(value) > 15:
                        value = value[:12] + '...'
                    pdf.cell(col_widths[i], 8, value, 1, 0, 'L')
                pdf.ln()
        
        # Save PDF
        pdf.output(self.output_file)

def main():
    # Example usage
    input_file = 'sample_data.csv'
    output_file = 'analysis_report.pdf'
    
    try:
        report = PDFReportGenerator(input_file, output_file)
        report.load_data()
        report.analyze_data()
        report.generate_pdf()
        print(f"Report generated successfully: {output_file}")
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
    except Exception as e:
        print(f"Error generating report: {str(e)}")

if __name__ == '__main__':
    main()
