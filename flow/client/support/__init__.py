from piggy.base.notation import Target, ElementType
from ws.rs.namebinding import NameBinding


@NameBinding
@Target({ElementType.TYPE, ElementType.METHOD})
class JwtAuthentication:
    pass


@NameBinding
@Target({ElementType.TYPE, ElementType.METHOD})
class PrmAuthentication:
    pass
