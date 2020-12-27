from flask import Flask
from flask import render_template
app = Flask(__name__)


@app.route('/<skill>')
def search(skill):
    from search_job import get_df, search_job_from_skill
    data = get_df()
    output, total, skill, ratio = search_job_from_skill(skill, data)
    return render_template('template1.html', output=output, total=total, skill=skill, ratio=ratio)
