#!/usr/bin/python

try:
    import safe
    import requests
    HAS_SAFEPY = True
except ImportError:
    HAS_SAFEPY = False


def main():
    module = AnsibleModule(
        argument_spec = dict(
            state = dict(required=True),
            view = dict(required=True),
        )
    )

    if not HAS_SAFEPY:
        module.fail_json(msg="safepy2 is not installed")

    try:
        api = safe.api('localhost')
    except requests.HTTPError as e:
        module.fail_json(msg=str(e))

    service, configuration = api.snmpd.service, api.snmpd.configuration
    status = service.status()['status_text']

    state = module.params['state']
    if state == 'started':
        configuration['assisted'] = 'true'
    elif state == 'stopped':
        configuration['assisted'] = 'false'

    if not any(api.snmpd.view.search({'oid': module.params['view']})):
        view_name = module.params['view']
        view_data = {'access': 'ro',
                     'oid': view_name,
                     'type': 'included'}
        api.snmpd.view.create('ansible-snmp', view_data)

    api.commit()

    if state == 'started' and status != 'RUNNING':
        service.start()
        module.exit_json(changed=True, state=state)
    elif state == 'stopped' and status == 'RUNNING':
        service.stop()
        module.exit_json(changed=True, state=state)
    else:
        module.exit_json(changed=False, state=state)


from ansible.module_utils.basic import *
main()
