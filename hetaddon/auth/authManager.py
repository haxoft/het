import atlassian_jwt
from hetaddon.models import TenantInfo


class AuthManager(atlassian_jwt.Authenticator):

    def __init__(self):
        super(AuthManager, self).__init__()

    @staticmethod
    def register_tenant(tenant_info_dict):

        existing_tenant_info = TenantInfo.objects.filter(client_key=tenant_info_dict["clientKey"])
        if len(existing_tenant_info) == 0:
            TenantInfo.objects.create(key=tenant_info_dict["key"],
                                      client_key=tenant_info_dict["clientKey"],
                                      shared_secret=tenant_info_dict["sharedSecret"])

    def get_shared_secret(self, client_key):
        tenant_info = TenantInfo.objects.filter(client_key=client_key)[0]

        if tenant_info is not None:
            return tenant_info.shared_secret
        return None
