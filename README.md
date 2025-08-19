# SRE Challenge - Vagrant + Dockerized Classifieds App

This repository provisions an Ubuntu VM with Docker and deploys a small classifieds web application and its supporting services using Docker Compose.

## Prerequisites
- Vagrant (2.2+)
- A provider such as VirtualBox or libvirt (VirtualBox assumed by default)

## Bring it up (recommended)
1. Start and provision the VM:
   vagrant up

   Provisioning installs Docker and brings the application stack up via Docker Compose.

2. Access the app:
   - From your host: http://localhost:8080/

3. Health endpoint:
   http://localhost:8080/healthz

4. SSH into the VM if needed:

   ```bash
   vagrant ssh
   ```

5. Manage the stack manually (inside the VM):

   ```bash
   cd /vagrant
   docker compose ps
   docker compose logs -f web
   docker compose up -d --build
   ```

## Seeding & migrations
- Migrations are SQL files stored in `app/migrations/` and are applied by the one-off seed job `(app/seed_db.py)`. Files are applied in alphabetical order.
- The seed job always attempts to apply SQL migrations first, then — only if `IMPORT_DUMP=TRUE` — attempts to import the dump file. This allows applying schema before loading data-only dumps.

## How the application behaves
- The web UI lists only validated posts (parts_service.list_parts filters by is_validated=1).
- Creating a part generates a validation token and (if contact_email provided) enqueues a background Celery task to send a validation email. The validation link points to `/validate/<token>` which marks the post validated when visited.
- Wishlists are stored in Redis (wishlist_service) and referenced by a wishlist_id cookie.

### Debugging tips
- Check service logs:

   ```bash
  docker compose logs -f <service>
  ```

- View MailHog: http://localhost:8025
- View RabbitMQ management: http://localhost:15672
- Re-run migrations/seed job:

```bash
  docker compose run --rm seed
```
