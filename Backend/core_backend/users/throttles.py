from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


"""Unauthorized users limits"""


class RegisterRateThrottle(AnonRateThrottle):
    scope = "register"


class LoginRateThrottle(AnonRateThrottle):
    scope = "login"


class VerifyEmailRateThrottle(AnonRateThrottle):
    scope = "verify_email"


class ResendVerifyRateThrottle(AnonRateThrottle):
    scope = "resend_verify"


class PasswordResetRequestRateThrottle(AnonRateThrottle):
    scope = "password_reset_request"


class PasswordResetConfirmRateThrottle(AnonRateThrottle):
    scope = "password_reset_confirm"


"""Authorized users limits"""


class ChangePasswordRateThrottle(UserRateThrottle):
    scope = "change_password"


class UserMeRateThrottle(UserRateThrottle):
    scope = "user_me"
