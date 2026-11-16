# Deployment Instructions

For a public reviewer link that remains available for a short demo period, follow
[RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md). It is separate from the offline
mobile deployment below and does not replace the offline-first prototype.

For a short-lived public cloud link without keeping the developer laptop online,
see [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md).

## Offline Packaging

### Mobile app

1. Place quantized TFLite model files under `mobile/assets/models`.
2. Install mobile dependencies on a connected build machine:

```bash
cd mobile
npm install
```

3. Build Android/iOS with the Datalake 3.0 app signing pipeline or a generated React Native native shell.
4. Verify airplane-mode enrollment, liveness, recognition, queueing, and later sync.

### Optional admin/backend demo

1. Pre-download Python and Node dependencies on a connected build machine.
2. Place local ONNX model files under `ai/models`.
3. Build Docker images:

```bash
docker compose build
```

4. Export images for transfer to the edge machine:

```bash
docker save hackathon-70-backend hackathon-70-frontend > nhai-edge-ai.tar
```

5. Load and run on the offline machine:

```bash
docker load < nhai-edge-ai.tar
docker compose up
```

## Production Hardening

- Replace `ADMIN_PASSWORD` and `APP_SECRET_KEY`.
- Mount `backend_data` to encrypted disk or an approved secure volume.
- Package exact model artifacts in `mobile/assets/models` and `ai/models`; do not allow runtime downloads.
- Run behind a local reverse proxy if TLS is required on the LAN.
- Keep Datalake REST sync disabled until a trusted endpoint is configured.

## Edge Sizing

Mobile minimum target:

- Android 8.0+ or iOS 12+
- 3 GB RAM
- Standard mobile CPU with NNAPI/Core ML acceleration where available
- Packaged model footprint under 20 MB

Optional admin/backend target:

- 2 CPU cores
- 4 GB RAM
- USB or integrated webcam
- 10 GB storage

Optional admin/backend recommended:

- 4 CPU cores
- 8 GB RAM
- Intel iGPU or small NVIDIA GPU if ONNX Runtime GPU is later enabled
