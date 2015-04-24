## ansible-modules-nsc

More of a proof-of-concept than anything else at the moment. Requires
`delegated_to` to point to a machine where the [sangoma/safepy][1]
library is installed. Hopefully in the future we'll ship it with our
products simplifying this significantly.

### Usage

To demo this support, check out this repository and add the resulting directory
to the [`ANSIBLE_LIBRARY`][2] environmental variable.

Then a task like this should work inside your ansible script:

~~~yaml
---
- name: Demo sip profile
  local_action: >
    nsc_profile host={{ inventory_hostname }}
    name=ansible-demo-profile
    ip={{ ansible_default_ipv4.address }}
    port=5060
~~~

Hopefully a profile should be created. Still rough, still needs to
support stuff like `state=started` and other profile fields.
Eventually should expand to support stuff like trunks, dialplans, and
other features.

Feel free to request features/fixes.

  [1]: https://github.com/sangoma/safepy
  [2]: http://docs.ansible.com/developing_modules.html#module-paths
