"""
Admin management API views

This module exposes an optional, admin-only API endpoint to trigger the
`clean_trash` management command from HTTP requests.

SECURITY NOTES:
- The endpoint is disabled by default. Enable it by setting the Django setting:
    ENABLE_CLEAN_TRASH_ADMIN_ENDPOINT = True

- When enabled, it requires a secret token to be provided (recommended).
  Configure the secret via:
    CLEAN_TRASH_ADMIN_SECRET = "<a strong secret>"

  The secret can be sent in one of the following ways (priority order):
    - HTTP header:  X-Clean-Trash-Secret: <secret>
    - POST body JSON: { "secret": "<secret>" }
    - Query param: ?secret=<secret>

- The endpoint also requires the requester to be an authenticated admin user
  (DRF permission `IsAdminUser`). Both checks are applied.

USAGE (example):
    POST /api/admin/clean_trash/       (with JSON body)
    {
        "days": 2,
        "dry_run": true,
        "inventory": 5,
        "limit": 100,
        "verbosity": 1,
        "secret": "my-secret"
    }

The view calls the management command `clean_trash` and returns the textual
output produced by the command.

To enable routing, include this module in your app urls:
    path('admin/', include('inventory.api_admin.management_views'))

This file provides `urlpatterns` with `admin/clean_trash/` so the above
`include()` will mount the endpoint at `/api/admin/clean_trash/` (because
`inventory/urls.py` already includes the app router under `/api/`).
"""
from io import StringIO
from typing import Optional

from django.conf import settings
from django.core.management import call_command

from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from django.urls import path


class CleanTrashView(APIView):
    """
    Admin-only view to trigger the clean_trash management command.

    Accepts POST with optional JSON fields:
      - days (int): TTL in days (overrides settings.TRASH_TTL_DAYS)
      - dry_run (bool): if true, command will run in dry-run mode (no deletion)
      - inventory (int): limit cleaning to specific inventory id
      - limit (int): maximum number of objects to delete in this execution
      - verbosity (int): verbosity level for the management command (default 1)
      - secret (string): secret token (alternatively send header X-Clean-Trash-Secret)

    Response:
      - 200 OK with {'ok': True, 'output': '<command stdout>'} on success
      - 400 Bad Request for invalid params
      - 403 Forbidden if endpoint disabled, invalid secret, or non-admin user
      - 500 Internal Server Error on unexpected errors
    """
    permission_classes = [IsAdminUser]

    def _get_provided_secret(self, request) -> Optional[str]:
        # Check header first, then body, then query param
        header = request.headers.get('X-Clean-Trash-Secret')
        if header:
            return header
        if isinstance(request.data, dict):
            body_secret = request.data.get('secret')
            if body_secret:
                return body_secret
        qp = request.query_params.get('secret')
        if qp:
            return qp
        return None

    def post(self, request, *args, **kwargs):
        # Check feature toggle
        if not getattr(settings, 'ENABLE_CLEAN_TRASH_ADMIN_ENDPOINT', False):
            return Response(
                {'error': 'Admin clean trash endpoint is disabled.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # If a secret is configured, require it
        configured_secret = getattr(settings, 'CLEAN_TRASH_ADMIN_SECRET', '')
        if configured_secret:
            provided = self._get_provided_secret(request)
            if not provided or provided != configured_secret:
                return Response(
                    {'error': 'Invalid or missing secret for admin clean-trash endpoint.'},
                    status=status.HTTP_403_FORBIDDEN
                )

        # Parse parameters
        data = request.data if isinstance(request.data, dict) else {}
        try:
            days = None
            if 'days' in data:
                days = int(data.get('days'))
                if days < 0:
                    raise ValueError('days must be non-negative')

            dry_run = bool(data.get('dry_run', False))
            inventory = data.get('inventory')
            if inventory is not None:
                inventory = int(inventory)
            limit = data.get('limit')
            if limit is not None:
                limit = int(limit)
            verbosity = int(data.get('verbosity', 1))
        except (ValueError, TypeError) as exc:
            return Response({'error': f'Invalid parameter: {exc}'}, status=status.HTTP_400_BAD_REQUEST)

        # Build kwargs for call_command
        cmd_kwargs = {
            'verbosity': verbosity,
        }
        if days is not None:
            cmd_kwargs['days'] = days
        else:
            # Let command use settings.TRASH_TTL_DAYS default if not provided
            pass

        if dry_run:
            cmd_kwargs['dry_run'] = True
        if inventory is not None:
            cmd_kwargs['inventory'] = inventory
        if limit is not None:
            cmd_kwargs['limit'] = limit

        # Run the management command and capture output
        stdout_buf = StringIO()
        try:
            call_command('clean_trash', **cmd_kwargs, stdout=stdout_buf)
        except Exception as exc:
            # Return the captured output and the error for debugging
            output = stdout_buf.getvalue()
            return Response(
                {'ok': False, 'error': str(exc), 'output': output},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        output = stdout_buf.getvalue()
        return Response({'ok': True, 'output': output}, status=status.HTTP_200_OK)


# Simple urlpatterns so this module can be included directly.
# Mounting this via `path('admin/', include('inventory.api_admin.management_views'))`
# will expose the endpoint at `/api/admin/clean_trash/` (given the existing project layout).
urlpatterns = [
    path('clean_trash/', CleanTrashView.as_view(), name='admin-clean-trash'),
]
