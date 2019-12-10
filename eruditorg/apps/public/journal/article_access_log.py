from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from typing import Optional


class AccessType(Enum):
    # html
    html_preview = "html_preview"
    html_full_view = "html_full_view"
    html_preview_pdf_embedded = "html_preview_pdf_embedded"
    html_full_view_pdf_embedded = "html_full_view_pdf_embedded"
    html_biblio = "html_biblio"
    html_toc = "html_toc"

    # pdf
    pdf_preview = "pdf_preview"
    pdf_full_view = "pdf_full_view"
    pdf_preview_embedded = "pdf_preview_embedded"
    pdf_full_view_embedded = "pdf_full_view_embedded"

    # xml
    xml_full_view = "xml_full_view"

    # content not available
    content_not_available = "content_not_available"


class ArticleAccessLog(BaseModel):
    version: str = "1"

    # apache
    timestamp: datetime
    accessed_uri: str
    ip: str
    protocol: str
    user_agent: str
    referer: str
    subscriber_referer: str

    # article info
    article_id: str
    article_full_pid: str

    # subscription info
    subscriber_id: Optional[int]
    is_subscribed_to_journal: bool

    # access info
    access_type: AccessType
    is_access_granted: bool
    is_issue_embargoed: bool
    is_journal_open_access: bool

    # user info
    session_key: str
    username: str
