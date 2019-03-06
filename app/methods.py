from bad_email_domains import BAD_EMAIL_DOMAIN_LIST

def generate_search_link(contacts):
    link = None
    search_domains = []
    base_url = "https://secure.helpscout.net/search/?query=email:"
    for contact in contacts:
        for email in contact['emails']:
            email_domain = email['email'].split('@')[1]
            search_domain = '*@%s' % email_domain
            if search_domain not in search_domains and email_domain not in BAD_EMAIL_DOMAIN_LIST:
                search_domains.append(search_domain)
            if len(search_domains) > 0:
                link = "%s(%s)" % (base_url, ' OR '.join(search_domains))
    return link
