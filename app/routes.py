import os
from flask import render_template, redirect, url_for, flash, request, jsonify
from app import app
import json
import requests

@app.route('/', methods=['POST'])
def index():
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % request.headers.get('X-Helpscout-Signature')}
    email = ""
    try:
        data = json.loads(request.data)
    except ValueError:
        return '', 400
    email = data['customer']['email']
    if email == "" or request.headers.get('X-Helpscout-Signature') == None:
        message = { 'message': 'Cannot process this request.'}
        template = app.jinja_env.get_template('errors.html')
        return jsonify({ 'html': template.render(message) })
    else:
        url = "https://app.close.io/api/v1/lead/"
        resp = requests.get(url, params={ 'query': 'email_address:"%s" sort:-contacts,-created' % email }, headers=headers)
        if resp.status_code != 200:
            message = { 'message': 'There was a Close API Error. Please check your API Key and reload the page.'}
            template = app.jinja_env.get_template('errors.html')
            return jsonify({ 'html': template.render(message) })
    if len(resp['data']) > 0:
        lead = resp['data'][0]
        org = requests.get('https://app.close.io/api/v1/organization/%s/' % lead.get('organization_id'), headers=headers, params={ '_fields': 'memberships,inactive_memberships' })
        if org.status_code != 200:
            message = { 'message': 'There was a Close API Error. Please check your API Key and reload the page.'}
            template = app.jinja_env.get_template('errors.html')
            return jsonify({ 'html': template.render(message) })
        memberships = [i for i in org['memberships']] + [i for i in org['inactive_memberships']]
        users = {}
        for member in memberships:
            users[member['user_id']] = member['user_full_name']
        for key in lead['custom']:
            if str(lead['custom'][key]).startswith('user_') and str(lead['custom'][key]) in users:
                lead['custom'][key] = users[lead['custom'][key]]
        template = app.jinja_env.get_template('has_lead.html')
        return jsonify({'html': template.render(lead)})
    else:
        template = app.jinja_env.get_template('no_lead.html')
        return jsonify({'html': template.render(data['customer'])})

# Create Lead Route
@app.route('/create-lead/', methods=['GET'])
def index2():
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % request.headers.get('X-Helpscout-Signature')}
    contact = { 'emails': [{'email': request.args.get("email")}]}
    contact['name'] = "%s %s" % (request.args.get("fname"), request.args.get("lname"))
    lead = { 'contacts': [contact] }
    resp = requests.post('https://app.close.io/api/v1/lead/', json=lead, headers=headers)
    if resp.status_code == 200:
        return redirect("https://app.close.io/lead/%s/" % resp['id'], code=302)
        # This will bring Close.io to an error page if lead creation fails
    else:
        return redirect("https://app.close.io/lead//", code=302)
