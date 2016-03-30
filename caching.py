import dataset
from datetime import datetime, timedelta
import HttpResponse

def check_if_cache_fresh(request, mod_since, cache):

    dummy_time = datetime.strptime("01 01 1000 00:00:00", '%d %m %Y %H:%M:%S')
    found = cache.find_one(request=request)

    if found:
        if mod_since == '':
            timestamp = datetime.utcnow()
        else:
            timestamp = mod_since

        # Found request in cache
        # If there's no expiry date, check that the last-modified date is still valid
        if found['expiry'] == dummy_time:
            check = found['last_mod'] + timedelta(seconds = found['max-age'])
            if timestamp < check and timestamp > found['last-mod']:
                print("Found in cache! Returning cached result.")
                return found['page']
            else:
                # Else the found entry is outdated and url must be requested again
                cache.delete(request=request)
                return "Outdated cache entry. Requesting again"

        # Else if there is an expiry date, compare it to your date
        elif found['expiry'] != dummy_time:
            if found['expiry'] > timestamp:
                print("Found in cache! Returning cached response.\n\n")
                return found['page']
        else:
            # Else the found entry is outdated and url must be requested again
            cache.delete(request=request)
            return "Outdated cache entry. Requesting again"

    else:
        return "Request not found in cache"

def save_in_cache(request, server_response, cache):
    to_save_in_cache = 0
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

        if server_response.last_mod and (last_mod_date + timedelta(minutes = 10) > expiry_date):
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
            # Default age not specified by server. Set default to 1 week; 86400 seconds = 1 week.
            max_age = 86400

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
