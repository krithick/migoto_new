from src.domain.common.exceptions import DomainException

class AvatarInteractionDomainException(DomainException):
    """Base exception for AvatarInteraction Domain """

class InvalidModeException(AvatarInteractionDomainException):
    """ Invalid Mode """