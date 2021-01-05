from flask import Flask
from flask import render_template
import json
import plotly
import plotly.graph_objs as go
app = Flask(__name__)


@app.route('/')
def entrypage():
    return render_template('template3.html')


@app.route('/skill-to-job/<skill>')
def search_job(skill):
    from search_job import get_df, search_job_from_skill
    data = get_df()
    output, total, skill, ratio = search_job_from_skill(skill, data)
    return render_template('template1.html', output=output, total=total, skill=skill, ratio=ratio)


@app.route('/skill-to-industry/<skill>')
def bar_plot(skill):
    from search_job import get_df, get_industry
    df = get_df()
    output = get_industry(skill, df)
    data = [go.Bar(x=output['industry'], y=output['counts'])]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('template4.html',
                           graphJSON=graphJSON, skill=skill)


@app.route('/job-to-skill/<job>')
def search_skill(job):
    from search_skill import get_df, read_file, searchskill
    data = get_df()
    output, job = searchskill(job, data)
    return render_template('template2.html', output=output, job=job)
