from oidc_provider.lib.claims import ScopeClaims
from .models import UserProfile


def userinfo(claims, user):
    # Fill a generic dict of user information
    # All available keys can be found in oidc_provider.lib.claims.STANDARD_CLAIMS
    claims['name'] = user.name
    claims['email'] = user.email
    return claims


class RlcScopeClaims(ScopeClaims):
    # Since we need some more specific information, we implement a custom scope "rlc".
    # It contains some of the claims from userinfo (name, email), but additional claims
    # that are not in the list of standard claims (identifier, rlc).

    info_rlc = (
        'RLC profile',
        'Information required for matrix server',
    )

    def scope_rlc(self):
        try:
            dic = {
                    'matrix_localpart': self.user.matrix_user.id,
                    'name': self.userinfo['name'],
                    'email': self.userinfo['email'],
                    'rlc': self.user.matrix_user.group,
            }
            return dic
        except UserProfile.matrix_user.RelatedObjectDoesNotExist:
            return ''
