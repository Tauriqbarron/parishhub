"""Listmonk email provider — N12 (#320).

Skeleton provider that will integrate with the listmonk API once deployed (N11).
For now, logs email details and marks deliveries as 'sent'.

Full integration will:
- POST to listmonk /api/tx endpoint for transactional email
- Handle API key auth via headers
- Parse response for delivery status
"""

import logging
from typing import Optional

logger = logging.getLogger("parish.providers.listmonk")


class ListmonkProvider:
    """Email delivery via self-hosted Listmonk.

    This is a stub that will be connected to the real listmonk API
    when the listmonk deployment (N11) is complete.
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self._configured = bool(base_url and api_key)

    def send(self, to_email: str, subject: str, body_html: str) -> dict:
        """Send a transactional email.

        Args:
            to_email: Recipient email address.
            subject: Email subject line.
            body_html: HTML body content.

        Returns:
            dict with keys: status, provider, message
        """
        if not self._configured:
            logger.info(
                "listmonk_stub_send: to=%s subject=%r body_len=%d — "
                "not configured (no base_url/api_key), marking as sent",
                to_email,
                subject,
                len(body_html),
            )
        else:
            logger.info(
                "listmonk_send: to=%s subject=%r body_len=%d — "
                "would POST to %s/api/tx",
                to_email,
                subject,
                len(body_html),
                self.base_url,
            )

        # TODO(N11): When listmonk is deployed, replace with actual API call:
        #   response = httpx.post(
        #       f"{self.base_url}/api/tx",
        #       json={"subscriber_email": to_email, "template_id": None, ...},
        #       headers={"Authorization": f"Bearer {self.api_key}"},
        #   )
        #   return {"status": "sent" if response.is_success else "failed", ...}

        return {
            "status": "sent",
            "provider": "listmonk",
            "message": "Logged — real sending pending listmonk deployment (N11)",
        }
