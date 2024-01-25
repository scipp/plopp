from typing import Any, NewType, Optional

import sphinx

_typehint_aliases = {
    'scipp._scipp.core.DataArray': 'scipp.DataArray',
    'scipp._scipp.core.Dataset': 'scipp.Dataset',
    'scipp._scipp.core.DType': 'scipp.DType',
    'scipp._scipp.core.Unit': 'scipp.Unit',
    'scipp._scipp.core.Variable': 'scipp.Variable',
    'scipp.core.data_group.DataGroup': 'scipp.DataGroup',
}


def typehints_formatter_for(package: str) -> callable:
    def typehints_formatter(annotation, config: sphinx.config.Config) -> Optional[str]:
        """Format typehints with improved NewType handling."""
        _ = config
        if _is_new_type(annotation):
            return _format_new_type(annotation, package)
        if _is_type_alias_type(annotation):
            return _format_type_alias_type(annotation, package)
        return None

    return typehints_formatter


def _is_new_type(annotation: Any) -> bool:
    # TODO Switch to isinstance(key, NewType) once our minimum is Python 3.10
    # Note that we cannot pass mypy in Python<3.10 since NewType is not a type.
    return hasattr(annotation, '__supertype__')


def _format_new_type(annotation: NewType, package: str) -> str:
    return (
        f'{_internal_link(annotation, "class", package)}'
        f' ({_link(annotation.__supertype__, "class")})'
    )


def _is_type_alias_type(annotation) -> bool:
    try:
        from typing import TypeAliasType

        return isinstance(annotation, TypeAliasType)
    except ImportError:
        return False  # pre python 3.12


def _format_type_alias_type(annotation: Any, package: str) -> str:
    alias = _internal_link(annotation, "class", package, annotation.__type_params__)
    value = _link(annotation.__value__, "class", _get_type_args(annotation.__value__))
    return f'{alias} ({value})'


def _get_type_args(ty: type) -> tuple[type, ...]:
    if (args := getattr(ty, '__args__', None)) is not None:
        return args  # e.g. list[int]
    return ty.__type_params__


def _internal_link(
    annotation: Any,
    kind: str,
    package: str,
    type_params: Optional[tuple[type, ...]] = None,
) -> str:
    target = f'{annotation.__module__}.{annotation.__name__}'
    label = f'{annotation.__module__.removeprefix(package+".")}.{annotation.__name__}'
    if type_params:
        label += f'[{", ".join(ty.__name__ for ty in type_params)}]'
    return f':{kind}:`{label} <{target}>`'


def _link(ty: type, kind: str, type_params: Optional[tuple[type, ...]] = None) -> str:
    if ty.__module__ == 'builtins':
        target = ty.__name__
    else:
        target = f'{ty.__module__}.{ty.__name__}'
    label = _typehint_aliases.get(target, target)
    if type_params:
        label += f'[{", ".join(ty.__name__ for ty in type_params)}]'
    return f':{kind}:`{label} <{target}>`'
