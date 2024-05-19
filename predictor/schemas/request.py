from pydantic import BaseModel


class BidRequest(BaseModel):
    id: str
    hour: str
    C1: str
    banner_pos: str
    site_id: str
    site_domain: str
    site_category: str
    app_id: str
    app_domain: str
    app_category: str
    device_id: str
    device_ip: str
    device_model: str
    device_type: str
    device_conn_type: str
    C14: str
    C15: str
    C16: str
    C17: str
    C18: str
    C19: str
    C20: str
    C21: str
