"""Auxiliar binario para los dos proveedores Python; sin salida diagnostica."""

from __future__ import annotations

import os
import sys


PROVIDERS = frozenset(
    {
        "python_os",
        "python_secrets",
    }
)

CONTRIBUTION_BYTES = 32

EXIT_GENERATION_FAILED = 10
EXIT_UNAVAILABLE = 11
EXIT_PROTOCOL = 12


class ProviderUnavailable(RuntimeError):
    pass


class ProtocolFailure(RuntimeError):
    pass


def parse_request(argv):
    if (
        len(argv) != 4
        or argv[0] != "--provider"
        or argv[2] != "--bytes"
        or argv[1] not in PROVIDERS
        or argv[3] != "32"
    ):
        raise ValueError("Solicitud no admitida.")

    return argv[1], CONTRIBUTION_BYTES


def generate_bytes(provider_id, nbytes):
    if (
        provider_id not in PROVIDERS
        or type(nbytes) is not int
        or nbytes != CONTRIBUTION_BYTES
    ):
        raise ValueError("Solicitud no admitida.")

    if provider_id == "python_os":
        generator = getattr(
            os,
            "urandom",
            None,
        )

        if not callable(generator):
            raise ProviderUnavailable()

        data = generator(nbytes)

    else:
        try:
            import secrets
        except ImportError:
            raise ProviderUnavailable() from None

        generator = getattr(
            secrets,
            "randbelow",
            None,
        )

        if not callable(generator):
            raise ProviderUnavailable()

        bound = 1 << (8 * nbytes)
        value = generator(bound)

        if (
            type(value) is not int
            or not 0 <= value < bound
        ):
            raise ProtocolFailure()

        data = value.to_bytes(
            nbytes,
            "big",
        )

    if (
        type(data) is not bytes
        or len(data) != nbytes
    ):
        raise ProtocolFailure()

    return data


def main(argv=None):
    try:
        if os.isatty(1):
            return EXIT_PROTOCOL

        provider_id, nbytes = parse_request(
            sys.argv[1:]
            if argv is None
            else argv
        )

    except Exception:
        return EXIT_PROTOCOL

    try:
        data = generate_bytes(
            provider_id,
            nbytes,
        )

    except ProviderUnavailable:
        return EXIT_UNAVAILABLE

    except (OSError, NotImplementedError):
        return EXIT_GENERATION_FAILED

    except Exception:
        return EXIT_PROTOCOL

    try:
        view = memoryview(data)

        while view:
            written = os.write(
                1,
                view,
            )

            if (
                written <= 0
                or written > len(view)
            ):
                return EXIT_PROTOCOL

            view = view[written:]

    except Exception:
        return EXIT_PROTOCOL

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
