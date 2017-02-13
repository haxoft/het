import atlassian_jwt


class AuthManager(atlassian_jwt.Authenticator):
    def __init__(self, tenant_info_store):
        super(AuthManager, self).__init__()
        self.tenant_info_store = tenant_info_store

    def get_shared_secret(self, client_key):
        tenant_info = self.tenant_info_store.get(client_key)
        return tenant_info['sharedSecret']

    def get_tenant_info_store(self):
        return self.tenant_info_store


def test_auth(tenant_info_store):

    my_auth = AuthManager(tenant_info_store)
    return None
    # try:
    #     client_key = my_auth.authenticate(http_method, url, headers)
    #     # authentication succeeded
    # except atlassian_jwt.DecodeError:
    #     # authentication failed
    #     pass
