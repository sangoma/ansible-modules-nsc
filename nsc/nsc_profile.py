try:
    import safepy
    import requests
    HAS_SAFEPY=True
except ImportError:
    HAS_SAFEPY=False


def get_network_ip(module, api):
    obj = api.network.ip.list({'address': module.params['ip']})
    if not obj:         
        module.fail_json(msg="Provided ip does not exist on the device")
    return obj[0]


def get_api(module):
    return safepy.api(module.params['host'])


def dicts_differ(d1, d2):
    overlap = d1.viewkeys() & d2.viewkeys()
    for key in overlap:
        if d1[key] != d2[key]:
            return True
    return False


def main():
    module = AnsibleModule(
        argument_spec = dict(
            host = dict(required=True),
            name = dict(required=True),
            ip = dict(required=True),
            port = dict(required=True)
        )
    )

    if not HAS_SAFEPY:
        module.fail_json(msg="safepy is not installed")

    with get_api(module) as api:
        profile_name = module.params['name']
        profile_data = {'sip-ip': get_network_ip(module, api),
                        'sip-port': module.params['port']}

        current = api.sip.profile[profile_name]
        try:
            current_status = bool(current.status())
            current_data = current.retrieve()
        except requests.HTTPError:
            # If we get an exception its because the profile doesn't
            # exist on the product. We're free to create it.
            api.sip.profile.create(profile_name, profile_data)
        else:
            # Otherwise we have to consider if its either already
            # running or actually different to continue.
            differ = dicts_differ(current_data, profile_data)
            if not differ:
                module.exit_json(changed=False)
            elif current_status and differ:
                module.fail_json(msg="Incompatable profile already started")

            current.update(profile_data)

    module.exit_json(changed=True)


from ansible.module_utils.basic import *
main()
