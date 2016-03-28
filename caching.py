import dataset
from datetime import datetime, timedelta

def check_if_cache_fresh(request, cache):
    found = cache.find_one(request=request)
    if found:
        check = found['last_mod'] + timedelta(weeks = 1)

        if datetime.now() < check:
            print("\nFound in cache! Returning cached result.")
            return found['page']
        else:
            cache.delete(request=request)
            return "Outdated cache. Request again"
    else:
        return "Not found"

def save_in_cache(request, server_response, cache):
    # if it is cache-able:
    print(server_response)
    if(str(server_response, 'ISO-8859-1').find('Last-Modified:')) > -1:
        last_mod_date = str(server_response, 'ISO-8859-1')[str(server_response, 'ISO-8859-1').find('Last-Modified:') + 15:]
        last_mod_date = last_mod_date[:last_mod_date.find('GMT')]

        last_mod_date = datetime.strptime(last_mod_date, '%a, %d %b %Y %H:%M:%S ')

        if (str(server_response, 'ISO-8859-1').find('Expires: -1')) == -1 and \
            (str(server_response, 'ISO-8859-1').find('Expires:')) > -1 :
            expired_date = str(server_response, 'ISO-8859-1')[str(server_response, 'ISO-8859-1').find('Expires:') + 9:]
            expired_date = expired_date[:expired_date.find('GMT')]

            expired_date = datetime.strptime(expired_date, '%a, %d %b %Y %H:%M:%S ')

            if last_mod_date and last_mod_date + timedelta(minutes = 10) > expired_date or expired_date < datetime.now():
                print('\nThis page CANNOT be cached')

            else:
                print('This page can be cached. Saving cache now.')
                cache.insert(dict(request=request, last_mod=last_mod_date, page=server_response))

        else:
            print('This page can be cached. Saving cache now.')
            cache.insert(dict(request=request, last_mod=last_mod_date, page=server_response))


    # Else it isn't cache-able
    elif(str(server_response, 'ISO-8859-1').find('no-cache')) > -1 or \
                    (str(server_response, 'ISO-8859-1').find('Expires: -1')) > -1 or \
                    (str(server_response, 'ISO-8859-1').find('Expires: Thu, 19 Nov 1981 08:52:00 GMT')) > -1 :
        print('\nThis page CANNOT be cached')

    else:
        print('\nThis page CANNOT be cached')
