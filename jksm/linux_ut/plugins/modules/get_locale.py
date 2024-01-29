#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
---
module: get_locale
short_description: Get System Locale Information
description:
- Get System Locale Information and Return Them as structured Data(json format)
options: {}
seealso:
- module: ansilbe.builtin.debug
author:
- jumpei kasama (@jkasama)
version_added: 0.1.0
requirements:
- python >= 3.9
- ansible >= 2.11
notes:
- Tested on RHEL9.2
"""

EXAMPLES = r"""
---
- jks.linux_ut.get_locale:
"""

RETURN = r"""
---
system_locale:
  type: str
  description: Default System Locale
  returned: success
language_code:
  type: str
  description: Language Code
  returned: On success
locale_detail:
  type: dict
  description: System Locale Detail Information
  returned: success
available_locales:
  type: list
  description: List of Available Locales in target systems. (localectl list-locales commands outputs)
  returned: success
"""

from ansible.module_utils.basic import AnsibleModule
from locale import getlocale

import asyncio
import subprocess


async def get_available_locales(str_code):
    try:
        comm_result = subprocess.run(["localectl", "list-locales"], capture_output=True, check=True)
    except subprocess.CalledProcessError as err:
        return None

    try:
        std_out = comm_result.stdout.decode(str_code)
    except UnicodeError as err:
        raise err("Decoding Stdout Failed During Get Available Locale List.")
    except Exception as err:
        raise err("Unexpected Error Occured During Get Available Details.")

    return std_out.splitlines()


async def get_locale_details(str_code):
    try:
        comm_result = subprocess.run(["locale"], capture_output=True, check=True)
    except subprocess.CalledProcessError as err:
        return None

    try:
        std_out = comm_result.stdout.decode(str_code)
    except UnicodeError as err:
        raise err("Decode Command Result Failed During Get Locale Details.")
    except Exception as err:
        raise err("Unexpected Error Occured During Get Locale Details.")

    fields = std_out.splitlines()
    result = {}
    for field in fields:
        key = field.split("=")[0]
        value = field.split("=")[1]
        result.update({
            key: value
        })

    return result


async def gather_commands_coroutines(str_code):
    func_list = [
        get_available_locales(str_code),
        get_locale_details(str_code)
    ]

    return await asyncio.gather(*func_list)


async def main():
    argument_spec = {}
    module = AnsibleModule(
        argument_spec=argument_spec,
    )

    system_locale = getlocale()
    if system_locale is None:
        result = {
            "msg": "Get System Locale Failed.",
            "changed": False
        }
        module.fail_json(**result)
    elif len(system_locale) != 2:
        result = {
            "msg": "Get System Locale or Language Code Failed",
            "changed": False
        }
        module.fail_json(**result)
    else:
        language_code = system_locale[0]
        locale = system_locale[1]

    result = {
        "system_locale": locale,
        "language_code": language_code,
    }

    command_result_list = await gather_commands_coroutines(system_locale)
    result.update({
        "changed": False,
        "message": "Gather Loales Infomations End Successfully.",
        "available_locales": command_result_list[0],
        "locale_details": command_result_list[1]
    })

    return result


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
