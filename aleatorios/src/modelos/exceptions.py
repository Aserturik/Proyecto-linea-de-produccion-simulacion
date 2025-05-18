class ValidationError(Exception):
    """Excepción lanzada cuando un lote de números aleatorios no pasa las pruebas."""
    pass

class GenerationError(Exception):
    """Excepción base para otros errores de generación si fueran necesarios."""
    pass
