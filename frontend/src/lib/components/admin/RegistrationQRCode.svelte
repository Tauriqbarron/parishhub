<script lang="ts">
  import QRCode from 'qrcode';

  let qrDataUrl = '';
  let registrationUrl = '';

  async function generateQR() {
    registrationUrl = `${window.location.origin}/register`;
    qrDataUrl = await QRCode.toDataURL(registrationUrl, { width: 300 });
  }
</script>

<div class="p-4 border rounded">
  <h3 class="font-bold mb-4">Registration QR Code</h3>

  <button on:click={generateQR} class="bg-blue-600 text-white px-4 py-2 rounded mb-4">
    Generate QR Code
  </button>

  {#if qrDataUrl}
    <div class="text-center">
      <img src={qrDataUrl} alt="Registration QR Code" class="mx-auto mb-2" />
      <p class="text-sm text-gray-600">{registrationUrl}</p>
      <a
        href={qrDataUrl}
        download="parish-registration-qr.png"
        class="text-blue-600 underline"
      >
        Download QR Code
      </a>
    </div>
  {/if}
</div>
