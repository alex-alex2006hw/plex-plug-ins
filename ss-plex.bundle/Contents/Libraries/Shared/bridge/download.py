import ss
import settings

import os
import signal
import thread

log = ss.util.getLogger('ss.bridge.download')

def queue():           return settings.get('downloads',        [])
def history():         return settings.get('download_history', [])
def dlq():         return settings.get('download_dlq', [])
def failed():          return settings.get('download_failed',  [])
def avoid_flv():       return settings.get('avoid_flv_downloading')
def speed_limit():     return settings.get('download_limit', 0)
def download_limit():     return settings.get('simultaneous_downloads')
def force_success_option():     return settings.get('auto_force_success')
def assumed_running(): return (0 < len(dlq()))
def curl_running(pid):    return pid_running(pid)
def running_windows(): return 'nt' == os.name

def strategy():
    return settings.get('download_strategy', 'curl')

def clear_history(): settings.clear('download_history')
def clear_failed():  settings.clear('download_failed')

def append(**kwargs):
    queue().append(kwargs)
    settings.persist()

def append_failed(**kwargs):
    failed().append(kwargs)
    settings.persist()

def append_history(endpoint):
    history().append(endpoint)
    settings.persist()

def append_dlq(**download):
    dlq().append(download)
    settings.persist()

def remove(endpoint):
    remove_from_collection(endpoint, queue())

def remove_failed(endpoint):
    remove_from_collection(endpoint, failed())

def remove_dlq(endpoint):
    remove_from_collection(endpoint, dlq())

def set_current(download):
    settings.set('download_current', download)
    settings.persist()

def is_current(endpoint):
    return assumed_running() and is_dlq(endpoint)

def current(endpoint):
    for i, items in enumerate(dlq()):
        if endpoint == items['endpoint']:
            return items

def current_queue(endpoint):
    found = filter(lambda d:d['endpoint'] == endpoint, dlq())
    if found: return found[0]

def current_pid(endpoint):
    for i, items in enumerate(dlq()):
        if endpoint == items['endpoint']:
            return items['pid']

def in_history(endpoint):
    return endpoint in history()

def in_dlq(endpoint):
    return endpoint in dlq()

def get_from_collection(endpoint, collection):
    found = filter(lambda d: d['endpoint'] == endpoint, collection)
    if found: return found[0]

def remove_from_collection(endpoint, collection):
    found = get_from_collection(endpoint, collection)
    if not found: return

    collection.remove(found)
    settings.persist()

def from_dlq(endpoint):
    return get_from_collection(endpoint, dlq())

def from_queue(endpoint):
    return get_from_collection(endpoint, queue())

def from_failed(endpoint):
    return get_from_collection(endpoint, failed())

def is_dlq(endpoint):
    return bool(from_dlq(endpoint))

def is_queued(endpoint):
    return bool(from_queue(endpoint))

def is_failed(endpoint):
    return bool(from_failed(endpoint))

def get(endpoint):
    _current = is_current(endpoint)
    if _current: return _current

    _queued = from_queue(endpoint)
    if _queued: return _queued

    _failed = from_failed(endpoint)
    if _failed: return _failed

def includes(endpoint):
    if get(endpoint): return True
    return in_history(endpoint)

def was_successful(endpoint):
    return is_current(endpoint) or is_dlq(endpoint) or is_queued(endpoint) or in_history(endpoint)

def update_library(section): pass
def on_start(dl): pass
def on_error(dl): pass
def on_success(dl): pass

def check_queue(openqueue = 0):
    restart = True
    while restart:
        restart = False
        for i, items in enumerate(dlq()):
            if items['pid'] and not pid_running(items['pid']):
                status = ss.downloader.status_for(items['endpoint'], strategy = strategy())
                log.info('Found download, %s, at %s complete' % (items['title'], status.report()[0].split("%%"[0])[0]))
                if 100 == int(status.report()[0].split("%%"[0])[0]) and force_success_option():
                    force_success(items['endpoint'], should_dispatch = False)
                    log.info('Forced Success of %s' % items['title'])
                    openqueue = openqueue + 1
                else:
                    log.info('Restarting anbandoned download: %s' % items['title'])
                    force_failure(items['endpoint'], should_dispatch = False)
                    remove_failed(items['endpoint'])
                    append(title = items['title'], endpoint = items['endpoint'], media_hint = items['media_hint'])
                    openqueue = openqueue + 1
                restart = True
                break
            if items['pid'] and pid_running(items['pid']):
                log.info('Active Item %s' % items['title'])

    if (openqueue + len(queue()) + 1) > int(download_limit()):
        log.debug('Current download queue larger then permitted download amount Dispatching %s times' % download_limit())
        for i in range(int(download_limit())):
            dispatch()
    else:
        log.debug('Dispatching %s times, based on current download queue.' % (openqueue + len(queue()) + 1))
        for i in range(openqueue + len(queue()) + 1):
            dispatch()

