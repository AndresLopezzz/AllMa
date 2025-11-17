#!/usr/bin/env python
"""
Management command: clean_trash

Borra permanentemente (hard delete) los productos que hayan sido movidos a la
papelera (soft-deleted) hace más de `TTL` días.

Uso:
    python manage.py clean_trash
    python manage.py clean_trash --days 7
    python manage.py clean_trash --days 3 --dry-run
    python manage.py clean_trash --inventory 5

Opciones:
    --days N        Tiempo en días (TTL). Si no se pasa, toma el valor de
                    settings.TRASH_TTL_DAYS si está definido, o 2 días por defecto.
    --dry-run       No borra nada; solo muestra cuántos y cuáles serían borrados.
    --inventory ID  Limitar la limpieza al inventario con id == ID.
    --limit N       (Opcional) Limitar la cantidad de objetos a borrar en esta ejecución.
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Elimina permanentemente productos que llevan en la papelera más tiempo del TTL configurado.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            help='TTL en días: borrar productos en papelera más antiguos que este valor. Si no se provee, se usará settings.TRASH_TTL_DAYS o 2.'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='No eliminar; solo mostrar qué se eliminaría.'
        )
        parser.add_argument(
            '--inventory',
            type=int,
            help='ID del inventario; si se pasa, solo se limpiará la papelera de ese inventario.'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limitar la cantidad máxima de productos a borrar en esta ejecución (útil para batches).'
        )

    def handle(self, *args, **options):
        # Lazy import of Product and Inventory to avoid import-time issues
        try:
            from inventory.backend.inventory.models import Product, Inventory
        except Exception:
            # Fallback import path in case of different module resolution
            try:
                from inventory.backend.inventory.models import Product, Inventory  # noqa: T484
            except Exception as exc:
                raise CommandError(f'No se pudo importar los modelos required: {exc}')

        days = options.get('days')
        if days is None:
            days = getattr(settings, 'TRASH_TTL_DAYS', 2)
        if days < 0:
            raise CommandError('--days debe ser un entero no negativo')

        dry_run = options.get('dry_run', False)
        inventory_id = options.get('inventory')
        limit = options.get('limit')

        now = timezone.now()
        cutoff = now - timezone.timedelta(days=days)

        self.stdout.write(f'Iniciando limpieza de papelera. TTL={days} días (cutoff={cutoff.isoformat()})')
        if inventory_id:
            self.stdout.write(f'Filtrando por inventario id={inventory_id}')

        # Construir queryset objetivo
        qs = Product.objects.filter(deleted_at__isnull=False, deleted_at__lt=cutoff)

        if inventory_id is not None:
            # Verificar que el inventario exista
            try:
                Inventory.objects.get(id=inventory_id)
            except Inventory.DoesNotExist:
                raise CommandError(f'No existe un inventario con id={inventory_id}')
            qs = qs.filter(inventory_id=inventory_id)

        # Orden predictable: borrar primero los más antiguos
        qs = qs.order_by('deleted_at')

        total_candidates = qs.count()
        if total_candidates == 0:
            self.stdout.write('No se encontraron productos para eliminar.')
            return

        self.stdout.write(f'Productos candidatos para borrado permanente: {total_candidates}')
        if limit and limit > 0:
            qs = qs[:limit]
            self.stdout.write(f'Aplicando limit: se procesarán como mucho {limit} objetos en esta ejecución.')

        # Mostrar lista cuando verbosity >= 2 or dry_run
        verbosity = options.get('verbosity', 1)
        ids_list = list(qs.values_list('id', flat=True))
        if verbosity >= 2 or dry_run:
            self.stdout.write('IDs candidatos:')
            self.stdout.write(', '.join(str(i) for i in ids_list))

        if dry_run:
            self.stdout.write('Dry-run activado: no se realizará ningún borrado.')
            return

        # Ejecutar borrado en transacción
        deleted_count = 0
        try:
            with transaction.atomic():
                # Re-query to ensure consistency within transaction (and apply limit slice if any)
                del_qs = Product.objects.filter(id__in=ids_list).order_by('deleted_at')
                # delete() sobre QuerySet realizará borrado físico en DB
                res = del_qs.delete()
                # res is a tuple: (n_deleted, { 'app.Model': n, ... })
                deleted_count = res[0] if isinstance(res, tuple) else int(res)
        except Exception as exc:
            logger.exception('Error durante la limpieza de la papelera')
            raise CommandError(f'Error al eliminar productos: {exc}')

        self.stdout.write(self.style.SUCCESS(f'Borrado completo. Total eliminado: {deleted_count}'))
        if verbosity >= 2:
            self.stdout.write(f'IDs procesados: {", ".join(str(i) for i in ids_list)}')
