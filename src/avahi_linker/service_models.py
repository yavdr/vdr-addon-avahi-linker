from pydantic import BaseModel, IPvAnyAddress, validator
from typing import NamedTuple
import avahi

class AvahiAnnouncement(NamedTuple):
    interface: int
    protocol: int
    name: str
    service_type: str
    domain: str
    flags: int

    def is_local(self):
        return bool(self.flags & avahi.LOOKUP_RESULT_LOCAL)

class ResolvedService(BaseModel):
    interface: int
    protocol: int
    name: str
    service_type: str
    domain: str
    host: str
    aprotocol: int
    address: IPvAnyAddress
    port: int
    payload: dict[str, str]
    flags: int

    @property
    def sharename(self):
        return f"{self.name} on {self.host}"
    
    @property
    def extended_sharename(self):
        return f"{self.sharename}: {self.payload}"

    @validator("payload", pre=True)
    def extract_payload(cls, v):
        d = dict(e.decode().split("=", maxsplit=1) for e in v)
        assert "path" in d, f"missing attribute 'path' in {d}"
        assert "subtype" in d, f"missing attribute 'subtype' in {d}"
        return d