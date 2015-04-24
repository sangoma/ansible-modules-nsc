#!/usr/bin/python

try:
    import safe
    import requests
    HAS_SAFEPY=True
except ImportError:
    HAS_SAFEPY=False


def main():
    module = AnsibleModule(
        argument_spec = dict(
            host = dict(required=True),
            state = dict(required=True),
        )
    )

    if not HAS_SAFEPY:
        module.fail_json(msg="safepy2 is not installed")

    with safe.api(module.params['host']) as api:
        service, configuration = api.snmpd.service, api.snmpd.configuration
        status = service.status()['status_text']

        state = module.params['state']
        if state == 'started':
            configuration['assisted'] = 'true'
        elif state == 'stopped':
            configuration['assisted'] = 'false'

    if state == 'started' and status != 'RUNNING':
        service.start()
        module.exit_json(changed=True, state=state)
    elif state == 'stopped' and status == 'RUNNING':
        service.stop()
        module.exit_json(changed=True, state=state)
    module.exit_json(changed=False, state=state)


from ansible.module_utils.basic import *
main()