def command(command, endpoint, pid):
    if not curl_running(pid):
        return
    signals  = [ signal.SIGTERM, signal.SIGINT ]
    commands = [ 'cancel',       'next' ]
    to_send  = signals[commands.index(command)]

    return signal_process(pid, to_send)

def force_success(endpoint, should_dispatch = True):
    import os

    _d = current(endpoint)
    _h = _d['media_hint']
    dest_key = '%s_destination' % _h
    destination = settings.get(dest_key)
    localfile = os.path.join(destination, _d['title'])
    partfile = localfile + '.part'

    try:    os.rename(partfile, localfile)
    except: pass

    update_library(_h)
    append_history(_d['endpoint'])
    remove_dlq(endpoint)
    if should_dispatch:
        dispatch()

def force_failure(endpoint, should_dispatch = True):
    import os

    _d = current(endpoint)
    _h = _d['media_hint']
    dest_key = '%s_destination' % _h
    destination = settings.get(dest_key)
    localfile = os.path.join(destination, _d['title'])
    partfile = localfile + '.part'

    try:    os.remove(partfile)
    except: pass

    append_failed(title = _d['title'], endpoint = _d['endpoint'],
            media_hint = _d['media_hint'])
    remove_dlq(endpoint)
    if should_dispatch:
        dispatch()
		
def dispatch(should_thread = True):

    if int(download_limit()) <= len(dlq()):
        log.debug('Download queue is full %s of %s' % (len(dlq()), download_limit()))
        return

    try:
        download = queue().pop(0)
        log.debug('Queue %s of %s' % (len(dlq()), download_limit()))
        append_dlq(endpoint = unicode(download['endpoint']),
                title = download['title'],
                media_hint = download['media_hint'],
                pid = '')

    except IndexError, e:
        log.info('Download queue empty')
        return

    def store_curl_pid(dl):
        remove_dlq(endpoint = unicode(dl.endpoint))
        append_dlq(endpoint = unicode(dl.endpoint),
                title = dl.file_name,
                media_hint = download['media_hint'],
                pid = dl.pid)

    def _update_library(dl):
        update_library(download['media_hint'])

    def clear_download_and_dispatch(dl):
        remove_dlq(dl.endpoint)
        dispatch(False)

    def store_download_endpoint(dl):
        append_history(dl.endpoint)

    def append_failed_download(dl):
        append_failed(endpoint = dl.endpoint,
                title = dl.wizard.file_hint or download['title'],
                media_hint = download['media_hint'])

    def clear_download_from_failed(dl):
        remove_failed(dl.endpoint)

    def perform_download():
        dest_key = '%s_destination' % download['media_hint']
        downloader = ss.Downloader(download['endpoint'],
            destination = settings.get(dest_key),
            limit       = speed_limit(),
            strategy    = strategy(),
            avoid_small_files = True
        )
        downloader.wizard.avoid_flv = avoid_flv()

        downloader.on_start(store_curl_pid)
        downloader.on_start(clear_download_from_failed)
        downloader.on_start(on_start)

        downloader.on_success(_update_library)
        downloader.on_success(store_download_endpoint)
        downloader.on_success(clear_download_and_dispatch)
        downloader.on_success(on_success)

        downloader.on_error(clear_download_from_failed)
        downloader.on_error(append_failed_download)
        downloader.on_error(clear_download_and_dispatch)
        downloader.on_error(on_error)

        downloader.download()

    set_current(download)

    if should_thread:
        thread.start_new_thread(perform_download, ())
    else:
        perform_download()

def pid_running(pid):
    if running_windows(): return pid_running_windows(pid)
    else:                 return signal_process_unix(pid)

def pid_running_windows(pid):
    import ctypes, ctypes.wintypes

    # GetExitCodeProcess uses a special exit code to indicate that the process is
    # still running.
    still_active = 259
    kernel32     = ctypes.windll.kernel32
    handle       = kernel32.OpenProcess(1, 0, pid)

    if handle == 0:
        return False

    # If the process exited recently, a pid may still exist for the handle.
    # So, check if we can get the exit code.
    exit_code  = ctypes.wintypes.DWORD()
    is_running = ( kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)) == 0 )
    kernel32.CloseHandle(handle)

    # See if we couldn't get the exit code or the exit code indicates that the
    # process is still running.
    return is_running or exit_code.value == still_active

def signal_process(pid, to_send = 0):
    if running_windows(): return signal_process_windows(pid, to_send)
    else:                 return signal_process_unix(pid, to_send)

def signal_process_unix(pid, to_send = 0):
    try:
        os.kill(pid, to_send)
        return True
    except:
        return False

def signal_process_windows(pid, to_send = 0):
    import ctypes

    try:
        # 1 == PROCESS_TERMINATE
        handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)
        ctypes.windll.kernel32.TerminateProcess(handle, to_send * -1)
        ctypes.windll.kernel32.CloseHandle(handle)
        return True
    except:
        return False



