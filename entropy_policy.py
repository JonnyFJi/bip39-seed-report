"""Politica de seleccion; no obtiene ni combina material aleatorio."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


POLICY_VERSION = "redundant-with-os-backup-and-java-pair-v1"

CONTRIBUTION_BYTES = 32

PROVIDER_ORDER = (
    "python_os",
    "java_secure_random",
    "javascript_webcrypto",
    "python_secrets",
)

KNOWN_PROVIDERS = frozenset(PROVIDER_ORDER)

JAVA_PAIR = frozenset(
    {
        "java_secure_random",
        "javascript_webcrypto",
    }
)


class ProviderStatus(str, Enum):
    OK = "ok"
    UNAVAILABLE = "unavailable"
    TIMEOUT = "timeout"
    GENERATION_FAILED = "generation_failed"


class GenerationMode(str, Enum):
    REDUNDANT = "redundante"
    REDUCED = "redundante_reducido"
    OS_BACKUP = "actual_respaldo"


class EntropyPolicyError(RuntimeError):
    """La seleccion no cumple la politica."""


@dataclass(frozen=True)
class ProviderOutcome:
    """Estado no secreto; nunca incluir bytes, hashes o salida del auxiliar."""

    provider_id: str
    status: ProviderStatus

    def __post_init__(self) -> None:
        if not isinstance(self.provider_id, str):
            raise TypeError("El identificador debe ser texto.")

        if self.provider_id not in KNOWN_PROVIDERS:
            raise ValueError("Identificador de proveedor no reconocido.")

        if not isinstance(self.status, ProviderStatus):
            raise TypeError("Estado de proveedor no valido.")


@dataclass(frozen=True)
class GenerationPlan:
    mode: GenerationMode
    provider_ids: tuple[str, ...]
    omitted_provider_ids: tuple[str, ...]
    failed_provider_ids: tuple[str, ...]
    policy_version: str = POLICY_VERSION


def select_generation_plan(
    outcomes: Iterable[ProviderOutcome],
    *,
    critical_error: bool = False,
) -> GenerationPlan:
    """Decide el modo tras registrar un resultado por cada proveedor.

    critical_error debe ser True ante errores de integridad o protocolo.
    Los errores del combinador posterior tambien deben detener al llamador.
    """

    if type(critical_error) is not bool:
        raise TypeError("critical_error debe ser booleano.")

    if critical_error:
        raise EntropyPolicyError(
            "Operacion detenida por un error critico."
        )

    results: dict[str, ProviderStatus] = {}

    for outcome in outcomes:
        if not isinstance(outcome, ProviderOutcome):
            raise TypeError("Resultado de proveedor no valido.")

        if outcome.provider_id in results:
            raise EntropyPolicyError(
                "Se recibieron resultados duplicados."
            )

        results[outcome.provider_id] = outcome.status

    if frozenset(results) != KNOWN_PROVIDERS:
        raise EntropyPolicyError(
            "Debe registrarse un resultado por proveedor."
        )

    accepted = frozenset(
        provider_id
        for provider_id, status in results.items()
        if status is ProviderStatus.OK
    )

    if len(accepted) >= 3:
        mode = GenerationMode.REDUNDANT
        selected = accepted

    elif "python_os" in accepted:
        mode = GenerationMode.OS_BACKUP
        selected = frozenset({"python_os"})

    elif JAVA_PAIR.issubset(accepted):
        mode = GenerationMode.REDUCED
        selected = JAVA_PAIR

    else:
        raise EntropyPolicyError(
            "Proveedores insuficientes para los modos autorizados."
        )

    return GenerationPlan(
        mode=mode,
        provider_ids=tuple(
            p for p in PROVIDER_ORDER if p in selected
        ),
        omitted_provider_ids=tuple(
            p for p in PROVIDER_ORDER if p not in selected
        ),
        failed_provider_ids=tuple(
            p for p in PROVIDER_ORDER if p not in accepted
        ),
    )
    