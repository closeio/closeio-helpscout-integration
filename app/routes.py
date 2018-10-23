import os
from flask import render_template, redirect, url_for, flash, request, jsonify
from app import app
import json
from closeio_api import Client as CloseIO_API, APIError

# Close.io API Initialization
api = CloseIO_API(os.environ['api_key'])
# Get all users in an org
org_id = api.get('api_key/' + os.environ['api_key'])['organization_id']
org = api.get('organization/' + org_id)
memberships = [i for i in org['memberships']] + [i for i in org['inactive_memberships']]
users = {}
for member in memberships:
    users[member['user_id']] = member['user_full_name']


@app.route('/', methods=['POST'])
def index():
    email = ""
    try:
        data = json.loads(request.data)
    except ValueError:
        return '', 400
    else:
        email = data['customer']['email']
    if email == "":
        return jsonify({ 'html': '<span style="color:red;">Cannot pull data</span>' })
    else:
        try:
            resp = api.get('lead', params={ 'query': 'email_address:"%s" sort:-"Monthly Billable Amount"' % email })
        except APIError as e:
            return jsonify({ 'html': '<span style="color:red;">There was a Close.io API Error</span>' })
    if len(resp['data']) > 0:
        lead = resp['data'][0]
        for key in lead['custom']:
            if str(lead['custom'][key]).startswith('user_'):
                lead['custom'][key] = users[lead['custom'][key]]
        template = app.jinja_env.get_template('has_lead.html')
        return jsonify({'html': template.render(lead)})
    else:
        template = app.jinja_env.get_template('no_lead.html')
        return jsonify({'html': template.render(data['customer'])})

# Create Lead Route
@app.route('/create-lead/', methods=['GET'])
def index2():
    contact = { 'emails': [{'email': request.args.get("email")}]}
    contact['name'] = "%s %s" % (request.args.get("fname"), request.args.get("lname"))
    lead = { 'contacts': [contact] }
    try:
        resp = api.post('lead', data=lead)
        return redirect("https://app.close.io/lead/%s/" % resp['id'], code=302)
    except APIError as e:
        # This will bring Close.io to an error page if lead creation fails
        return redirect("https://app.close.io/lead//", code=302)
