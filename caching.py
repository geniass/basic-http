import dataset
from datetime import datetime, timedelta
import HttpResponse

def check_if_cache_fresh(request, cache):
    dummy_time = datetime.strptime("01 01 1000 00:00:00", '%d %m %Y %H:%M:%S')
    found = cache.find_one(request=request)

    if found:
        user_date = datetime.utcnow()

        # Found request in cache
        # If there's no expiry date, but there is a max-age, check that the cache is still fresh
        if found['expiry'] == dummy_time and found['max_age'] != 0:
            check = found['last_mod'] + timedelta(seconds = found['max_age'])
            if user_date < check and user_date > found['last_mod']:
                return dict(status = "Found in cache! Returning cached result.",page=found['page'])
            else:
                # Else the found entry is outdated and url must be requested again
                cache.delete(request=request)
                return dict(status = "Outdated cache entry. Requesting again", page='',last_mod='')

        # Else if there's not an expiry header nor a max-age header, make conditional get
        elif found['expiry'] == dummy_time and found['max_age'] == 0:
            return dict(status = "Found in cache. But no expiry or max-age. Make conditional get request",page='',
                        last_mod = found['last_mod'])

        # Else if there is an expiry date, compare it to your date
        else:
            if found['expiry'] > user_date:
                return dict(status = "Found in cache! Returning cached result.",page=found['page'])
            else:
                # Else the found entry is outdated and url must be requested again
                cache.delete(request=request)
                return dict(status = "Outdated cache entry. Requesting again", page='',last_mod='')

    else:
        return dict(status = "Request not found in cache", page='',last_mod='')

def save_in_cache(request, server_response, cache):
    to_save_in_cache = 1
    dummy_time = datetime.strptime("01 01 1000 00:00:00", '%d %m %Y %H:%M:%S')

    if server_response.last_mod:
        # Check if it has a last modified header
        last_mod_date = datetime.strptime(server_response.last_mod, '%a, %d %b %Y %H:%M:%S GMT')
    else:
        last_mod_date = datetime.utcnow()

    if server_response.expires and server_response.expires != '-1':
        # Check if it has an expiry header
        expiry_date = datetime.strptime(server_response.expires, '%a, %d %b %Y %H:%M:%S GMT')

        if expiry_date > (datetime.utcnow()):
            to_save_in_cache = 1
        else:
            # If expiry date is before present date, don't save
            to_save_in_cache = 0

        if last_mod_date + timedelta(minutes = 1) > expiry_date:
            # If it expires within 10 minutes of modification, don't save
            to_save_in_cache = 0

    if server_response.expires and server_response.expires == '-1':
        # If expiry date = -1 (default set by server when page not cache-able), don't save
        to_save_in_cache = 0

    if server_response.cache_control and (server_response.cache_control.find("no-cache") > -1):
        to_save_in_cache = 0

    if to_save_in_cache == 1:

        if server_response.cache_control and server_response.cache_control.startswith('max-age'):
            # Save max_age (validity) of page if specified by server
            max_age = server_response.cache_control[(server_response.cache_control.find('max-age=')+8):]
            max_age = max_age[:max_age.find(',')]
        else:
            # Default age not specified by server.
            max_age = 0

        print('\nThis page can be cached. Saving cache now.\n')
        # Store in cache database
        if server_response.expires:
            cache.insert(dict(request=request, last_mod=last_mod_date, max_age = max_age, expiry = expiry_date,
                              page=server_response.gen_message()))
        else:
            cache.insert(dict(request=request, last_mod=last_mod_date, max_age = max_age, expiry = dummy_time,
                              page=server_response.gen_message()))

    else:
        print('\nThis page cannot be cached.\n')
