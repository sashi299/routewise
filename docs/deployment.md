# Deployment

The backend can be deployed with `render.yaml` and the frontend with `netlify.toml`. Configure `NEBIUS_API_KEY`, `CORS_ORIGINS`, and `VITE_API_URL` in the respective providers. The current sandbox has no GitHub, Netlify, or Render credentials connected, so this repository is prepared for deployment but has not been published externally.

Before publishing, run the live evaluator with a valid Nebius key and commit the generated `results/` artifacts only after reviewing that the numbers are real and reproducible.

## Reproducible frontend build

The managed publication installs frontend dependencies from `frontend/package-lock.json` during the hosted build. Generated dependency folders are not part of the Git checkpoint; this keeps the container build reproducible and prevents local tool wrappers from becoming deployment inputs.
