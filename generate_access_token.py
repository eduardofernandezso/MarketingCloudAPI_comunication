def generate_access_token(clientid: str, clientsecret: str) -> str:
    subdomain = 'mcc*********************'
    auth_base_url = f'https://{subdomain}.auth.marketingcloudapis.com/v2/token'
    headers = {'content-type': 'application/json'}
    payload = {
      'grant_type': 'client_credentials',
      'client_id': f'{clientid}',
      'client_secret':  f'{clientsecret}'
    }
    authentication_response = requests.post(
        url=auth_base_url, data=json.dumps(payload), headers=headers
    ).json()

    if 'access_token' not in authentication_response:
        raise Exception(
          f'Unable to validate (ClientID/ClientSecret): {repr(authentication_response)}'
        )
    access_token = authentication_response['access_token']
    expires_in = time() + authentication_response['expires_in']

    stubObj = FuelSDK.ET_Client(
      False, False,
      {
          'clientid': f'{clientid}',
          'clientsecret': f'{clientsecret}',
          'defaultwsdl': f'https://{subdomain}.soap.marketingcloudapis.com/etframework.wsdl',
          'authenticationurl': f'https://{subdomain}.auth.marketingcloudapis.com',
          'baseapiurl': f'https://{subdomain}.rest.marketingcloudapis.com',
          'soapendpoint': f'https://f{subdomain}.soap.marketingcloudapis.com',
          'useOAuth2Authentication': 'True',
          'applicationType': 'server'

      })
    return access_token, expires_in, stubObj
