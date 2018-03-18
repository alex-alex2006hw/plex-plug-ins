#!/usr/bin/env python
import urllib2

def CheckAdmin():
    """
    For Plex Home   : Only the main users token is accepted at http://127.0.0.1:32400/myplex/account
    For All Else    : Only the main users token is accepted at https://plex.tv/users/account
    """

    url = 'https://plex.tv/users/account' if Prefs['plextv'] else 'http://127.0.0.1:32400/myplex/account'

    Log.Debug('*' * 80)
    Log.Debug('* Checking if user is Admin')
    Log.Debug('* Auth URL   = %s' %url)

    try:
        ptoken = Request.Headers.get('X-Plex-Token', '')
        Log.Debug('* %sPlex Token is available for validation' %('' if ptoken else 'No '))
        req = urllib2.Request(url, headers={'X-Plex-Token': ptoken})
        res = urllib2.urlopen(req)
        if res.read():
            Log.Debug('* Current User is Admin')
            Log.Debug('*' * 80)
            return True
    except Exception as e:
        Log.Error('* Current User is NOT Admin')
        Log.Error('* CheckAdmin: User denied access: %s' %str(e))
        Log.Debug('*' * 80)
        return False
