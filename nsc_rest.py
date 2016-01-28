#!/usr/bin/python

try:
    import safe
    import requests
    HAS_SAFEPY = True
except ImportError:
    HAS_SAFEPY = False


def diff_dictionaries(d1, d2):
    for key in d1.viewkeys() & d2.viewkeys():
        if d1[key] != d2[key]:
            return True
    return False


def main():
    module = AnsibleModule(
        argument_spec = dict(
            apikey = dict(),
            description = dict()
        )
    )

    if not HAS_SAFEPY:
        module.fail_json(msg="safepy2 is not installed")

    try:
        api = safe.api('localhost')
    except safe.APIError as e:
        module.fail_json(msg=str(e))

    configuration = {'ip-whitelist': 'false'}

    changed = False
    apikey = module.params['apikey']

    if not apikey:
        configuration['enable'] = 'false'
    else:
        configuration['enable'] = 'true'
        configuration['api-key'] = 'true'
        new_apikey = {'key': apikey}

        description = module.params['description']
        if description:
            new_apikey['description'] = description

        try:
            old_apikey = api.rest.apikey.retrieve('ansible-key')
        except safe.APIError as e:
            if e.response.status_code != 404:
                module.fail_json(msg="falied to query apikey: {}".format(e))

            api.rest.apikey.create('ansible-key', new_apikey)
            changed = True
        else:
            if old_apikey != new_apikey:
                module.fail_json(msg="conflicting api key present".format(e))

    if diff_dictionaries(api.rest.configuration.retrieve(), configuration):
        api.rest.configuration.update(configuration)
        changed = True

    try:
        api.commit()
    except safe.APIError as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=changed)


from ansible.module_utils.basic import *
main()
