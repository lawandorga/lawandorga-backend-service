from .mfa import (
    MfaDisableView,
    MfaEnableView,
    MfaLoginView,
    MfaSetupView,
    MfaStatusView,
)
from .user import (
    CustomLoginView,
    CustomLogoutView,
    CustomPasswordResetCompleteView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetDoneView,
    CustomPasswordResetView,
    CustomRegisterDoneView,
    CustomRegisterView,
)

__all__ = [
    "CustomLoginView",
    "CustomLogoutView",
    "CustomPasswordResetCompleteView",
    "CustomPasswordResetConfirmView",
    "CustomPasswordResetDoneView",
    "CustomPasswordResetView",
    "CustomRegisterDoneView",
    "CustomRegisterView",
    "MfaDisableView",
    "MfaEnableView",
    "MfaLoginView",
    "MfaSetupView",
    "MfaStatusView",
]
