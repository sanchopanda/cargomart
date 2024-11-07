import logging

def convert_to_single(value):
    """
    Преобразует список с одним элементом в одиночное значение.
    Если значение не список или список содержит более одного элемента, возвращает его без изменений.
    
    Args:
        value (any): Значение для преобразования.
        
    Returns:
        any: Преобразованное значение.
    """
    if isinstance(value, list):
        if len(value) == 1:
            return value[0]
    return value