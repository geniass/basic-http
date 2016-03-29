import dataset
from datetime import datetime, timedelta
import HttpResponse

def check_if_cache_fresh(request, cache):
    dummy_time = datetime.strptime("01 01 1000 00:00:00", '%d %m %Y %H:%M:%S')
    found = cache.find_one(request=request)
    if found: # Found request in cache
        # If there's no expiry date, check that the last-modified date isn't too old
        if found['expiry'] == dummy_time:
            check = found['last_mod'] + timedelta(weeks = 1)
            if datetime.now() < check:
                print("Found in cache! Returning cached result.")
                return found['page']
        # If there is an expiry date, compare it to today's date
        elif found['expiry'] != dummy_time:
            if found['expiry'] > datetime.now():
                print("Found in cache! Returning cached response.\n\n")
                return found['page']
        else:
            # Else the found entry is outdated and url must be requested again
            cache.delete(request=request)
            return "Outdated cache entry. Requesting again"

    else:
        return "Request not found in cache"

def save_in_cache(request, server_response, cache):
    # Save flag
    to_save_in_cache = 0
    dummy_time = datetime.strptime("01 01 1000 00:00:00", '%d %m %Y %H:%M:%S')

    if server_response.last_mod:
        # Check if it has a last modified header
        last_mod_date = datetime.strptime(server_response.last_mod, '%a, %d %b %Y %H:%M:%S GMT')

        to_save_in_cache = 1

    if server_response.expires and server_response.expires != '-1':
        # Check if it has an expiry header
        expiry_date = datetime.strptime(server_response.expires, '%a, %d %b %Y %H:%M:%S GMT')

        if expiry_date > (datetime.now()):
            to_save_in_cache = 1

        if server_response.last_mod and (last_mod_date + timedelta(minutes = 10) > expiry_date):
            # If it expires within 10 minutes of modification, don't save
            to_save_in_cache = 0

        if expiry_date < (datetime.now()):
            # If expiry date is before present date, don't save
            to_save_in_cache = 0
            print('TO CACHE EXPIRY IS IN THE PAST')
            print((datetime.now() + timedelta(days = 1)))
            print(to_save_in_cache)

    if server_response.expires and server_response.expires == '-1':
        # If expiry date = -1 (default set by server when page not cache-able), don't save
        to_save_in_cache = 0


    if to_save_in_cache == 1:
        print('\nThis page can be cached. Saving cache now.\n')
        # Store in cache database
        if server_response.last_mod and server_response.expires and server_response.expires != '-1':
            cache.insert(dict(request=request, last_mod=last_mod_date, expiry = expiry_date,
                              page=server_response.gen_message()))
        elif not server_response.last_mod and server_response.expires and server_response.expires != '-1':
            cache.insert(dict(request=request, last_mod= dummy_time, expiry = expiry_date,
                              page=server_response.gen_message()))
        else:
            cache.insert(dict(request=request, last_mod=last_mod_date, expiry = dummy_time,
                              page=server_response.gen_message()))

    else:
        print('\nThis page cannot be cached.\n')
