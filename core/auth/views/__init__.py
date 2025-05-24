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
    LegalRequirementView,
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
    "LegalRequirementView",
    "MfaDisableView",
    "MfaEnableView",
    "MfaLoginView",
    "MfaSetupView",
    "MfaStatusView",
]
