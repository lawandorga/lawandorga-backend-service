from core.auth.use_cases.keys import check_keys
from core.auth.use_cases.matrix_user import create_matrix_user
from core.auth.use_cases.rlc_user import (
    activate_rlc_user,
    delete_user,
    unlock_myself,
    unlock_user,
    update_frontend_settings,
    update_user_data,
)
from core.auth.use_cases.user import change_password_of_user

USECASES = {
    "auth/change_password": change_password_of_user,
    "auth/delete_user": delete_user,
    # "auth/confirm_email": confirm_email,
    "auth/unlock_user": unlock_user,
    # "auth/create_mfa_secret": create_mfa_secret,
    # "auth/enable_mfa_secret": enable_mfa_secret,
    # "auth/delete_mfa_secret": delete_mfa_secret,
    "auth/create_matrix_user": create_matrix_user,
    "auth/unlock_myself": unlock_myself,
    "auth/test_keys": check_keys,
    "auth/update_frontend_settings": update_frontend_settings,
    "auth/activate_user": activate_rlc_user,
    "auth/update_user_data": update_user_data,
}
