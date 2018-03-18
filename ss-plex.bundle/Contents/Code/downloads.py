FEATURE_PREFIX = '%s/downloads' % consts.prefix

@route(FEATURE_PREFIX)
def MainMenu(refresh = 0):
    container = container_for('heading.download', no_cache = True)

    if bridge.download.assumed_running():
        bridge.download.check_queue()	
        for download in bridge.download.dlq():
            if download['pid']: 

                status   = ss.downloader.status_for(download['endpoint'], strategy = bridge.download.strategy())

                container.add(popup_button(download['title'], OptionsForCurrent,
                endpoint = download['endpoint'], icon = 'icon-downloads.png'))

                for ln in status.report():
                    container.add(popup_button('- %s' % ln, OptionsForCurrent,
                    endpoint = download['endpoint'], icon = 'icon-downloads.png'))
            else: 
                container.add(popup_button('Processing...' + download['title'], OptionsForCurrent,
                endpoint = download['endpoint'], icon = 'icon-downloads.png'))

    for download in bridge.download.queue():
        container.add(popup_button(download['title'], OptionsForQueue,
            endpoint = download['endpoint'], icon = 'icon-downloads-queue.png'))

    for download in bridge.download.failed():
        container.add(popup_button(download['title'], OptionsForFailed,
            endpoint = download['endpoint'], icon = 'icon-downloads-failed.png'))

    add_refresh_to(container, refresh, MainMenu)
    return container

@route('%s/options-for-endpoint' % FEATURE_PREFIX)
def OptionsForEndpoint(endpoint):
    if bridge.download.is_current(endpoint):
        return OptionsForCurrent(endpoint)

    queued = bridge.download.from_queue(endpoint)
    if queued: return OptionsForQueue(endpoint)

    failed = bridge.download.from_failed(endpoint)
    if failed: return OptionsForFailed(endpoint)

    return dialog('heading.error', F('download.response.not-found', endpoint))

@route('%s/options-for-current' % FEATURE_PREFIX)
def OptionsForCurrent(endpoint):
    download  = bridge.download.current(endpoint)
    if not download:
        return dialog('heading.error', F('download.response.not-found', endpoint))

    container = container_for(download['title'], no_cache = True)

    if download['pid'] and bridge.download.curl_running(download['pid']):
        container.add(button('download.heading.next', NextSource, endpoint = endpoint, pid = download['pid']))
        container.add(button('download.heading.cancel', RemoveCurrent, endpoint = endpoint, pid = download['pid']))
    else:
        container.add(button('download.heading.force-success', ForceSuccess, endpoint = endpoint))
        container.add(button('download.heading.force-failure', ForceFailure, endpoint = endpoint))

    return container

@route('%s/options-for-queue' % FEATURE_PREFIX)
def OptionsForQueue(endpoint):
    download = bridge.download.from_queue(endpoint)
    if not download:
        return dialog('heading.error', F('download.response.not-found', endpoint))

    container = container_for(download['title'], no_cache = True)
    cancel_button = button('download.heading.cancel', Remove, endpoint = endpoint)
    container.add(cancel_button)

    return container

@route('%s/options-for-failed' % FEATURE_PREFIX)
def OptionsForFailed(endpoint):
    download = bridge.download.from_failed(endpoint)
    if not download:
        return dialog('heading.error', F('download.response.not-found', endpoint))

    container     = container_for(download['title'], no_cache = True)
    cancel_button = button('download.heading.cancel', RemoveFailed, endpoint = endpoint)
    retry_button  = button('download.heading.retry', Queue,
        endpoint   = download['endpoint'],
        media_hint = download['media_hint'],
        title      = download['title'],
        icon       = 'icon-downloads-queue.png'
    )

    container.add(retry_button)
    container.add(cancel_button)

    return container

@route('%s/queue' % FEATURE_PREFIX)
def Queue(endpoint, media_hint, title):
    if bridge.download.was_successful(endpoint):
        message = 'exists'
    else:
        slog.info('Adding %s %s to download queue' % (media_hint, title))
        message = 'added'
        bridge.download.remove_failed(endpoint = endpoint)
        bridge.download.append(title = title, endpoint = endpoint, media_hint = media_hint)

    bridge.download.dispatch()
    return dialog('heading.download', F('download.response.%s' % message, title))

@route('%s/dispatch' % FEATURE_PREFIX)
def Dispatch():
    bridge.download.dispatch()

@route('%s/dispatch/force' % FEATURE_PREFIX)
def DispatchForce():
    slog.warning('Repairing downloads')
    bridge.download.clear_current()
    bridge.download.dispatch()

@route('%s/force-success' % FEATURE_PREFIX)
def ForceSuccess(endpoint):
    bridge.download.force_success(endpoint)
    return dialog('heading.download', 'download.response.force-success')

@route('%s/force-failure' % FEATURE_PREFIX)
def ForceFailure(endpoint):
    bridge.download.force_failure(endpoint)
    return dialog('heading.download', 'download.response.force-failure')

@route('%s/next' % FEATURE_PREFIX)
def NextSource(endpoint, pid):
    bridge.download.command('next', endpoint, int(pid))
    return dialog('heading.download', 'download.response.next')

@route('%s/remove' % FEATURE_PREFIX)
def Remove(endpoint):
    download = bridge.download.from_queue(endpoint)
    if not download:
        return dialog('heading.error', F('download.response.not-found', endpoint))

    bridge.download.remove(endpoint)
    return dialog('heading.download',
            F('download.response.cancel', download['title']))

@route('%s/remove-failed' % FEATURE_PREFIX)
def RemoveFailed(endpoint):
    download = bridge.download.from_failed(endpoint)

    if not download:
        return dialog('heading.error',
                F('download.response.not-found', endpoint))

    bridge.download.remove_failed(endpoint)
    return dialog('heading.download', 'download.response.remove-failed')

@route('%s/remove-current' % FEATURE_PREFIX)
def RemoveCurrent(endpoint, pid):
    download = bridge.download.current(endpoint)
    bridge.download.command('cancel', endpoint, int(pid))

    return dialog('heading.download',
            F('download.response.cancel', download['title']))

