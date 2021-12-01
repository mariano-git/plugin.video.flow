import pprint
from typing import List

import requests as requests

from ext.util import ModelHelper, isBlank
from ext.util.logger import Logger
from ext.ws.rs import NotAuthorizedException
from ext.ws.rs.client import Client, ClientRequestContext, ClientResponseContext
from ext.ws.rs.core import MediaType, Response
from ext.ws.rs.ext import ApiModel, RuntimeDelegate


class PiggyInvoker:
    def __init__(self, client: Client):
        self.client: Client = client
        self.apiModel: ApiModel = RuntimeDelegate().apimodel

    def getURL(self, elements):
        uri = self.client.webTarget.targetUri
        slash = '/'
        remove = ''
        if 'http://' in uri.lower():
            remove = 'http://'
        elif 'https://' in uri.lower():
            remove = 'https://'

        uri = uri.replace(remove, '')
        parts = uri.split(slash)
        segments = []
        for p in parts:
            segments.append(p)

        for e in elements:
            u = self.apiModel.get(e, 'path') or ''
            parts = u.split(slash)
            for p in parts:
                segments.append(p)

        uri = f"{remove}{slash.join(segments)}"

        return uri

    def buildHeaders(self, apiNode, callNode, **kwargs):
        # produces -> Accept
        # consumes -> Content-type

        apiProduces = self.apiModel.get(apiNode, 'produces')
        apiConsumes = self.apiModel.get(apiNode, 'produces')
        callProduces = self.apiModel.get(callNode, 'produces')
        callConsumes = self.apiModel.get(callNode, 'consumes')

        accept_header = apiProduces if callProduces is None else callProduces
        content_header = apiConsumes if callConsumes is None else callConsumes
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                                 'Chrome/94.0.4606.81 Safari/537.36 ',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'en-US,en;q=0.9,es;q=0.8'}

        if not isBlank(accept_header):
            headers['Accept'] = accept_header  # f"{accept_header}, text/plain, */*"
        else:
            headers['Accept'] = 'application/json, text/plain, */*'

        if not isBlank(content_header):
            headers['Content-Type'] = content_header
        else:
            headers['Content-Type'] = None

        # we may have extra arbitrary headers and we must honor that
        # very rough implementation
        apiHeaders = self.apiModel.get(apiNode, 'headers')
        callHeaders = self.apiModel.get(callNode, 'headers')
        if apiHeaders is not None:
            for key, value in apiHeaders.items():
                headers[key] = value
        if callHeaders is not None:
            for key, value in callHeaders.items():
                headers[key] = value

        Logger.debug(pprint.pformat(headers, indent=4))

        return headers

    def buildQuery(self, callNode, **kwargs):
        query_params = {}
        parameters = self.apiModel.get(callNode, 'parameters')
        if not parameters or 'QueryParam' not in parameters:
            return None
        params = parameters['QueryParam']
        for param in params:
            query_params[param['as']] = kwargs[param['name']] if param['name'] in kwargs else param['default']
        return query_params

    def buildBody(self, callNode, **kwargs):
        body_param = None
        parameters = self.apiModel.get(callNode, 'parameters')
        if not parameters:
            return None
        params = self.apiModel.get(parameters, 'BeanParam')
        if not params:
            params = self.apiModel.get(parameters, 'Schema')
        if not params:
            return None
        for param in params:
            value = kwargs[param['name']]
            # FIXME
            # if type(value).__name__ != 'list':
            #    return value
            # else:
            return value

        return body_param

    def notifyFilters(self, requestContext: ClientRequestContext, responseContext: ClientResponseContext = None):
        for f in self.client.filters:
            f.filter(requestContext, responseContext)

    def handleError(self, cause):
        Logger.log_error(f"{cause} \n {cause.response.json()}")

        response = cause.response
        rsResponse: Response = Response(response)
        if response.status_code >= 401 or response.status_code <= 403:
            raise NotAuthorizedException(message="Not Authorized", cause=cause, response=rsResponse)

    def execute(self, api, call, kwargs):

        Logger.debug(f"execute api: {api} call: {call} kwargs: {kwargs}")
        from http.client import HTTPConnection  # py3
        HTTPConnection.debuglevel = 1

        # self.apiModel.dump()

        apiNode = self.apiModel.getApi(api)
        callNode = self.apiModel.get(apiNode, call)
        requestNode = self.apiModel.get(callNode, 'request')
        responseNode = self.apiModel.get(callNode, 'response')

        # self.method = method
        # self.url = url
        # self.headers = headers
        # self.files = files
        # self.data = data
        # self.json = json
        # self.params = params
        # self.auth = auth
        # self.cookies = cookies

        headers = self.buildHeaders(apiNode, callNode, **kwargs)
        query = self.buildQuery(requestNode, **kwargs)
        body = self.buildBody(requestNode, **kwargs)
        method = self.apiModel.get(callNode, 'method')
        # FIXME to implement
        form = {}

        url = self.getURL([apiNode, callNode])

        requestContext = ClientRequestContext(method, url, headers, query, body)
        if len(self.client.filters) > 0:
            self.notifyFilters(requestContext)

        try:
            # method, url, params=params, data=form, headers=headers, json=body
            if isinstance(body, ModelHelper):
                body = body.to_dict()

            response = requests.request(method=method, url=url, headers=headers, params=query, data=form, json=body)

            response.raise_for_status()

            payload = response.json()
            results = {}

            respType = response.headers.get('Content-type')
            if MediaType.TEXT_PLAIN in respType:
                results = payload
            elif MediaType.APPLICATION_JSON in respType:
                if isinstance(payload, List):
                    results = responseNode['type'](payload)
                elif isinstance(payload, (int, float, bool)):
                    results = payload
                else:
                    results = responseNode['type'](**payload)

            responseContext: ClientResponseContext = ClientResponseContext(
                response.status_code,
                response.headers,
                results
            )

            if len(self.client.filters) > 0:
                self.notifyFilters(requestContext, responseContext)

            return results
            # Code here will only run if the request is successful
        except requests.exceptions.HTTPError as errh:
            self.handleError(errh)
        except requests.exceptions.ConnectionError as errc:
            self.handleError(errc)
        except requests.exceptions.Timeout as errt:
            self.handleError(errt)
        except requests.exceptions.RequestException as err:
            self.handleError(err)
