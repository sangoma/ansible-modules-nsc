#!/usr/bin/python

try:
    import safe
    import requests
    HAS_SAFEPY = True
except ImportError:
    HAS_SAFEPY = False


def main():
    module = AnsibleModule(
        argument_spec=dict()
    )

    if not HAS_SAFEPY:
        module.fail_json(msg="safepy2 is not installed")

    try:
        api = safe.api('localhost')
    except requests.HTTPError as e:
        module.fail_json(msg=str(e))

    version = api.nsc.version.retrieve()
    version_facts = {'release': version['release_version'],
                     'major': version['major_version'],
                     'minor': version['minor_version'],
                     'patch': version['patch_version'],
                     'build': version['build_version']}

    facts = {'nsc_product_name': version['full_name'],
             'nsc_version': version_facts}
    module.exit_json(changes=False, ansible_facts=facts)


from ansible.module_utils.basic import *
main()
