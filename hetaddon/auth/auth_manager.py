import atlassian_jwt
from hetaddon.models.model import TenantInfo, ExternalPlatform, User
import logging
import jwt

log = logging.getLogger('django')


class AuthManager(atlassian_jwt.Authenticator):

    def __init__(self):
        super(AuthManager, self).__init__()

    def get_shared_secret(self, client_key):
        tenant_info = TenantInfo.objects.filter(client_key=client_key)[0]

        if tenant_info is not None:
            return tenant_info.shared_secret
        return None

    @staticmethod
    def register_tenant(tenant_info_dict):

        existing_tenant_info = TenantInfo.objects.filter(client_key=tenant_info_dict["clientKey"])
        if len(existing_tenant_info) == 0:
            TenantInfo.objects.create(key=tenant_info_dict["key"],
                                      client_key=tenant_info_dict["clientKey"],
                                      shared_secret=tenant_info_dict["sharedSecret"])

    @staticmethod
    def authenticate_user(request, inside_atlassian):

        if not inside_atlassian:  # skip authentication and set the session for the mocked user (from data.py)
            user = User.objects.get(externalplatform__user_ext_id='admin')
            user_mock_context = {"displayName": user.name, "userKey": "admin"}
            print("mocking user session for user:" + str(user))
            request.session['user'] = user_mock_context
            return

        auth_manager = AuthManager()
        try:
            client_key = auth_manager.authenticate(request.method, request.get_full_path())
            log.info("Client was successfully authenticated. Client key:" + client_key)
            jwt_token = request.GET.get('jwt', '')
            decoded_token = jwt.decode(jwt_token, verify=False)  # no need for verification - already done
            user_context_dict = decoded_token["context"]["user"]
            log.info("Found user context:" + str(user_context_dict))

            atl_platform_records = ExternalPlatform.objects.filter(platform_name='atl')
            ext_user = atl_platform_records.filter(user_ext_id=user_context_dict["userKey"])
            if len(ext_user) > 0:
                log.info("User recognized:" + str(ext_user[0]))
            else:
                log.info("User unknown. Creating new user record.")
                new_user = User.objects.create(name=user_context_dict["displayName"], email='')
                ExternalPlatform.objects.create(platform_name='atl',
                                                user_ext_id=user_context_dict["userKey"],
                                                user=new_user)

            request.session['user'] = user_context_dict

        except atlassian_jwt.DecodeError:
            log.error("Authentication failed!")
            pass
