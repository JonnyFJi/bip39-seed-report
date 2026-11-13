"""Candidato experimental de finalizacion; no adquiere bytes ni genera palabras."""

from __future__ import annotations

import hashlib

from dataclasses import dataclass, field
from types import MappingProxyType

from entropy_policy import (
    CONTRIBUTION_BYTES,
    POLICY_VERSION,
    GenerationMode,
    GenerationPlan,
    ProviderOutcome,
    ProviderStatus,
    EntropyPolicyError,
    select_generation_plan,
)

from entropy_coordinator import AcquisitionResult


COMBINER_VERSION = "sha512-framed-v1"
PURPOSE = "bip39-initial-entropy"

HEADER = b"BSR-ENTROPY\x00"

VALID_ENTROPY_BITS = frozenset(
    {
        128,
        160,
        192,
        224,
        256,
    }
)


class EntropyCombinerError(RuntimeError):
    pass


@dataclass(frozen=True)
class FinalEntropyResult:
    mode: GenerationMode
    provider_ids: tuple[str, ...]
    entropy_bits: int
    method: str
    combiner_version: str
    entropy: bytes = field(repr=False)


def _validated_snapshot(acquisition):
    try:
        if type(acquisition) is not AcquisitionResult:
            raise EntropyCombinerError(
                "Resultado de adquisicion no admitido."
            )

        if type(acquisition.plan) is not GenerationPlan:
            raise EntropyCombinerError(
                "Plan no admitido."
            )

        if type(acquisition.plan.mode) is not GenerationMode:
            raise EntropyCombinerError(
                "Modo no admitido."
            )

        if acquisition.plan.policy_version != POLICY_VERSION:
            raise EntropyCombinerError(
                "Version de politica no admitida."
            )

        if type(acquisition.outcomes) is not tuple:
            raise EntropyCombinerError(
                "Estados no admitidos."
            )

        for outcome in acquisition.outcomes:
            if (
                type(outcome) is not ProviderOutcome
                or type(outcome.status) is not ProviderStatus
            ):
                raise EntropyCombinerError(
                    "Estado no admitido."
                )

        expected = select_generation_plan(
            acquisition.outcomes
        )

        if acquisition.plan != expected:
            raise EntropyCombinerError(
                "El plan no coincide con sus estados."
            )

        if type(acquisition.contributions) not in (
            dict,
            MappingProxyType,
        ):
            raise EntropyCombinerError(
                "Contenedor de aportaciones no admitido."
            )

        snapshot = dict(
            acquisition.contributions
        )

        if set(snapshot) != set(
            expected.provider_ids
        ):
            raise EntropyCombinerError(
                "Las aportaciones no coinciden con el plan."
            )

        for data in snapshot.values():
            if (
                type(data) is not bytes
                or len(data) != CONTRIBUTION_BYTES
            ):
                raise EntropyCombinerError(
                    "Aportacion no admitida."
                )

        return expected, snapshot

    except EntropyCombinerError:
        raise

    except (
        EntropyPolicyError,
        KeyError,
        TypeError,
        ValueError,
        RuntimeError,
    ):
        raise EntropyCombinerError(
            "Adquisicion incoherente; operacion detenida."
        ) from None


def _feed(hasher, value):
    hasher.update(
        len(value).to_bytes(
            4,
            "big",
        )
    )

    hasher.update(value)


def finalize_entropy(
    acquisition,
    *,
    entropy_bits,
):
    if (
        type(entropy_bits) is not int
        or entropy_bits not in VALID_ENTROPY_BITS
    ):
        raise ValueError(
            "La salida debe ser "
            "128, 160, 192, 224 o 256 bits."
        )

    plan, snapshot = _validated_snapshot(
        acquisition
    )

    nbytes = entropy_bits // 8

    if plan.mode is GenerationMode.OS_BACKUP:
        entropy = snapshot[
            "python_os"
        ][:nbytes]

        method = "python-os-prefix"

    else:
        try:
            hasher = hashlib.sha512()

            hasher.update(HEADER)

            fields = (
                COMBINER_VERSION.encode("ascii"),
                POLICY_VERSION.encode("ascii"),
                PURPOSE.encode("ascii"),
                plan.mode.value.encode("ascii"),
                entropy_bits.to_bytes(2, "big"),
                len(plan.provider_ids).to_bytes(1, "big"),
            )

            for value in fields:
                _feed(hasher, value)

            for provider_id in plan.provider_ids:
                _feed(
                    hasher,
                    provider_id.encode("ascii"),
                )

                _feed(
                    hasher,
                    snapshot[provider_id],
                )

            digest = hasher.digest()

            if (
                type(digest) is not bytes
                or len(digest) != 64
            ):
                raise EntropyCombinerError(
                    "Respuesta SHA-512 no admitida."
                )

            entropy = digest[:nbytes]
            method = "sha512-framed"

        except EntropyCombinerError:
            raise

        except Exception:
            raise EntropyCombinerError(
                "Fallo del combinador; "
                "no se permite respaldo."
            ) from None

    return FinalEntropyResult(
        mode=plan.mode,
        provider_ids=plan.provider_ids,
        entropy_bits=entropy_bits,
        method=method,
        combiner_version=COMBINER_VERSION,
        entropy=entropy,
    )
