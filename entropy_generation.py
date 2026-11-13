"""Una adquisicion y una finalizacion por solicitud; sin conversion a palabras."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

from entropy_combiner import (
    FinalEntropyResult,
    finalize_entropy,
)

from entropy_coordinator import (
    acquire_contributions,
)

from entropy_policy import ProviderOutcome


WORD_ENTROPY_BITS = MappingProxyType(
    {
        12: 128,
        15: 160,
        18: 192,
        21: 224,
        24: 256,
    }
)


@dataclass(frozen=True)
class EntropyGenerationResult:
    final: FinalEntropyResult
    outcomes: tuple[ProviderOutcome, ...]


def generate_entropy_result(
    words,
    *,
    runner,
    timeout_seconds,
):
    if (
        type(words) is not int
        or words not in WORD_ENTROPY_BITS
    ):
        raise ValueError(
            "BIP39 solo admite "
            "12, 15, 18, 21 o 24 palabras."
        )

    acquisition = acquire_contributions(
        runner,
        timeout_seconds=timeout_seconds,
    )

    final = finalize_entropy(
        acquisition,
        entropy_bits=WORD_ENTROPY_BITS[words],
    )

    return EntropyGenerationResult(
        final=final,
        outcomes=acquisition.outcomes,
    )
