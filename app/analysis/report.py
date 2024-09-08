from jinja2 import Environment, FileSystemLoader
import pdfkit

def generate_report(data, template_path, output_pdf):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_path)
    html_output = template.render(data=data)
    
    with open('report.html', 'w') as f:
        f.write(html_output)
    
    pdfkit.from_file('report.html', output_pdf)
