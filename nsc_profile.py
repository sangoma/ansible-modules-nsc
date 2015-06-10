#!/usr/bin/python

try:
    import safe
    import requests
    HAS_SAFEPY=True
except ImportError:
    HAS_SAFEPY=False


def get_network_ip(module, api):
    obj = api.network.ip.list({'address': module.params['ip']})
    if not obj:
        module.fail_json(msg="Provided ip does not exist on the device")
    return obj[0]


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
        module.fail_json(msg="safepy2 is not installed")

    with safe.api(module.params['host']) as api:
        profile_name = module.params['name']
        profile_data = {'sip-ip': get_network_ip(module, api),
                        'sip-port': str(module.params['port'])}

        current = api.sip.profile[profile_name]
        try:
            current_status = bool(current.status())
            current_data = current.retrieve()
        except requests.HTTPError as e:
            if e.response.status_code != 404:
                module.fail_json(msg="falied to query profile")

            try:
                # If we get an exception its because the profile doesn't
                # exist on the product. We're free to create it.
                api.sip.profile.create(profile_name, profile_data)
            except requests.HTTPError:
                module.fail_json(msg="falied to create profile")
        else:
            # Otherwise we have to consider if its either already
            # running or actually different to continue.
            differ = dicts_differ(current_data, profile_data)
            if not differ:
                module.exit_json(changed=False)
            elif current_status and differ:
                module.fail_json(msg="incompatable profile already started")

            try:
                current.update(profile_data)
            except requests.HTTPError as e:
                module.fail_json(msg="falied to update profile")

    module.exit_json(changed=True)


from ansible.module_utils.basic import *
main()
