"""Coordinador desacoplado del transporte; no genera seeds ni mezcla bytes."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Protocol

from entropy_policy import (
    CONTRIBUTION_BYTES,
    PROVIDER_ORDER,
    GenerationPlan,
    ProviderOutcome,
    ProviderStatus,
    select_generation_plan,
)


class ProviderUnavailableError(RuntimeError):
    pass


class ProviderTimeoutError(RuntimeError):
    pass


class ProviderGenerationError(RuntimeError):
    pass


class ProviderProtocolError(RuntimeError):
    pass


class CoordinatorCriticalError(RuntimeError):
    pass


class ProviderRunner(Protocol):
    def acquire(
        self,
        provider_id: str,
        nbytes: int,
        *,
        timeout_seconds: float,
    ) -> bytes:
        """El ejecutor real debe imponer el timeout y limpiar sus procesos."""
        ...


@dataclass(frozen=True)
class AcquisitionResult:
    plan: GenerationPlan
    outcomes: tuple[ProviderOutcome, ...]
    contributions: Mapping[str, bytes] = field(repr=False)


def acquire_contributions(
    runner: ProviderRunner,
    *,
    timeout_seconds: float,
) -> AcquisitionResult:
    """Adquiere una vez por proveedor y conserva solo aportaciones seleccionadas.

    No impone un timeout por si mismo: esa obligacion pertenece al runner.
    No usar con auxiliares reales hasta implementar y probar su ejecutor.
    """

    if (
        type(timeout_seconds) not in (int, float)
        or not (0 < timeout_seconds < math.inf)
    ):
        raise ValueError(
            "El timeout debe ser numerico, positivo y finito."
        )

    outcomes = []
    contributions = {}

    for provider_id in PROVIDER_ORDER:
        try:
            data = runner.acquire(
                provider_id,
                CONTRIBUTION_BYTES,
                timeout_seconds=timeout_seconds,
            )

        except ProviderUnavailableError:
            status = ProviderStatus.UNAVAILABLE

        except ProviderTimeoutError:
            status = ProviderStatus.TIMEOUT

        except ProviderGenerationError:
            status = ProviderStatus.GENERATION_FAILED

        except ProviderProtocolError:
            raise CoordinatorCriticalError(
                "Operacion detenida: protocolo de proveedor invalido."
            ) from None

        except Exception:
            raise CoordinatorCriticalError(
                "Operacion detenida: error interno del ejecutor."
            ) from None

        else:
            if (
                type(data) is not bytes
                or len(data) != CONTRIBUTION_BYTES
            ):
                raise CoordinatorCriticalError(
                    "Operacion detenida: respuesta de proveedor invalida."
                )

            contributions[provider_id] = data
            status = ProviderStatus.OK

        outcomes.append(
            ProviderOutcome(provider_id, status)
        )

    plan = select_generation_plan(outcomes)

    selected = {
        provider_id: contributions[provider_id]
        for provider_id in plan.provider_ids
    }

    return AcquisitionResult(
        plan=plan,
        outcomes=tuple(outcomes),
        contributions=MappingProxyType(selected),
    )
