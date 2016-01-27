#!/usr/bin/python

try:
    import safe
    import requests
    HAS_SAFEPY=True
except ImportError:
    HAS_SAFEPY=False


def build_profile(module, api):
    data = {}

    sip_ip = module.params.get('ip')
    if sip_ip:
        sip_obj = next(api.network.ip.search({'address': sip_ip}), None)
        if not sip_obj:
            module.fail_json(msg="Couldn't find {}".format(sip_ip))
        data['sip-ip'] = sip_obj.ident

    sip_port = module.params.get('port')
    if sip_port:
        data['sip-port'] = sip_port

    return data


def diff_dictionaries(d1, d2):
    overlap = d1.viewkeys() & d2.viewkeys()
    for key in overlap:
        if d1[key] != d2[key]:
            return True
    return False


def main():
    module = AnsibleModule(
        argument_spec = dict(
            name = dict(required=True),
            ip = dict(),
            port = dict(),
            state = dict(default='present')
        )
    )

    if not HAS_SAFEPY:
        module.fail_json(msg="safepy2 is not installed")

    try:
        api = safe.api('localhost')
    except requests.HTTPError as e:
        module.fail_json(msg=str(e))

    profile_name = module.params['name']
    profile_data = build_profile(module, api)

    current = api.sip.profile[profile_name]
    try:
        is_running = bool(current.status())
        current_data = current.retrieve()
    except safe.APIError as e:
        if e.response.status_code != 404:
            module.fail_json(msg="falied to query profile: {}".format(e))

        # If we get an exception its because the profile doesn't exist
        # on the product. We're free to create it.
        if module.params['state'] == 'present':
            try:
                api.sip.profile.create(profile_name, profile_data)
                api.commit()
                module.exit_json(changed=True)
            except safe.APIError as e:
                module.fail_json(msg="falied to create profile: {}".format(e))
    else:
        # Otherwise we have to consider if its either already running
        # or actually diffent to continue.
        if profile_data:
            diff = diff_dictionaries(current_data, profile_data)
            if diff:
                module.fail_json(msg="running profile has different data")

        if module.params['state'] == 'absent':
            try:
                if is_running:
                    current.stop()
                api.sip.profile.delete(profile_name)
                api.commit()
                module.exit_json(changed=True)
            except safe.APIError as e:
                module.fail_json(msg="falied to delete profile: {}".format(e))

    module.exit_json(changed=False)


from ansible.module_utils.basic import *
main()
