
import os
from pdf_plan_sorter import PdfPlanSorter
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_files():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'weights' not in request.files or 'batches' not in request.files:
            return 'No file part'

        weights_file = request.files['weights']
        batches_file = request.files['batches']
        can1 = request.form.get('can1')
        hydro = request.form.get('hydro')
        line3 = request.form.get('line3')

        if weights_file.filename == '' or batches_file.filename == '':
            return 'No selected file'

        if weights_file and allowed_file(
                weights_file.filename) and batches_file and allowed_file(
                    batches_file.filename):
            weights_filename = secure_filename(weights_file.filename)
            batches_filename = secure_filename(batches_file.filename)
            weights_file_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                             weights_filename)
            batches_file_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                             batches_filename)
            weights_file.save(weights_file_path)
            batches_file.save(batches_file_path)

            # Process the files
            pdf_plan_sorter = PdfPlanSorter(weights_file_path,
                                            batches_file_path, can1, hydro,
                                            line3)

            pdf_plan_sorter.extract_weights_plans_and_pages()
            pdf_plan_sorter.extract_batches_plans_and_pages()
            combined_plans_with_pages = pdf_plan_sorter.combine_plans_and_pages(
            )
            # print(combined_plans_with_pages)
            output_pdf_path = pdf_plan_sorter.add_pages_to_pdf(
                combined_plans_with_pages)

            return send_file(output_pdf_path, as_attachment=True)

    return 'Error processing files'


if __name__ == '__main__':
    app.run(debug=True)
