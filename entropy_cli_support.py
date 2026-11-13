"""Adaptacion no secreta para la interfaz; sin adquisiciones al importar."""

from __future__ import annotations

import math


PROVIDERS = (
    "python_os",
    "java_secure_random",
    "javascript_webcrypto",
    "python_secrets",
)

WORD_BITS = {
    12: 128,
    15: 160,
    18: 192,
    21: 224,
    24: 256,
}


def _run_redundant(words, timeout_seconds):
    try:
        from entropy_all_config import (
            build_all_provider_commands,
        )
        from entropy_process_runner import (
            ProcessProviderRunner,
        )
        from entropy_generation import (
            generate_entropy_result,
        )

        return generate_entropy_result(
            words,
            runner=ProcessProviderRunner(
                build_all_provider_commands()
            ),
            timeout_seconds=timeout_seconds,
        )

    except ImportError:
        raise RuntimeError(
            "Faltan modulos del modo redundante; "
            "operacion detenida."
        ) from None

    except OSError:
        raise RuntimeError(
            "No se pudo preparar el modo redundante; "
            "operacion detenida."
        ) from None


def generate_for_report(
    words,
    *,
    mode,
    timeout_seconds,
    current_generator,
):
    if (
        type(words) is not int
        or words not in WORD_BITS
    ):
        raise ValueError(
            "Cantidad de palabras BIP39 no admitida."
        )

    if mode not in (
        "current",
        "redundant",
    ):
        raise ValueError(
            "Modo de entropy no admitido."
        )

    if mode == "current":
        entropy = current_generator(words)

        if (
            type(entropy) is not bytes
            or len(entropy) * 8 != WORD_BITS[words]
        ):
            raise RuntimeError(
                "Respuesta del generador actual no admitida."
            )

        actual_mode = "actual_explicito"
        method = "os.urandom"
        policy_version = None
        combiner_version = None
        used = ("python_os",)

        statuses = {
            p: (
                "ok"
                if p == "python_os"
                else "not_attempted"
            )
            for p in PROVIDERS
        }

    else:
        if (
            type(timeout_seconds) not in (int, float)
            or not (0 < timeout_seconds < math.inf)
        ):
            raise ValueError(
                "El timeout debe ser positivo y finito."
            )

        result = _run_redundant(
            words,
            timeout_seconds,
        )

        from entropy_policy import (
            POLICY_VERSION,
            select_generation_plan,
        )
        from entropy_combiner import (
            COMBINER_VERSION,
        )

        plan = select_generation_plan(
            result.outcomes
        )

        final = result.final

        if (
            final.mode is not plan.mode
            or final.provider_ids != plan.provider_ids
            or final.combiner_version != COMBINER_VERSION
            or final.entropy_bits != WORD_BITS[words]
            or type(final.entropy) is not bytes
            or len(final.entropy) * 8 != WORD_BITS[words]
        ):
            raise RuntimeError(
                "Resultado redundante incoherente."
            )

        expected_method = (
            "python-os-prefix"
            if plan.mode.value == "actual_respaldo"
            else "sha512-framed"
        )

        if final.method != expected_method:
            raise RuntimeError(
                "Metodo de finalizacion incoherente."
            )

        entropy = final.entropy
        actual_mode = plan.mode.value
        method = final.method
        policy_version = POLICY_VERSION
        combiner_version = final.combiner_version
        used = plan.provider_ids

        statuses = {
            o.provider_id: o.status.value
            for o in result.outcomes
        }

    metadata = {
        "version": 1,
        "requested_mode": mode,
        "actual_mode": actual_mode,
        "method": method,
        "policy_version": policy_version,
        "combiner_version": combiner_version,
        "entropy_bits": WORD_BITS[words],
        "providers_used": list(used),
        "providers_omitted": [
            p
            for p in PROVIDERS
            if p not in used
        ],
        "providers_failed": [
            p
            for p in PROVIDERS
            if statuses[p] not in (
                "ok",
                "not_attempted",
            )
        ],
        "provider_statuses": statuses,
    }

    return entropy, metadata


def format_generation_metadata(info):
    modes = {
        "redundante": "redundante",
        "redundante_reducido": (
            "redundante reducido: Java + JavaScript"
        ),
        "actual_respaldo": (
            "actual como respaldo automatico"
        ),
        "actual_explicito": (
            "actual solicitado directamente"
        ),
    }

    status_labels = {
        "ok": "aceptado",
        "not_attempted": "no intentado",
        "unavailable": "no disponible",
        "timeout": "tiempo agotado",
        "generation_failed": "fallo de generacion",
    }

    requested = {
        "redundant": "redundante",
        "current": "actual",
    }

    methods = {
        "os.urandom": "os.urandom directo",
        "python-os-prefix": (
            "prefijo de python_os aceptado"
        ),
        "sha512-framed": (
            "SHA-512 con codificacion de campos"
        ),
    }

    statuses = info.get(
        "provider_statuses",
        {},
    )

    used = [
        p
        for p in PROVIDERS
        if p in info.get(
            "providers_used",
            (),
        )
    ]

    lines = [
        "",
        "GENERACION AUTOMATICA DE ENTROPY",
        (
            "Modo solicitado: "
            + requested.get(
                info.get("requested_mode"),
                "no reconocido",
            )
        ),
        (
            "Modo ejecutado: "
            + modes.get(
                info.get("actual_mode"),
                "no reconocido",
            )
        ),
        (
            "Metodo: "
            + methods.get(
                info.get("method"),
                "no reconocido",
            )
        ),
        (
            "Proveedores utilizados: "
            + (", ".join(used) or "ninguno")
        ),
    ]

    for provider_id in PROVIDERS:
        label = status_labels.get(
            statuses.get(provider_id),
            "no informado",
        )

        suffix = (
            "utilizado"
            if provider_id in used
            else "omitido"
        )

        lines.append(
            "  "
            + provider_id
            + ": "
            + label
            + "; "
            + suffix
        )

    if info.get("actual_mode") == "actual_respaldo":
        lines.append(
            "AVISO: cambio automatico a python_os; "
            "se reutilizo su aportacion aceptada."
        )

    elif (
        info.get("actual_mode")
        == "redundante_reducido"
    ):
        lines.append(
            "AVISO: continuidad con la pareja "
            "Java + JavaScript."
        )

    elif info.get("providers_failed"):
        lines.append(
            "AVISO: se continuo sin los "
            "proveedores fallidos indicados."
        )

    return lines


def generation_notices(info):
    mode = info.get("actual_mode")

    if mode == "actual_explicito":
        return [
            "La generacion utiliza os.urandom "
            "en modo actual solicitado directamente."
        ]

    notices = [
        (
            "La generacion automatica utilizo la politica "
            "de proveedores registrada en entropy_generation."
        ),
        (
            "Las interfaces pueden compartir fuentes del "
            "sistema operativo; no se certifica independencia."
        ),
        (
            "El combinador es experimental y no tiene "
            "una auditoria criptografica independiente."
        ),
    ]

    if mode == "actual_respaldo":
        notices.append(
            "Se activo el respaldo automatico utilizando "
            "solo la aportacion aceptada de python_os."
        )

    elif mode == "redundante_reducido":
        notices.append(
            "Se continuo con las aportaciones "
            "de Java y JavaScript."
        )

    return notices
