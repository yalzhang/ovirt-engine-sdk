#
# Copyright (c) 2010 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#           http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from ovirtsdk.xml import params
import types

class ERROR(Exception):
    def __init__(self, content):
        Exception.__init__(self, content)

class ConnectionError(Exception):
    def __init__(self, expect):
        Exception.__init__(self, '[ERROR]::oVirt API connection failure, %s' % expect)

class NoCertificatesError(Exception):
    def __init__(self):
        Exception.__init__(self, '[ERROR]::key_file, cert_file, ca_file must be specified for SSL connection.')

class RequestError(Exception):
    def __init__(self, response):
        self.detail = None
        self.status = None
        self.reason = None
        res = response.read()
        detail = ''
        RESPONSE_FORMAT = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        RESPONSE_FAULT_BODY = '<fault>'
        APP_SERVER_RESPONSE_FORMAT = '<html><head><title>JBoss Web'

        #REST error
        if res and res.startswith(RESPONSE_FORMAT) and res.find(RESPONSE_FAULT_BODY) != -1:
            try:
                f_detail = params.parseString(res)
            except:
                f_detail = ''

            if types.StringType != type(f_detail):
                if isinstance(f_detail, params.Action) and f_detail.fault is not None:
                    #self.reason = f_detail.fault.reason
                    detail = f_detail.fault.detail.lstrip()
                else:
                    #self.reason = response.reason
                    if f_detail is not None:
                        detail = f_detail.detail.lstrip()

                #engine returns can-do-action error messages with brackets
                if detail.startswith('[') and detail.endswith(']'):
                    detail = detail[1:len(detail) - 1]

        #application server error
        elif res.startswith(APP_SERVER_RESPONSE_FORMAT):
            detail = res
            start = detail.find('<h1>')
            end = detail.find('</h1>')
            if start != -1 and end != -1:
                detail = detail[start:end].replace('<h1>', '').replace('</h1>', '')
                if detail and detail.endswith(' - '):
                    detail = detail[:len(detail) - 3]
        else:
            detail = '\n' + res if res else ''

        self.detail = detail
        self.reason = response.reason
        self.status = response.status

        Exception.__init__(self, '[ERROR]::oVirt API request failure.' + self.__str__())

    def __str__(self):
        return '\r\nstatus: ' + str(self.status) + '\r\nreason: ' + self.reason + '\r\ndetail: ' + str(self.detail)

class ImmutableError(Exception):
    def __init__(self, key):
        Exception.__init__(self, '[ERROR]::\'%s\' is immutable.' % key)
