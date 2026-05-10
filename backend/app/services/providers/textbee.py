"""TextBee SMS provider — N15 (#323).

Skeleton provider that will integrate with the TextBee Android SMS gateway
once deployed. For now, logs SMS details and marks deliveries as 'queued'.

Full integration will:
- POST to TextBee /api/v1/send endpoint
- Handle API key auth
- Track message status via gateway device ID
"""

import logging
from typing import Optional

logger = logging.getLogger("parish.providers.textbee")


class TextBeeProvider:
    """SMS delivery via TextBee Android gateway.

    This is a stub that will be connected to the real TextBee API
    when the phone gateway is deployed.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        device_id: Optional[str] = None,
        base_url: str = "https://api.textbee.dev/api/v1",
    ):
        self.api_key = api_key
        self.device_id = device_id
        self.base_url = base_url
        self._configured = bool(api_key and device_id)

    def send(self, phone_number: str, message: str) -> dict:
        """Send an SMS message.

        Args:
            phone_number: Recipient phone number (E.164 format preferred).
            message: SMS text body (max 160 chars per segment).

        Returns:
            dict with keys: status, provider, message
        """
        if not self._configured:
            logger.info(
                "textbee_stub_send: to=%s msg_len=%d — "
                "not configured (no api_key/device_id), marking as queued",
                phone_number,
                len(message),
            )
        else:
            logger.info(
                "textbee_send: to=%s msg_len=%d — "
                "would POST to %s/send via device %s",
                phone_number,
                len(message),
                self.base_url,
                self.device_id,
            )

        # TODO: When TextBee gateway is deployed, replace with actual API call:
        #   response = httpx.post(
        #       f"{self.base_url}/send",
        #       json={
        #           "deviceId": self.device_id,
        #           "recipients": [phone_number],
        #           "message": message,
        #       },
        #       headers={"x-api-key": self.api_key},
        #   )
        #   data = response.json()
        #   return {"status": "queued" if data.get("success") else "failed", ...}

        return {
            "status": "queued",
            "provider": "textbee",
            "message": "Logged — real sending pending TextBee deployment",
        }
