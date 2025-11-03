from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Product, Movement


@receiver(pre_save, sender=Product)
def track_quantity_change(sender, instance, **kwargs):
    """
    Signal que se ejecuta ANTES de guardar un Product.
    Guarda la cantidad anterior en una variable temporal para poder compararla después.
    """
    if instance.pk:  # Solo si el producto ya existe (no es creación)
        try:
            old_instance = Product.objects.get(pk=instance.pk)
            instance._old_quantity = old_instance.quantity
        except Product.DoesNotExist:
            instance._old_quantity = None
    else:
        # Si es un producto nuevo, la cantidad anterior es 0
        instance._old_quantity = 0


@receiver(post_save, sender=Product)
def create_movement_on_quantity_change(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta DESPUÉS de guardar un Product.
    Crea un Movement si la cantidad cambió.
    """
    # Obtener la cantidad anterior (guardada en el signal pre_save)
    old_quantity = getattr(instance, '_old_quantity', None)

    if old_quantity is None:
        return  # No hay información anterior, salir

    current_quantity = instance.quantity

    # Si la cantidad no cambió, no hacer nada
    if old_quantity == current_quantity:
        return

    # Calcular la diferencia
    quantity_change = current_quantity - old_quantity

    # Determinar el tipo de movimiento
    if quantity_change > 0:
        movement_type = 'entrada'
        reason = f'Entrada de {quantity_change} unidades'
    elif quantity_change < 0:
        movement_type = 'salida'
        reason = f'Salida de {abs(quantity_change)} unidades'
    else:
        return  # No hay cambio

    # Obtener el usuario que realizó el cambio desde el contexto
    # Esto se configura en la vista cuando se guarda el producto
    performed_by = getattr(instance, '_performed_by', None)

    # Crear el movimiento
    Movement.objects.create(
        product=instance,
        movement_type=movement_type,
        quantity=quantity_change,
        quantity_before=old_quantity,
        quantity_after=current_quantity,
        reason=reason,
        performed_by=performed_by
    )

    # Limpiar el atributo temporal
    if hasattr(instance, '_old_quantity'):
        delattr(instance, '_old_quantity')
    if hasattr(instance, '_performed_by'):
        delattr(instance, '_performed_by')
