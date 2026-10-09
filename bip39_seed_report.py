#!/usr/bin/env python3
"""
Offline BIP39 Seed Report

PROGRAMA SOLO CON FINES EDUCATIVOS Y DE PRUEBA.

Esta herramienta genera, valida y reporta material BIP39/BIP32 offline.
No es una wallet: no consulta la red, no muestra saldos, no firma
transacciones y no transmite transacciones.

Uso seguro recomendado:
- Ejecutar solo offline.
- Usar un entorno confiable.
- Proporcionar entropy correcta y verificable.
- Preferir una máquina limpia y no comprometida.
- No usar con fondos reales: el proyecto no está auditado para producción.

Entrada compatible:
- -w / --words
- --entropy-bin
- --entropy-hex
- --mnemonic
- --mnemonic-incomplete

Opciones:
- -p / --passphrase
- -i / --interactive
- --audit-passphrase
- --run-tests
- --vectors-file
- -n / --network
- -f / --format
- -o / --output
- --show-all

Dependencias:
    python3 -m pip install mnemonic bip-utils cryptography
"""

from __future__ import annotations

import argparse
import base64
import getpass
import warnings
import hashlib
import hmac
import json
import os
import pathlib
import sys
import tempfile
import unicodedata

import time
from typing import Callable, Collection, TypeVar

from collections import Counter
import math

from mnemonic import Mnemonic
from bip_utils import (
    Bip39SeedGenerator,
    Bip44,
    Bip44Coins,
    Bip44Changes,
    Bip49,
    Bip49Coins,
    Bip84,
    Bip84Coins,
    Bip86,
    Bip86Coins,
)

# Integrado desde sensitive_terminal_input.py; ver historial de cambios.
"""Utilidades genéricas para entradas sensibles en una terminal.

No contiene lógica de wallet, BIP39, claves ni derivación criptográfica.
Proporciona:
- Entrada sin eco mediante getpass.
- Menús temporizados con cancelación segura.
- Revisión temporal opcional de valores.
- Confirmación doble de secretos.
- Entrada visible opcional tras advertencia explícita.

Limitación: la limpieza ANSI solo intenta ocultar la vista actual. No borra
scrollback, registros de terminal, capturas, memoria, swap ni un sistema
comprometido.
"""

import getpass
import os
import sys
import time
from typing import Callable, Collection, TypeVar


DEFAULT_DECISION_TIMEOUT_SECONDS = 360
T = TypeVar("T")


class InputTimeoutError(RuntimeError):
    """La persona usuaria no tomó una decisión antes del límite."""


class InputCancelledError(RuntimeError):
    """La persona usuaria canceló explícitamente la operación."""


def _require_tty() -> None:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise RuntimeError(
            "Esta operación requiere una terminal interactiva (TTY)."
        )

def read_hidden_secret(prompt: str) -> str:
    """Lee un secreto sin aceptar el fallback de getpass con eco."""
    _require_tty()

    with warnings.catch_warnings():
        warnings.simplefilter("error", getpass.GetPassWarning)

        try:
            return getpass.getpass(prompt)
        except getpass.GetPassWarning as exc:
            raise RuntimeError(
                "No se pudo garantizar una entrada sin eco. "
                "Operación cancelada: utiliza una terminal local compatible."
            ) from exc

def _normalize_choice(value: str) -> str:
    return value.strip().lower()

def _read_line_with_timeout_unix(prompt: str, timeout_seconds: int) -> str:
    import selectors

    sys.stdout.write(prompt)
    sys.stdout.flush()

    selector = selectors.DefaultSelector()
    try:
        selector.register(sys.stdin, selectors.EVENT_READ)
        events = selector.select(timeout_seconds)
    finally:
        selector.close()

    if not events:
        raise InputTimeoutError(
            f"Tiempo agotado: no hubo respuesta en {timeout_seconds} segundos."
        )

    line = sys.stdin.readline()
    if line == "":
        raise EOFError("Entrada estándar finalizada.")
    return line.rstrip("\n")


def _read_line_with_timeout_windows(prompt: str, timeout_seconds: int) -> str:
    import msvcrt

    sys.stdout.write(prompt)
    sys.stdout.flush()

    deadline = time.monotonic() + timeout_seconds
    chars: list[str] = []

    while time.monotonic() < deadline:
        if not msvcrt.kbhit():
            time.sleep(0.05)
            continue

        char = msvcrt.getwch()
        if char in ("\r", "\n"):
            sys.stdout.write("\n")
            sys.stdout.flush()
            return "".join(chars)
        if char == "\x03":
            raise KeyboardInterrupt
        if char == "\x1a":
            raise EOFError("Entrada estándar finalizada.")
        if char == "\b":
            if chars:
                chars.pop()
                sys.stdout.write("\b \b")
                sys.stdout.flush()
            continue
        if char in ("\x00", "\xe0"):
            msvcrt.getwch()
            continue
        chars.append(char)
        sys.stdout.write(char)
        sys.stdout.flush()

    raise InputTimeoutError(
        f"Tiempo agotado: no hubo respuesta en {timeout_seconds} segundos."
    )


def timed_input(prompt: str, timeout_seconds: int = DEFAULT_DECISION_TIMEOUT_SECONDS) -> str:
    """Lee una línea visible con límite de tiempo en una TTY local.

    En Unix usa selectors sobre stdin. En Windows usa msvcrt para la consola.
    La función se usa solo para decisiones cortas de menú, no para secretos.
    """
    _require_tty()
    if timeout_seconds <= 0:
        raise ValueError("El timeout debe ser mayor que cero.")

    if os.name == "nt":
        return _read_line_with_timeout_windows(prompt, timeout_seconds)
    return _read_line_with_timeout_unix(prompt, timeout_seconds)


def timed_menu_choice(
    prompt: str,
    choices: Collection[str],
    timeout_seconds: int = DEFAULT_DECISION_TIMEOUT_SECONDS,
) -> str:
    """Solicita una opción visible y devuelve una opción normalizada válida."""
    normalized_choices = {_normalize_choice(choice) for choice in choices}
    if not normalized_choices:
        raise ValueError("Debe proporcionarse al menos una opción válida.")

    while True:
        value = _normalize_choice(timed_input(prompt, timeout_seconds))
        if value in normalized_choices:
            return value
        print(
            "❌ Opción inválida. Opciones válidas: "
            + ", ".join(sorted(normalized_choices)).upper()
        )


def clear_sensitive_display(lines: int = 1) -> bool:
    """Intenta ocultar líneas recientes de la vista actual mediante ANSI.

    Devuelve True si se emitieron secuencias ANSI. No garantiza eliminación de
    scrollback o de cualquier registro externo.
    """
    if lines < 1 or not sys.stdout.isatty():
        return False

    try:
        for _ in range(lines):
            sys.stdout.write("\x1b[1A\r\x1b[2K")
        sys.stdout.flush()
        return True
    except OSError:
        return False


def show_sensitive_value_temporarily(value: str, label: str) -> None:
    """Muestra un valor solo tras decisión explícita y luego intenta ocultarlo."""
    print("\n⚠️  ADVERTENCIA: se mostrará información sensible en esta terminal.")
    print("   Puede quedar en scrollback, grabaciones o capturas de pantalla.\n")
    print(f"{label}:\n{value}")
    input("\nPresiona Enter para intentar ocultar la vista temporal...")
    cleared = clear_sensitive_display(lines=4)
    if not cleared:
        print(
            "⚠️  No fue posible limpiar visualmente esta consola. "
            "Limpia el scrollback manualmente si procede."
        )


def _validated_hidden_value(prompt: str, validator: Callable[[str], T]) -> tuple[str, T]:
    value = read_hidden_secret(prompt)
    validated = validator(value)
    return value, validated


def get_reviewable_secure_input(
    prompt: str,
    validator: Callable[[str], T],
    description: str,
    timeout_seconds: int = DEFAULT_DECISION_TIMEOUT_SECONDS,
    allow_visible_review: bool = True,
) -> T:
    """Obtiene un valor sin eco y permite Ver, Confirmar, Reingresar o Cancelar.

    El validador recibe el texto introducido y devuelve el valor normalizado o
    procesado. Debe lanzar ValueError si la entrada no es válida.
    """
    while True:
        try:
            raw_value, validated = _validated_hidden_value(prompt, validator)
        except ValueError as exc:
            print(f"❌ Entrada inválida: {exc}")
            continue

        print(f"\nEntrada recibida y validada: {description}.")
        print("[V] Ver temporalmente  [C] Confirmar y continuar  [R] Reingresar  [Q] Cancelar")
        print(f"Tienes {timeout_seconds} segundos para seleccionar una opción.")
        choice = timed_menu_choice(
            "Opción [V/C/R/Q]: ",
            {"v", "c", "r", "q"},
            timeout_seconds,
        )

        if choice == "c":
            raw_value = ""
            return validated
        if choice == "r":
            raw_value = ""
            continue
        if choice == "q":
            raw_value = ""
            raise InputCancelledError("Operación cancelada por el usuario.")
        if choice == "v" and allow_visible_review:
            show_sensitive_value_temporarily(raw_value, description)
            continue
        print("❌ La revisión visible no está habilitada para esta entrada.")


def get_confirmed_secret(
    prompt: str,
    confirmation_prompt: str,
    normalizer: Callable[[str], str] | None = None,
) -> str:
    """Solicita un secreto dos veces sin eco y exige coincidencia.

    Si se suministra normalizer, la comparación se efectúa sobre el resultado
    normalizado y se devuelve esa forma normalizada.
    """
    normalize = normalizer or (lambda value: value)
    while True:
        first = read_hidden_secret(prompt)
        second = read_hidden_secret(confirmation_prompt)
        normalized_first = normalize(first)
        normalized_second = normalize(second)

        if normalized_first == normalized_second:
            first = ""
            second = ""
            return normalized_first

        first = ""
        second = ""
        print("❌ Los valores no coinciden. Intenta nuevamente.")


def get_visible_input_with_acknowledgement(
    prompt: str,
    validator: Callable[[str], T],
    description: str,
    timeout_seconds: int = DEFAULT_DECISION_TIMEOUT_SECONDS,
) -> T:
    """Obtiene una entrada visible únicamente tras advertencia y confirmación.

    Se usa para texto largo que la persona necesite editar visualmente. No se
    aplica a contraseñas ni a otros secretos que deban permanecer ocultos.
    """
    print("\n⚠️  MODO DE EDICIÓN VISIBLE")
    print("El contenido se verá mientras escribes o pegas.")
    print("Puede quedar en scrollback, grabaciones o capturas de pantalla.")
    print("Úsalo solo en una terminal local confiable.")
    print(f"Tienes {timeout_seconds} segundos para decidir.")

    choice = timed_menu_choice(
        "[C] Entiendo y continuar  [Q] Cancelar: ",
        {"c", "q"},
        timeout_seconds,
    )
    if choice == "q":
        raise InputCancelledError("Operación cancelada por el usuario.")

    while True:
        raw_value = input(prompt)
        try:
            validated = validator(raw_value)
        except ValueError as exc:
            raw_value = ""
            print(f"❌ Entrada inválida: {exc}")
            continue

        print(f"\nEntrada recibida y validada: {description}.")
        print("[C] Confirmar y continuar  [R] Reingresar  [Q] Cancelar")
        print(f"Tienes {timeout_seconds} segundos para seleccionar una opción.")
        choice = timed_menu_choice(
            "Opción [C/R/Q]: ",
            {"c", "r", "q"},
            timeout_seconds,
        )
        if choice == "c":
            raw_value = ""
            clear_sensitive_display(lines=1)
            return validated
        if choice == "r":
            raw_value = ""
            continue
        raw_value = ""
        raise InputCancelledError("Operación cancelada por el usuario.")

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.exceptions import InvalidTag
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️  ADVERTENCIA: La librería 'cryptography' no está instalada.")
    print("    Instala con: pip3 install cryptography")
    print("    El script continuará pero NO podrá encriptar archivos.\n")

# ============================================================================
# WORDLIST BIP39 OFICIAL EMBEBIDA
# Fuente: https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt
# Hash SHA256: 187db04a869dd9bc7be80d21a86497d692c0db6abd3aa8cb6be5d618ff757fae
# ============================================================================

BIP39_OFFICIAL_WORDLIST = [
    "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract", "absurd", "abuse",
    "access", "accident", "account", "accuse", "achieve", "acid", "acoustic", "acquire", "across", "act",
    "action", "actor", "actress", "actual", "adapt", "add", "addict", "address", "adjust", "admit",
    "adult", "advance", "advice", "aerobic", "affair", "afford", "afraid", "again", "age", "agent",
    "agree", "ahead", "aim", "air", "airport", "aisle", "alarm", "album", "alcohol", "alert",
    "alien", "all", "alley", "allow", "almost", "alone", "alpha", "already", "also", "alter",
    "always", "amateur", "amazing", "among", "amount", "amused", "analyst", "anchor", "ancient", "anger",
    "angle", "angry", "animal", "ankle", "announce", "annual", "another", "answer", "antenna", "antique",
    "anxiety", "any", "apart", "apology", "appear", "apple", "approve", "april", "arch", "arctic",
    "area", "arena", "argue", "arm", "armed", "armor", "army", "around", "arrange", "arrest",
    "arrive", "arrow", "art", "artefact", "artist", "artwork", "ask", "aspect", "assault", "asset",
    "assist", "assume", "asthma", "athlete", "atom", "attack", "attend", "attitude", "attract", "auction",
    "audit", "august", "aunt", "author", "auto", "autumn", "average", "avocado", "avoid", "awake",
    "aware", "away", "awesome", "awful", "awkward", "axis", "baby", "bachelor", "bacon", "badge",
    "bag", "balance", "balcony", "ball", "bamboo", "banana", "banner", "bar", "barely", "bargain",
    "barrel", "base", "basic", "basket", "battle", "beach", "bean", "beauty", "because", "become",
    "beef", "before", "begin", "behave", "behind", "believe", "below", "belt", "bench", "benefit",
    "best", "betray", "better", "between", "beyond", "bicycle", "bid", "bike", "bind", "biology",
    "bird", "birth", "bitter", "black", "blade", "blame", "blanket", "blast", "bleak", "bless",
    "blind", "blood", "blossom", "blouse", "blue", "blur", "blush", "board", "boat", "body",
    "boil", "bomb", "bone", "bonus", "book", "boost", "border", "boring", "borrow", "boss",
    "bottom", "bounce", "box", "boy", "bracket", "brain", "brand", "brass", "brave", "bread",
    "breeze", "brick", "bridge", "brief", "bright", "bring", "brisk", "broccoli", "broken", "bronze",
    "broom", "brother", "brown", "brush", "bubble", "buddy", "budget", "buffalo", "build", "bulb",
    "bulk", "bullet", "bundle", "bunker", "burden", "burger", "burst", "bus", "business", "busy",
    "butter", "buyer", "buzz", "cabbage", "cabin", "cable", "cactus", "cage", "cake", "call",
    "calm", "camera", "camp", "can", "canal", "cancel", "candy", "cannon", "canoe", "canvas",
    "canyon", "capable", "capital", "captain", "car", "carbon", "card", "cargo", "carpet", "carry",
    "cart", "case", "cash", "casino", "castle", "casual", "cat", "catalog", "catch", "category",
    "cattle", "caught", "cause", "caution", "cave", "ceiling", "celery", "cement", "census", "century",
    "cereal", "certain", "chair", "chalk", "champion", "change", "chaos", "chapter", "charge", "chase",
    "chat", "cheap", "check", "cheese", "chef", "cherry", "chest", "chicken", "chief", "child",
    "chimney", "choice", "choose", "chronic", "chuckle", "chunk", "churn", "cigar", "cinnamon", "circle",
    "citizen", "city", "civil", "claim", "clap", "clarify", "claw", "clay", "clean", "clerk",
    "clever", "click", "client", "cliff", "climb", "clinic", "clip", "clock", "clog", "close",
    "cloth", "cloud", "clown", "club", "clump", "cluster", "clutch", "coach", "coast", "coconut",
    "code", "coffee", "coil", "coin", "collect", "color", "column", "combine", "come", "comfort",
    "comic", "common", "company", "concert", "conduct", "confirm", "congress", "connect", "consider", "control",
    "convince", "cook", "cool", "copper", "copy", "coral", "core", "corn", "correct", "cost",
    "cotton", "couch", "country", "couple", "course", "cousin", "cover", "coyote", "crack", "cradle",
    "craft", "cram", "crane", "crash", "crater", "crawl", "crazy", "cream", "credit", "creek",
    "crew", "cricket", "crime", "crisp", "critic", "crop", "cross", "crouch", "crowd", "crucial",
    "cruel", "cruise", "crumble", "crunch", "crush", "cry", "crystal", "cube", "culture", "cup",
    "cupboard", "curious", "current", "curtain", "curve", "cushion", "custom", "cute", "cycle", "dad",
    "damage", "damp", "dance", "danger", "daring", "dash", "daughter", "dawn", "day", "deal",
    "debate", "debris", "decade", "december", "decide", "decline", "decorate", "decrease", "deer", "defense",
    "define", "defy", "degree", "delay", "deliver", "demand", "demise", "denial", "dentist", "deny",
    "depart", "depend", "deposit", "depth", "deputy", "derive", "describe", "desert", "design", "desk",
    "despair", "destroy", "detail", "detect", "develop", "device", "devote", "diagram", "dial", "diamond",
    "diary", "dice", "diesel", "diet", "differ", "digital", "dignity", "dilemma", "dinner", "dinosaur",
    "direct", "dirt", "disagree", "discover", "disease", "dish", "dismiss", "disorder", "display", "distance",
    "divert", "divide", "divorce", "dizzy", "doctor", "document", "dog", "doll", "dolphin", "domain",
    "donate", "donkey", "donor", "door", "dose", "double", "dove", "draft", "dragon", "drama",
    "drastic", "draw", "dream", "dress", "drift", "drill", "drink", "drip", "drive", "drop",
    "drum", "dry", "duck", "dumb", "dune", "during", "dust", "dutch", "duty", "dwarf",
    "dynamic", "eager", "eagle", "early", "earn", "earth", "easily", "east", "easy", "echo",
    "ecology", "economy", "edge", "edit", "educate", "effort", "egg", "eight", "either", "elbow",
    "elder", "electric", "elegant", "element", "elephant", "elevator", "elite", "else", "embark", "embody",
    "embrace", "emerge", "emotion", "employ", "empower", "empty", "enable", "enact", "end", "endless",
    "endorse", "enemy", "energy", "enforce", "engage", "engine", "enhance", "enjoy", "enlist", "enough",
    "enrich", "enroll", "ensure", "enter", "entire", "entry", "envelope", "episode", "equal", "equip",
    "era", "erase", "erode", "erosion", "error", "erupt", "escape", "essay", "essence", "estate",
    "eternal", "ethics", "evidence", "evil", "evoke", "evolve", "exact", "example", "excess", "exchange",
    "excite", "exclude", "excuse", "execute", "exercise", "exhaust", "exhibit", "exile", "exist", "exit",
    "exotic", "expand", "expect", "expire", "explain", "expose", "express", "extend", "extra", "eye",
    "eyebrow", "fabric", "face", "faculty", "fade", "faint", "faith", "fall", "false", "fame",
    "family", "famous", "fan", "fancy", "fantasy", "farm", "fashion", "fat", "fatal", "father",
    "fatigue", "fault", "favorite", "feature", "february", "federal", "fee", "feed", "feel", "female",
    "fence", "festival", "fetch", "fever", "few", "fiber", "fiction", "field", "figure", "file",
    "film", "filter", "final", "find", "fine", "finger", "finish", "fire", "firm", "first",
    "fiscal", "fish", "fit", "fitness", "fix", "flag", "flame", "flash", "flat", "flavor",
    "flee", "flight", "flip", "float", "flock", "floor", "flower", "fluid", "flush", "fly",
    "foam", "focus", "fog", "foil", "fold", "follow", "food", "foot", "force", "forest",
    "forget", "fork", "fortune", "forum", "forward", "fossil", "foster", "found", "fox", "fragile",
    "frame", "frequent", "fresh", "friend", "fringe", "frog", "front", "frost", "frown", "frozen",
    "fruit", "fuel", "fun", "funny", "furnace", "fury", "future", "gadget", "gain", "galaxy",
    "gallery", "game", "gap", "garage", "garbage", "garden", "garlic", "garment", "gas", "gasp",
    "gate", "gather", "gauge", "gaze", "general", "genius", "genre", "gentle", "genuine", "gesture",
    "ghost", "giant", "gift", "giggle", "ginger", "giraffe", "girl", "give", "glad", "glance",
    "glare", "glass", "glide", "glimpse", "globe", "gloom", "glory", "glove", "glow", "glue",
    "goat", "goddess", "gold", "good", "goose", "gorilla", "gospel", "gossip", "govern", "gown",
    "grab", "grace", "grain", "grant", "grape", "grass", "gravity", "great", "green", "grid",
    "grief", "grit", "grocery", "group", "grow", "grunt", "guard", "guess", "guide", "guilt",
    "guitar", "gun", "gym", "habit", "hair", "half", "hammer", "hamster", "hand", "happy",
    "harbor", "hard", "harsh", "harvest", "hat", "have", "hawk", "hazard", "head", "health",
    "heart", "heavy", "hedgehog", "height", "hello", "helmet", "help", "hen", "hero", "hidden",
    "high", "hill", "hint", "hip", "hire", "history", "hobby", "hockey", "hold", "hole",
    "holiday", "hollow", "home", "honey", "hood", "hope", "horn", "horror", "horse", "hospital",
    "host", "hotel", "hour", "hover", "hub", "huge", "human", "humble", "humor", "hundred",
    "hungry", "hunt", "hurdle", "hurry", "hurt", "husband", "hybrid", "ice", "icon", "idea",
    "identify", "idle", "ignore", "ill", "illegal", "illness", "image", "imitate", "immense", "immune",
    "impact", "impose", "improve", "impulse", "inch", "include", "income", "increase", "index", "indicate",
    "indoor", "industry", "infant", "inflict", "inform", "inhale", "inherit", "initial", "inject", "injury",
    "inmate", "inner", "innocent", "input", "inquiry", "insane", "insect", "inside", "inspire", "install",
    "intact", "interest", "into", "invest", "invite", "involve", "iron", "island", "isolate", "issue",
    "item", "ivory", "jacket", "jaguar", "jar", "jazz", "jealous", "jeans", "jelly", "jewel",
    "job", "join", "joke", "journey", "joy", "judge", "juice", "jump", "jungle", "junior",
    "junk", "just", "kangaroo", "keen", "keep", "ketchup", "key", "kick", "kid", "kidney",
    "kind", "kingdom", "kiss", "kit", "kitchen", "kite", "kitten", "kiwi", "knee", "knife",
    "knock", "know", "lab", "label", "labor", "ladder", "lady", "lake", "lamp", "language",
    "laptop", "large", "later", "latin", "laugh", "laundry", "lava", "law", "lawn", "lawsuit",
    "layer", "lazy", "leader", "leaf", "learn", "leave", "lecture", "left", "leg", "legal",
    "legend", "leisure", "lemon", "lend", "length", "lens", "leopard", "lesson", "letter", "level",
    "liar", "liberty", "library", "license", "life", "lift", "light", "like", "limb", "limit",
    "link", "lion", "liquid", "list", "little", "live", "lizard", "load", "loan", "lobster",
    "local", "lock", "logic", "lonely", "long", "loop", "lottery", "loud", "lounge", "love",
    "loyal", "lucky", "luggage", "lumber", "lunar", "lunch", "luxury", "lyrics", "machine", "mad",
    "magic", "magnet", "maid", "mail", "main", "major", "make", "mammal", "man", "manage",
    "mandate", "mango", "mansion", "manual", "maple", "marble", "march", "margin", "marine", "market",
    "marriage", "mask", "mass", "master", "match", "material", "math", "matrix", "matter", "maximum",
    "maze", "meadow", "mean", "measure", "meat", "mechanic", "medal", "media", "melody", "melt",
    "member", "memory", "mention", "menu", "mercy", "merge", "merit", "merry", "mesh", "message",
    "metal", "method", "middle", "midnight", "milk", "million", "mimic", "mind", "minimum", "minor",
    "minute", "miracle", "mirror", "misery", "miss", "mistake", "mix", "mixed", "mixture", "mobile",
    "model", "modify", "mom", "moment", "monitor", "monkey", "monster", "month", "moon", "moral",
    "more", "morning", "mosquito", "mother", "motion", "motor", "mountain", "mouse", "move", "movie",
    "much", "muffin", "mule", "multiply", "muscle", "museum", "mushroom", "music", "must", "mutual",
    "myself", "mystery", "myth", "naive", "name", "napkin", "narrow", "nasty", "nation", "nature",
    "near", "neck", "need", "negative", "neglect", "neither", "nephew", "nerve", "nest", "net",
    "network", "neutral", "never", "news", "next", "nice", "night", "noble", "noise", "nominee",
    "noodle", "normal", "north", "nose", "notable", "note", "nothing", "notice", "novel", "now",
    "nuclear", "number", "nurse", "nut", "oak", "obey", "object", "oblige", "obscure", "observe",
    "obtain", "obvious", "occur", "ocean", "october", "odor", "off", "offer", "office", "often",
    "oil", "okay", "old", "olive", "olympic", "omit", "once", "one", "onion", "online",
    "only", "open", "opera", "opinion", "oppose", "option", "orange", "orbit", "orchard", "order",
    "ordinary", "organ", "orient", "original", "orphan", "ostrich", "other", "outdoor", "outer", "output",
    "outside", "oval", "oven", "over", "own", "owner", "oxygen", "oyster", "ozone", "pact",
    "paddle", "page", "pair", "palace", "palm", "panda", "panel", "panic", "panther", "paper",
    "parade", "parent", "park", "parrot", "party", "pass", "patch", "path", "patient", "patrol",
    "pattern", "pause", "pave", "payment", "peace", "peanut", "pear", "peasant", "pelican", "pen",
    "penalty", "pencil", "people", "pepper", "perfect", "permit", "person", "pet", "phone", "photo",
    "phrase", "physical", "piano", "picnic", "picture", "piece", "pig", "pigeon", "pill", "pilot",
    "pink", "pioneer", "pipe", "pistol", "pitch", "pizza", "place", "planet", "plastic", "plate",
    "play", "please", "pledge", "pluck", "plug", "plunge", "poem", "poet", "point", "polar",
    "pole", "police", "pond", "pony", "pool", "popular", "portion", "position", "possible", "post",
    "potato", "pottery", "poverty", "powder", "power", "practice", "praise", "predict", "prefer", "prepare",
    "present", "pretty", "prevent", "price", "pride", "primary", "print", "priority", "prison", "private",
    "prize", "problem", "process", "produce", "profit", "program", "project", "promote", "proof", "property",
    "prosper", "protect", "proud", "provide", "public", "pudding", "pull", "pulp", "pulse", "pumpkin",
    "punch", "pupil", "puppy", "purchase", "purity", "purpose", "purse", "push", "put", "puzzle",
    "pyramid", "quality", "quantum", "quarter", "question", "quick", "quit", "quiz", "quote", "rabbit",
    "raccoon", "race", "rack", "radar", "radio", "rail", "rain", "raise", "rally", "ramp",
    "ranch", "random", "range", "rapid", "rare", "rate", "rather", "raven", "raw", "razor",
    "ready", "real", "reason", "rebel", "rebuild", "recall", "receive", "recipe", "record", "recycle",
    "reduce", "reflect", "reform", "refuse", "region", "regret", "regular", "reject", "relax", "release",
    "relief", "rely", "remain", "remember", "remind", "remove", "render", "renew", "rent", "reopen",
    "repair", "repeat", "replace", "report", "require", "rescue", "resemble", "resist", "resource", "response",
    "result", "retire", "retreat", "return", "reunion", "reveal", "review", "reward", "rhythm", "rib",
    "ribbon", "rice", "rich", "ride", "ridge", "rifle", "right", "rigid", "ring", "riot",
    "ripple", "risk", "ritual", "rival", "river", "road", "roast", "robot", "robust", "rocket",
    "romance", "roof", "rookie", "room", "rose", "rotate", "rough", "round", "route", "royal",
    "rubber", "rude", "rug", "rule", "run", "runway", "rural", "sad", "saddle", "sadness",
    "safe", "sail", "salad", "salmon", "salon", "salt", "salute", "same", "sample", "sand",
    "satisfy", "satoshi", "sauce", "sausage", "save", "say", "scale", "scan", "scare", "scatter",
    "scene", "scheme", "school", "science", "scissors", "scorpion", "scout", "scrap", "screen", "script",
    "scrub", "sea", "search", "season", "seat", "second", "secret", "section", "security", "seed",
    "seek", "segment", "select", "sell", "seminar", "senior", "sense", "sentence", "series", "service",
    "session", "settle", "setup", "seven", "shadow", "shaft", "shallow", "share", "shed", "shell",
    "sheriff", "shield", "shift", "shine", "ship", "shiver", "shock", "shoe", "shoot", "shop",
    "short", "shoulder", "shove", "shrimp", "shrug", "shuffle", "shy", "sibling", "sick", "side",
    "siege", "sight", "sign", "silent", "silk", "silly", "silver", "similar", "simple", "since",
    "sing", "siren", "sister", "situate", "six", "size", "skate", "sketch", "ski", "skill",
    "skin", "skirt", "skull", "slab", "slam", "sleep", "slender", "slice", "slide", "slight",
    "slim", "slogan", "slot", "slow", "slush", "small", "smart", "smile", "smoke", "smooth",
    "snack", "snake", "snap", "sniff", "snow", "soap", "soccer", "social", "sock", "soda",
    "soft", "solar", "soldier", "solid", "solution", "solve", "someone", "song", "soon", "sorry",
    "sort", "soul", "sound", "soup", "source", "south", "space", "spare", "spatial", "spawn",
    "speak", "special", "speed", "spell", "spend", "sphere", "spice", "spider", "spike", "spin",
    "spirit", "split", "spoil", "sponsor", "spoon", "sport", "spot", "spray", "spread", "spring",
    "spy", "square", "squeeze", "squirrel", "stable", "stadium", "staff", "stage", "stairs", "stamp",
    "stand", "start", "state", "stay", "steak", "steel", "stem", "step", "stereo", "stick",
    "still", "sting", "stock", "stomach", "stone", "stool", "story", "stove", "strategy", "street",
    "strike", "strong", "struggle", "student", "stuff", "stumble", "style", "subject", "submit", "subway",
    "success", "such", "sudden", "suffer", "sugar", "suggest", "suit", "summer", "sun", "sunny",
    "sunset", "super", "supply", "supreme", "sure", "surface", "surge", "surprise", "surround", "survey",
    "suspect", "sustain", "swallow", "swamp", "swap", "swarm", "swear", "sweet", "swift", "swim",
    "swing", "switch", "sword", "symbol", "symptom", "syrup", "system", "table", "tackle", "tag",
    "tail", "talent", "talk", "tank", "tape", "target", "task", "taste", "tattoo", "taxi",
    "teach", "team", "tell", "ten", "tenant", "tennis", "tent", "term", "test", "text",
    "thank", "that", "theme", "then", "theory", "there", "they", "thing", "this", "thought",
    "three", "thrive", "throw", "thumb", "thunder", "ticket", "tide", "tiger", "tilt", "timber",
    "time", "tiny", "tip", "tired", "tissue", "title", "toast", "tobacco", "today", "toddler",
    "toe", "together", "toilet", "token", "tomato", "tomorrow", "tone", "tongue", "tonight", "tool",
    "tooth", "top", "topic", "topple", "torch", "tornado", "tortoise", "toss", "total", "tourist",
    "toward", "tower", "town", "toy", "track", "trade", "traffic", "tragic", "train", "transfer",
    "trap", "trash", "travel", "tray", "treat", "tree", "trend", "trial", "tribe", "trick",
    "trigger", "trim", "trip", "trophy", "trouble", "truck", "true", "truly", "trumpet", "trust",
    "truth", "try", "tube", "tuition", "tumble", "tuna", "tunnel", "turkey", "turn", "turtle",
    "twelve", "twenty", "twice", "twin", "twist", "two", "type", "typical", "ugly", "umbrella",
    "unable", "unaware", "uncle", "uncover", "under", "undo", "unfair", "unfold", "unhappy", "uniform",
    "unique", "unit", "universe", "unknown", "unlock", "until", "unusual", "unveil", "update", "upgrade",
    "uphold", "upon", "upper", "upset", "urban", "urge", "usage", "use", "used", "useful",
    "useless", "usual", "utility", "vacant", "vacuum", "vague", "valid", "valley", "valve", "van",
    "vanish", "vapor", "various", "vast", "vault", "vehicle", "velvet", "vendor", "venture", "venue",
    "verb", "verify", "version", "very", "vessel", "veteran", "viable", "vibrant", "vicious", "victory",
    "video", "view", "village", "vintage", "violin", "virtual", "virus", "visa", "visit", "visual",
    "vital", "vivid", "vocal", "voice", "void", "volcano", "volume", "vote", "voyage", "wage",
    "wagon", "wait", "walk", "wall", "walnut", "want", "warfare", "warm", "warrior", "wash",
    "wasp", "waste", "water", "wave", "way", "wealth", "weapon", "wear", "weasel", "weather",
    "web", "wedding", "weekend", "weird", "welcome", "west", "wet", "whale", "what", "wheat",
    "wheel", "when", "where", "whip", "whisper", "wide", "width", "wife", "wild", "will",
    "win", "window", "wine", "wing", "wink", "winner", "winter", "wire", "wisdom", "wise",
    "wish", "witness", "wolf", "woman", "wonder", "wood", "wool", "word", "work", "world",
    "worry", "worth", "wrap", "wreck", "wrestle", "wrist", "write", "wrong", "yard", "year",
    "yellow", "you", "young", "youth", "zebra", "zero", "zone", "zoo"
]

BIP39_OFFICIAL_SHA256 = "187db04a869dd9bc7be80d21a86497d692c0db6abd3aa8cb6be5d618ff757fae"


def verify_against_bip39_official():
    """Comprueba la lista embebida y la lista efectiva de mnemonic, offline."""
    if len(BIP39_OFFICIAL_WORDLIST) != 2048:
        print("ERROR: la wordlist embebida no contiene 2048 palabras.")
        return False

    official_hash = hashlib.sha256(
        "\n".join(BIP39_OFFICIAL_WORDLIST).encode("utf-8")
    ).hexdigest()

    if official_hash != BIP39_OFFICIAL_SHA256:
        print("ERROR: el hash de la wordlist embebida no coincide.")
        return False

    effective_wordlist = list(Mnemonic("english").wordlist)

    if effective_wordlist != list(BIP39_OFFICIAL_WORDLIST):
        print(
            "ERROR: la wordlist usada por mnemonic no coincide "
            "con la lista embebida esperada."
        )
        return False

    print(
        "Wordlist BIP39 embebida: hash local verificado (2048 palabras)."
    )
    print(
        "Wordlist efectiva de mnemonic: contenido y orden verificados."
    )
    return True


VALID_ENTROPY_BITS = {128, 160, 192, 224, 256}
VALID_WORD_COUNTS = {12, 15, 18, 21, 24}
DEFAULT_VECTORS_FILE = "vectors.json"
GAP_LIMIT = 5

DEFAULT_OUTPUT_PATH = "output/bip39_seed_report.json"

ENCRYPTED_REPORT_FORMAT = "bip39-seed-report-encrypted"
ENCRYPTED_REPORT_VERSION = 1
ENCRYPTED_REPORT_CIPHER = "AES-256-GCM"
ENCRYPTED_REPORT_KDF = "scrypt"

SCRYPT_N = 2**18
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_DKLEN = 32
SCRYPT_SALT_BYTES = 16
AES_GCM_NONCE_BYTES = 12
SCRYPT_MAXMEM = 512 * 1024 * 1024

def normalize_text(text):
    return unicodedata.normalize("NFKD", text)


def bytes_to_binary(data):
    return "".join(f"{byte:08b}" for byte in data)


def validate_entropy_length(bit_len):
    if bit_len not in VALID_ENTROPY_BITS:
        raise ValueError("La entropía debe ser 128, 160, 192, 224 o 256 bits.")


def entropy_checksum_bits(entropy):
    checksum_len = (len(entropy) * 8) // 32
    digest_bits = bytes_to_binary(hashlib.sha256(entropy).digest())
    return digest_bits[:checksum_len]


def binary_to_bytes(binary_str):
    clean = binary_str.strip().replace(" ", "")
    if not clean:
        raise ValueError("La entropía binaria está vacía.")
    if any(ch not in "01" for ch in clean):
        raise ValueError("La entropía binaria solo puede contener 0 y 1.")
    validate_entropy_length(len(clean))
    return int(clean, 2).to_bytes(len(clean) // 8, "big")


def hex_to_bytes(hex_str):
    clean = hex_str.strip().replace(" ", "").lower()
    if not clean:
        raise ValueError("La entropía hexadecimal está vacía.")
    if clean.startswith("0x"):
        clean = clean[2:]
    if len(clean) % 2 != 0:
        raise ValueError("La entropía hexadecimal debe tener longitud par.")
    entropy = bytes.fromhex(clean)
    validate_entropy_length(len(entropy) * 8)
    return entropy


def generate_entropy(words):
    if words not in VALID_WORD_COUNTS:
        raise ValueError("BIP39 solo admite 12, 15, 18, 21 o 24 palabras.")
    return os.urandom({12: 16, 15: 20, 18: 24, 21: 28, 24: 32}[words])


def entropy_to_mnemonic(entropy):
    return Mnemonic("english").to_mnemonic(entropy)


def validate_mnemonic_text(mnemonic):
    phrase = normalize_text(mnemonic).strip()
    words = phrase.split()
    if len(words) not in VALID_WORD_COUNTS:
        raise ValueError("La mnemonic debe tener 12, 15, 18, 21 o 24 palabras.")
    mnemo = Mnemonic("english")
    if not mnemo.check(phrase):
        raise ValueError("La mnemonic no es válida o su checksum no coincide.")
    return phrase


def mnemonic_to_entropy(mnemonic):
    phrase = validate_mnemonic_text(mnemonic)
    mnemo = Mnemonic("english")
    words = phrase.split()
    indexes = [mnemo.wordlist.index(word) for word in words]
    bits = "".join(f"{idx:011b}" for idx in indexes)
    entropy_bits = {12: 128, 15: 160, 18: 192, 21: 224, 24: 256}[len(words)]
    checksum_bits = entropy_bits // 32
    entropy_bin = bits[:entropy_bits]
    embedded_checksum = bits[entropy_bits:entropy_bits + checksum_bits]
    entropy = int(entropy_bin, 2).to_bytes(entropy_bits // 8, "big")
    expected_checksum = entropy_checksum_bits(entropy)
    return {
        "entropy": entropy,
        "entropy_bin": entropy_bin,
        "entropy_hex": entropy.hex(),
        "embedded_checksum": embedded_checksum,
        "expected_checksum": expected_checksum,
        "checksum_valid": embedded_checksum == expected_checksum,
    }


def mnemonic_seed(mnemonic, passphrase=""):
    return Bip39SeedGenerator(normalize_text(mnemonic)).Generate(normalize_text(passphrase))


def bip32_master_key(seed):
    I = hmac.new(key=b"Bitcoin seed", msg=seed, digestmod=hashlib.sha512).digest()
    return I[:32].hex(), I[32:].hex()


def select_network(network):
    if network == "mainnet":
        return {
            "bip44": Bip44Coins.BITCOIN,
            "bip49": Bip49Coins.BITCOIN,
            "bip84": Bip84Coins.BITCOIN,
            "bip86": Bip86Coins.BITCOIN,
            "coin_type": "0'",
        }
    if network == "testnet":
        return {
            "bip44": Bip44Coins.BITCOIN_TESTNET,
            "bip49": Bip49Coins.BITCOIN_TESTNET,
            "bip84": Bip84Coins.BITCOIN_TESTNET,
            "bip86": Bip86Coins.BITCOIN_TESTNET,
            "coin_type": "1'",
        }
    raise ValueError("La red debe ser mainnet o testnet.")


def derive_addresses_bip44(seed, coin, coin_type, gap_limit=GAP_LIMIT):
    root = Bip44.FromSeed(seed, coin)
    account = root.Purpose().Coin().Account(0)
    change = account.Change(Bip44Changes.CHAIN_EXT)
    addresses = []
    for i in range(gap_limit):
        addr = change.AddressIndex(i)
        addresses.append({
            "index": i,
            "path": f"m/44'/{coin_type}/0'/0/{i}",
            "address": addr.PublicKey().ToAddress(),
            "private_key_wif": addr.PrivateKey().ToWif(),
            "public_key_hex": addr.PublicKey().RawCompressed().ToHex(),
        })
    return {
        "path_template": f"m/44'/{coin_type}/0'/0/i",
        "xpub": account.PublicKey().ToExtended(),
        "addresses": addresses,
        "address_type": "P2PKH",
    }


def derive_addresses_bip49(seed, coin, coin_type, gap_limit=GAP_LIMIT):
    root = Bip49.FromSeed(seed, coin)
    account = root.Purpose().Coin().Account(0)
    change = account.Change(Bip44Changes.CHAIN_EXT)
    addresses = []
    for i in range(gap_limit):
        addr = change.AddressIndex(i)
        addresses.append({
            "index": i,
            "path": f"m/49'/{coin_type}/0'/0/{i}",
            "address": addr.PublicKey().ToAddress(),
            "private_key_wif": addr.PrivateKey().ToWif(),
            "public_key_hex": addr.PublicKey().RawCompressed().ToHex(),
        })
    return {
        "path_template": f"m/49'/{coin_type}/0'/0/i",
        "ypub": account.PublicKey().ToExtended(),
        "addresses": addresses,
        "address_type": "P2WPKH-P2SH",
    }


def derive_addresses_bip84(seed, coin, coin_type, gap_limit=GAP_LIMIT):
    root = Bip84.FromSeed(seed, coin)
    account = root.Purpose().Coin().Account(0)
    change = account.Change(Bip44Changes.CHAIN_EXT)
    addresses = []
    for i in range(gap_limit):
        addr = change.AddressIndex(i)
        addresses.append({
            "index": i,
            "path": f"m/84'/{coin_type}/0'/0/{i}",
            "address": addr.PublicKey().ToAddress(),
            "private_key_wif": addr.PrivateKey().ToWif(),
            "public_key_hex": addr.PublicKey().RawCompressed().ToHex(),
        })
    return {
        "path_template": f"m/84'/{coin_type}/0'/0/i",
        "zpub": account.PublicKey().ToExtended(),
        "addresses": addresses,
        "address_type": "P2WPKH",
    }


def derive_addresses_bip86(seed, coin, coin_type, gap_limit=GAP_LIMIT):
    root = Bip86.FromSeed(seed, coin)
    account = root.Purpose().Coin().Account(0)
    change = account.Change(Bip44Changes.CHAIN_EXT)
    addresses = []
    for i in range(gap_limit):
        addr = change.AddressIndex(i)
        addresses.append({
            "index": i,
            "path": f"m/86'/{coin_type}/0'/0/{i}",
            "address": addr.PublicKey().ToAddress(),
            "private_key_wif": addr.PrivateKey().ToWif(),
            "public_key_hex": addr.PublicKey().RawCompressed().ToHex(),
        })
    return {
        "path_template": f"m/86'/{coin_type}/0'/0/i",
        "addresses": addresses,
        "address_type": "P2TR",
    }


def _canonical_encryption_aad(
    report_format: str,
    version: int,
    cipher_name: str,
    kdf_name: str,
    n: int,
    r: int,
    p: int,
    dklen: int,
) -> bytes:
    metadata = {
        "cipher": cipher_name,
        "format": report_format,
        "kdf": {
            "dklen": dklen,
            "n": n,
            "name": kdf_name,
            "p": p,
            "r": r,
        },
        "version": version,
    }
    return json.dumps(
        metadata,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _derive_scrypt_key(
    password: str,
    salt: bytes,
    n: int,
    r: int,
    p: int,
    dklen: int,
) -> bytes:
    if not isinstance(password, str) or not password:
        raise ValueError("La contraseña de cifrado no puede estar vacía.")

    if len(salt) != SCRYPT_SALT_BYTES:
        raise ValueError("El salt del archivo cifrado es inválido.")

    try:
        return hashlib.scrypt(
            unicodedata.normalize("NFKD", password).encode("utf-8"),
            salt=salt,
            n=n,
            r=r,
            p=p,
            dklen=dklen,
            maxmem=SCRYPT_MAXMEM,
        )
    except ValueError as exc:
        raise RuntimeError(
            "No fue posible ejecutar scrypt con los parámetros del archivo."
        ) from exc


def _encrypt_report_content(content: str, password: str) -> str:
    if not CRYPTO_AVAILABLE:
        raise RuntimeError(
            "La librería cryptography es requerida para cifrar archivos."
        )

    salt = os.urandom(SCRYPT_SALT_BYTES)
    nonce = os.urandom(AES_GCM_NONCE_BYTES)
    aad = _canonical_encryption_aad(
        ENCRYPTED_REPORT_FORMAT,
        ENCRYPTED_REPORT_VERSION,
        ENCRYPTED_REPORT_CIPHER,
        ENCRYPTED_REPORT_KDF,
        SCRYPT_N,
        SCRYPT_R,
        SCRYPT_P,
        SCRYPT_DKLEN,
    )
    key = _derive_scrypt_key(
        password,
        salt,
        SCRYPT_N,
        SCRYPT_R,
        SCRYPT_P,
        SCRYPT_DKLEN,
    )
    ciphertext = AESGCM(key).encrypt(
        nonce,
        content.encode("utf-8"),
        aad,
    )

    container = {
        "cipher": {
            "name": ENCRYPTED_REPORT_CIPHER,
            "nonce_b64": base64.b64encode(nonce).decode("ascii"),
        },
        "ciphertext_b64": base64.b64encode(ciphertext).decode("ascii"),
        "format": ENCRYPTED_REPORT_FORMAT,
        "kdf": {
            "dklen": SCRYPT_DKLEN,
            "n": SCRYPT_N,
            "name": ENCRYPTED_REPORT_KDF,
            "p": SCRYPT_P,
            "r": SCRYPT_R,
            "salt_b64": base64.b64encode(salt).decode("ascii"),
        },
        "version": ENCRYPTED_REPORT_VERSION,
    }
    return json.dumps(
        container,
        ensure_ascii=True,
        indent=2,
        sort_keys=True,
    ) + "\n"


def _decrypt_versioned_report(
    encrypted_content: str,
    password: str,
) -> str:
    try:
        container = json.loads(encrypted_content)
    except json.JSONDecodeError as exc:
        raise ValueError("El archivo cifrado no contiene JSON válido.") from exc

    if not isinstance(container, dict):
        raise ValueError("El contenedor cifrado debe ser un objeto JSON.")

    if container.get("format") != ENCRYPTED_REPORT_FORMAT:
        raise ValueError("Formato de contenedor cifrado no reconocido.")

    version = container.get("version")
    if type(version) is not int or version != ENCRYPTED_REPORT_VERSION:
        raise ValueError(
            f"Versión de contenedor no soportada: {version!r}."
        )

    cipher_data = container.get("cipher")
    kdf_data = container.get("kdf")
    ciphertext_b64 = container.get("ciphertext_b64")

    if not isinstance(cipher_data, dict):
        raise ValueError("Metadatos de cifrado inválidos.")

    if not isinstance(kdf_data, dict):
        raise ValueError("Metadatos KDF inválidos.")

    if cipher_data.get("name") != ENCRYPTED_REPORT_CIPHER:
        raise ValueError("Algoritmo de cifrado no soportado.")

    if kdf_data.get("name") != ENCRYPTED_REPORT_KDF:
        raise ValueError("KDF no soportada.")

    n = kdf_data.get("n")
    r = kdf_data.get("r")
    p = kdf_data.get("p")
    dklen = kdf_data.get("dklen")

    parameters = (n, r, p, dklen)

    if any(type(value) is not int for value in parameters):
        raise ValueError("Los parámetros scrypt deben ser enteros.")

    if parameters != (SCRYPT_N, SCRYPT_R, SCRYPT_P, SCRYPT_DKLEN):
        raise ValueError(
            "Perfil scrypt no admitido para este formato de reporte."
        )

    try:
        salt = base64.b64decode(
            kdf_data["salt_b64"],
            validate=True,
        )
        nonce = base64.b64decode(
            cipher_data["nonce_b64"],
            validate=True,
        )
        ciphertext = base64.b64decode(
            ciphertext_b64,
            validate=True,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            "El contenedor cifrado tiene datos base64 inválidos."
        ) from exc

    if len(nonce) != AES_GCM_NONCE_BYTES:
        raise ValueError("El nonce AES-GCM tiene longitud inválida.")

    aad = _canonical_encryption_aad(
        ENCRYPTED_REPORT_FORMAT,
        version,
        cipher_data["name"],
        kdf_data["name"],
        n,
        r,
        p,
        dklen,
    )
    key = _derive_scrypt_key(
        password,
        salt,
        n,
        r,
        p,
        dklen,
    )

    try:
        plaintext = AESGCM(key).decrypt(
            nonce,
            ciphertext,
            aad,
        )
    except InvalidTag as exc:
        raise ValueError(
            "No se pudo descifrar el reporte. La contraseña es incorrecta "
            "o el archivo fue alterado."
        ) from exc

    try:
        return plaintext.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "El contenido descifrado no es UTF-8 válido."
        ) from exc


def _decrypt_legacy_report(
    encrypted_content: str,
    password: str,
) -> str:
    print(
        "ADVERTENCIA: este archivo usa el formato histórico con SHA-256 "
        "directo de contraseña, sin una KDF resistente. Descífralo solo "
        "para migrarlo y vuelve a exportarlo en el formato actual."
    )

    try:
        encrypted_data = base64.b64decode(
            encrypted_content[len("ENCRYPTED:"):],
            validate=True,
        )
    except ValueError as exc:
        raise ValueError(
            "El archivo histórico tiene base64 inválido."
        ) from exc

    if len(encrypted_data) <= AES_GCM_NONCE_BYTES:
        raise ValueError("El archivo histórico está incompleto.")

    nonce = encrypted_data[:AES_GCM_NONCE_BYTES]
    ciphertext = encrypted_data[AES_GCM_NONCE_BYTES:]
    legacy_key = hashlib.sha256(password.encode("utf-8")).digest()

    try:
        plaintext = AESGCM(legacy_key).decrypt(
            nonce,
            ciphertext,
            None,
        )
    except InvalidTag as exc:
        raise ValueError(
            "No se pudo descifrar el archivo histórico. La contraseña "
            "es incorrecta o el archivo fue alterado."
        ) from exc

    try:
        return plaintext.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "El contenido histórico descifrado no es UTF-8 válido."
        ) from exc


def decrypt_report_content(encrypted_content: str, password: str) -> str:
    if not CRYPTO_AVAILABLE:
        raise RuntimeError(
            "La librería cryptography es requerida para descifrar archivos."
        )

    if not isinstance(encrypted_content, str):
        raise TypeError("El contenido cifrado debe ser texto.")

    if encrypted_content.startswith("ENCRYPTED:"):
        return _decrypt_legacy_report(encrypted_content, password)

    return _decrypt_versioned_report(encrypted_content, password)


def write_secure_file(
    path: str,
    content: str,
    encrypt: bool = True,
    password: str | None = None,
) -> None:
    destination = pathlib.Path(path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    if encrypt:
        if not password:
            raise ValueError(
                "Se requiere una contraseña para cifrar el reporte."
            )
        content_to_write = _encrypt_report_content(content, password)
    else:
        content_to_write = content

    fd, temp_name = tempfile.mkstemp(
        prefix=destination.name + ".",
        dir=str(destination.parent),
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file_handle:
            file_handle.write(content_to_write)
            file_handle.flush()
            os.fsync(file_handle.fileno())

        try:
            os.chmod(temp_name, 0o600)
        except OSError:
            pass

        os.replace(temp_name, destination)

        try:
            os.chmod(destination, 0o600)
        except OSError:
            pass
    finally:
        if os.path.exists(temp_name):
            try:
                os.remove(temp_name)
            except OSError:
                pass


def decrypt_file_content(encrypted_content, password):
    """Alias de compatibilidad; delega al descifrador actual."""
    return decrypt_report_content(encrypted_content, password)


def generate_sequential_path(base_path):
    destination = pathlib.Path(base_path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        return destination
    stem, suffix, parent = destination.stem, destination.suffix, destination.parent
    counter = 1
    while True:
        new_path = parent / f"{stem}_{counter:03d}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1


def audit_passphrase(passphrase):
    normalized = normalize_text(passphrase)
    utf8_bytes = normalized.encode("utf-8")
    return {
        "present": len(normalized) > 0,
        "characters": len(normalized),
        "utf8_bytes": len(utf8_bytes),
        "unique_characters": len(set(normalized)),
        "has_lowercase": any(c.islower() for c in normalized),
        "has_uppercase": any(c.isupper() for c in normalized),
        "has_digits": any(c.isdigit() for c in normalized),
        "has_symbols": any(not c.isalnum() and not c.isspace() for c in normalized),
        "has_spaces": any(c.isspace() for c in normalized),
        "classification": "vacía" if len(normalized) == 0 else "proporcionada por el usuario",
        "security_note": "No añade incertidumbre adicional." if len(normalized) == 0 else "No es posible calcular su entropía real sin conocer el proceso aleatorio utilizado para elegirla.",
    }


def attempt_clear_history():
    try:
        import readline
        readline.clear_history()
    except Exception:
        pass


def get_secure_input(prompt, allow_empty=False):
    while True:
        value = read_hidden_secret(prompt)
        if value or allow_empty:
            return value
        print("⚠️  Este campo no puede estar vacío. Intenta nuevamente.")


def find_last_word(incomplete_phrase):
    mnemo = Mnemonic("english")
    wordlist = mnemo.wordlist
    words = incomplete_phrase.strip().split()
    if len(words) == 11:
        entropy_bits = 128
    elif len(words) == 23:
        entropy_bits = 256
    else:
        raise ValueError("Solo se pueden calcular mnemonics de 11→12 o 23→24 palabras.")
    checksum_bits = entropy_bits // 32
    valid_candidates = []
    print(f"Buscando palabras para completar mnemonic de {len(words)} palabras...")
    print(f"Checksum de {checksum_bits} bits = {2**checksum_bits} posibilidades teóricas")
    for candidate_word in wordlist:
        if mnemo.check(incomplete_phrase + " " + candidate_word):
            valid_candidates.append(candidate_word)
    return valid_candidates


def get_secure_mnemonic():
    print("\n📝 Ingresa la mnemonic (las palabras se ocultarán mientras escribes):")
    print("   Escribe todas las palabras separadas por espacios.")
    print("   Presiona Enter cuando termines.\n")
    return get_secure_input("Mnemonic: ").strip()


def get_secure_entropy_hex():
    print("\n🔢 Ingresa la entropía hexadecimal (oculto):")
    print("   Debe ser 32, 40, 48, 56 o 64 caracteres hexadecimales.")
    print("   Presiona Enter cuando termines.\n")
    return get_secure_input("Entropy hex: ").strip()


def get_secure_entropy_bin():
    print("\n🔢 Ingresa la entropía binaria (oculto):")
    print("   Debe ser 128, 160, 192, 224 o 256 bits (solo 0 y 1).")
    print("   Presiona Enter cuando termines.\n")
    return get_secure_input("Entropy bin: ").strip()


def get_secure_passphrase():
    print("\n🔐 Ingresa la passphrase BIP39 (opcional, oculto):")
    print("   Presiona Enter en ambos campos para dejarla vacía.\n")

    return get_confirmed_secret(
        prompt="Passphrase: ",
        confirmation_prompt="Confirmar passphrase: ",
        normalizer=normalize_text,
    )


def analizar_indicadores_mnemonic(mnemonic):
    """
    Valida formato BIP39 e informa indicadores superficiales de patrón.

    Esta función no estima entropy criptográfica, no certifica
    imprevisibilidad y no puede determinar cómo se generó históricamente
    la mnemonic.
    """
    mnemo = Mnemonic("english")
    phrase = normalize_text(mnemonic.strip())
    words = phrase.split()
    word_count = len(words)

    if word_count not in VALID_WORD_COUNTS:
        return {
            "valid": False,
            "error": "Número de palabras inválido",
        }

    if not mnemo.check(phrase):
        return {
            "valid": False,
            "error": "Checksum BIP39 inválido",
        }

    indexes = [mnemo.wordlist.index(word) for word in words]
    unique_words = len(set(words))
    repeated_total = word_count - unique_words
    repeated_word_count = sum(
        1 for count in Counter(words).values() if count > 1
    )
    consecutive_indexes = sum(
        1
        for index in range(1, len(indexes))
        if indexes[index] == indexes[index - 1] + 1
    )
    consecutive_repetitions = sum(
        1
        for index in range(1, len(words))
        if words[index] == words[index - 1]
    )

    indicators = []

    if repeated_total:
        indicators.append(
            "Se observaron palabras repetidas; esto puede ocurrir "
            "en una mnemonic aleatoria válida."
        )

    if consecutive_indexes:
        indicators.append(
            "Se observaron índices consecutivos en la wordlist; "
            "esto por sí solo no determina la calidad de la entropy."
        )

    if not indicators:
        indicators.append(
            "No se detectaron repeticiones ni secuencias consecutivas "
            "simples."
        )

    return {
        "valid": True,
        "word_count": word_count,
        "unique_words": unique_words,
        "repeated_total": repeated_total,
        "repeated_word_count": repeated_word_count,
        "consecutive_indexes": consecutive_indexes,
        "consecutive_repetitions": consecutive_repetitions,
        "indicators": indicators,
        "limitation": (
            "Estos indicadores son superficiales. No estiman ni "
            "certifican entropy criptográfica, imprevisibilidad ni la "
            "calidad histórica de la fuente que generó la mnemonic."
        ),
    }

def resolve_input(args, interactive=False):
    if interactive:
        has_words = args.words is not None
        has_entropy_bin = bool(args.entropy_bin)
        has_entropy_hex = bool(args.entropy_hex)
        has_mnemonic = bool(args.mnemonic)
        has_mnemonic_incomplete = bool(args.mnemonic_incomplete)

        input_count = sum([has_words, has_entropy_bin, has_entropy_hex, has_mnemonic, has_mnemonic_incomplete])

        if input_count == 0:
            print("\nSelecciona el tipo de entrada:")
            print("  [1] Generar nueva mnemonic aleatoria")
            print("  [2] Ingresar entropía hexadecimal")
            print("  [3] Ingresar entropía binaria")
            print("  [4] Ingresar mnemonic existente")
            print("  [5] Calcular última palabra (11 o 23 palabras)")
            print()

            while True:
                choice = input("Opción [1-5]: ").strip()
                if choice == '1':
                    print("\nSelecciona la longitud de la mnemonic:")
                    print("  [1] 12 palabras (128 bits - estándar, recomendado)")
                    print("  [2] 24 palabras (256 bits de entropía de entrada)")
                    print()
                    while True:
                        length_choice = input("Opción [1-2]: ").strip()
                        if length_choice == '1':
                            args.words = 12
                            break
                        elif length_choice == '2':
                            args.words = 24
                            break
                        else:
                            print("❌ Opción inválida. Ingresa 1 o 2.")
                    break
                elif choice == '2':
                    args.entropy_hex = get_secure_entropy_hex()
                    break
                elif choice == '3':
                    args.entropy_bin = get_secure_entropy_bin()
                    break
                elif choice == '4':
                    args.mnemonic = get_secure_mnemonic()
                    break
                elif choice == '5':
                    args.mnemonic_incomplete = get_secure_mnemonic()
                    break
                else:
                    print("❌ Opción inválida. Ingresa un número entre 1 y 5.")

        if args.network is None:
            print("\nSelecciona la red Bitcoin:")
            print("  [1] Mainnet (Bitcoin principal - predeterminada)")
            print("  [2] Testnet (Bitcoin de pruebas)")

            while True:
                network_choice = input("Opción [1-2]: ").strip()

                if network_choice == "1":
                    args.network = "mainnet"
                    break
                elif network_choice == "2":
                    args.network = "testnet"
                    break
                else:
                    print("Opción inválida. Ingresa 1 o 2.")

        if not args.passphrase:
            args.passphrase = get_secure_passphrase()

    if args.network is None:
        args.network = "mainnet"


    if sum(1 for x in [args.words, args.entropy_bin, args.entropy_hex, args.mnemonic, args.mnemonic_incomplete] if x) != 1:
        raise ValueError("Debes proporcionar exactamente una entrada entre -w/--words, --entropy-bin, --entropy-hex, --mnemonic o --mnemonic-incomplete.")

    if args.entropy_bin:
        entropy = binary_to_bytes(args.entropy_bin)
        mnemonic = entropy_to_mnemonic(entropy)
        recovered = {
            "entropy": entropy,
            "entropy_bin": bytes_to_binary(entropy),
            "entropy_hex": entropy.hex(),
            "checksum_valid": True,
        }
        return entropy, mnemonic, recovered, "entropy_bin"

    if args.entropy_hex:
        entropy = hex_to_bytes(args.entropy_hex)
        mnemonic = entropy_to_mnemonic(entropy)
        recovered = {
            "entropy": entropy,
            "entropy_bin": bytes_to_binary(entropy),
            "entropy_hex": entropy.hex(),
            "checksum_valid": True,
        }
        return entropy, mnemonic, recovered, "entropy_hex"

    if args.mnemonic:
        mnemonic = validate_mnemonic_text(args.mnemonic)
        recovered = mnemonic_to_entropy(mnemonic)
        return recovered["entropy"], mnemonic, recovered, "mnemonic"

    if args.mnemonic_incomplete:
        incomplete_phrase = normalize_text(args.mnemonic_incomplete).strip()
        candidates = find_last_word(incomplete_phrase)

        if not candidates:
            raise ValueError("No se encontró ninguna palabra válida. Verifica que las palabras sean correctas.")

        print(f"\n✅ Se encontraron {len(candidates)} palabra(s) posible(s):\n")
        for i, word in enumerate(candidates, start=1):
            print(f"  [{i:2d}] {word}")
        print()

        if len(candidates) == 1:
            mnemonic = incomplete_phrase + " " + candidates[0]
            print("✅ Única palabra encontrada. Continuando...\n")
        else:
            print(f"⚠️  Hay {len(candidates)} palabras posibles.\n")
            print("INSTRUCCIONES:")
            print(
                "1. Compara cada candidato con una fuente de recuperación "
                "o un verificador independiente de confianza"
            )
            print("2. Ingresa el número de la palabra correcta (1 al {max_idx})".format(max_idx=len(candidates)))
            print("3. O ingresa 'q' para cancelar\n")

            while True:
                try:
                    user_input = input("Selecciona una palabra [1-{max_idx}]: ".format(max_idx=len(candidates))).strip()
                    if user_input.lower() == 'q':
                        print("\n❌ Operación cancelada por el usuario.")
                        sys.exit(0)
                    try:
                        selection = int(user_input)
                        if 1 <= selection <= len(candidates):
                            selected_word = candidates[selection - 1]
                            mnemonic = incomplete_phrase + " " + selected_word
                            print(f"\n✅ Palabra seleccionada: {selected_word}")
                            print(
                                "ADVERTENCIA: confirma la palabra elegida mediante una fuente "
                                "independiente antes de tratar el resultado como recuperación válida."
                            )
                            break
                        else:
                            print(f"❌ Número inválido. Ingresa un número entre 1 y {len(candidates)}.")
                    except ValueError:
                        print("❌ Entrada inválida. Ingresa un número o 'q' para cancelar.")                
                except EOFError as exc:
                    raise RuntimeError(
                        "No se puede seleccionar una palabra candidata sin interacción. "
                        "Ejecuta el proceso en una TTY y selecciona explícitamente un "
                        "candidato, o cancela la operación."
                    ) from exc

        recovered = mnemonic_to_entropy(mnemonic)
        return recovered["entropy"], mnemonic, recovered, "mnemonic_incomplete"

    entropy = generate_entropy(args.words)
    mnemonic = entropy_to_mnemonic(entropy)

    recovered = {
        "entropy": entropy,
        "entropy_bin": bytes_to_binary(entropy),
        "entropy_hex": entropy.hex(),
        "checksum_valid": True,
    }
    return entropy, mnemonic, recovered, "words"


def build_context(args, interactive=False):
    entropy, mnemonic, recovered, input_mode = resolve_input(args, interactive)
    seed = mnemonic_seed(mnemonic, args.passphrase)

    bip32_master, bip32_chain_code = bip32_master_key(seed)
    bip32_root_key = bip32_master + bip32_chain_code

    if args.network not in ("mainnet", "testnet"):
        raise RuntimeError(
            f"Error interno: red no resuelta antes de derivar: {args.network!r}"
        )

    network = select_network(args.network)

    derivations = {
        "BIP44": derive_addresses_bip44(seed, network["bip44"], network["coin_type"], GAP_LIMIT),
        "BIP49": derive_addresses_bip49(seed, network["bip49"], network["coin_type"], GAP_LIMIT),
        "BIP84": derive_addresses_bip84(seed, network["bip84"], network["coin_type"], GAP_LIMIT),
        "BIP86": derive_addresses_bip86(seed, network["bip86"], network["coin_type"], GAP_LIMIT),
    }

    context = {
        "coin_type_label": "Bitcoin",
        "network": args.network,
        "input_mode": input_mode,
        "entropy_bits": len(entropy) * 8,
        "entropy_bin": recovered["entropy_bin"],
        "entropy_hex": recovered["entropy_hex"],
        "entropy_checksum": entropy_checksum_bits(entropy),
        "checksum_valid": recovered["checksum_valid"],
        "mnemonic": mnemonic,
        "mnemonic_valid": True,
        "passphrase_used": bool(args.passphrase),
        "bip39_seed_hex": seed.hex(),
        "bip32_root_key": bip32_root_key,
        "bip32_master_key": bip32_master,
        "bip32_chain_code": bip32_chain_code,
        "derivations": derivations,
        "gap_limit": GAP_LIMIT,
    }

    indicadores = analizar_indicadores_mnemonic(mnemonic)
    context["indicadores_mnemonic"] = indicadores

    if args.audit_passphrase:
        context["passphrase_audit"] = audit_passphrase(args.passphrase)

    return context


def format_report(data, terminal_mode=True, hide_sensitive=True, show_all=False):
    if show_all:
        hide_sensitive = False

    lines = [
        "\nOffline BIP39 Seed Report",
        "NO ES UNA WALLET: no consulta red, no firma ni transmite transacciones.",
        "NO USAR CON FONDOS REALES: el proyecto no está auditado para producción.",
        "========================================",
        f"Coin type       : {data['coin_type_label']}",
        f"Input mode      : {data['input_mode']}",
        f"Network         : {data['network']}",
    ]

    if not hide_sensitive or not terminal_mode:
        lines.extend([
            f"Entropy bits    : {data['entropy_bits']}",
            f"Entropy binary  : {data['entropy_bin']}",
            f"Entropy hex     : {data['entropy_hex']}",
            f"Checksum BIP39  : {data['entropy_checksum']}",
            f"Checksum valid  : {data['checksum_valid']}",
        ])
    else:
        lines.extend([
            "Entropy bits    : [OCULTO - ver archivo desencriptado]",
            "Entropy binary  : [OCULTO - ver archivo desencriptado]",
            "Entropy hex     : [OCULTO - ver archivo desencriptado]",
            "Checksum BIP39  : [OCULTO - ver archivo desencriptado]",
            "Checksum valid  : [OCULTO - ver archivo desencriptado]",
        ])

    if "indicadores_mnemonic" in data:
        ind = data["indicadores_mnemonic"]

        lines.extend([
            "----------------------------------------",
            "VALIDACIÓN BIP39 E INDICADORES DE PATRÓN",
            "----------------------------------------",
        ])

        if not ind["valid"]:
            lines.append(
                f"Validación BIP39: inválida ({ind['error']})"
            )
        else:
            lines.extend([
                "Validación BIP39: válida",
                f"Palabras: {ind['word_count']}",
                (
                    f"Palabras únicas: "
                    f"{ind['unique_words']}/{ind['word_count']}"
                ),
                f"Repeticiones totales: {ind['repeated_total']}",
                (
                    "Palabras con repeticiones: "
                    f"{ind['repeated_word_count']}"
                ),
                (
                    "Índices consecutivos observados: "
                    f"{ind['consecutive_indexes']}"
                ),
                (
                    "Repeticiones consecutivas: "
                    f"{ind['consecutive_repetitions']}"
                ),
                "Indicadores:",
            ])

            for message in ind["indicators"]:
                lines.append(f"- {message}")

            lines.extend([
                "Límite:",
                ind["limitation"],
            ])

            if data.get("input_mode") == "mnemonic":
                lines.extend([
                    "Origen de entropy: desconocido.",
                    (
                        "La validación BIP39 confirma formato y checksum, "
                        "pero no puede certificar que la mnemonic importada "
                        "fuera generada con una fuente aleatoria segura."
                    ),
                ])

    if "passphrase_audit" in data:
        pa = data["passphrase_audit"]
        lines.extend([
            "----------------------------------------",
            "AUDITORÍA DE PASSPHRASE",
            "----------------------------------------",
            f"Estado                 : {'presente' if pa['present'] else 'vacía'}",
            f"Caracteres             : {pa['characters']}",
            f"Bytes UTF-8            : {pa['utf8_bytes']}",
            f"Caracteres distintos   : {pa['unique_characters']}",
            f"Minúsculas             : {pa['has_lowercase']}",
            f"Mayúsculas             : {pa['has_uppercase']}",
            f"Dígitos                : {pa['has_digits']}",
            f"Símbolos               : {pa['has_symbols']}",
            f"Espacios               : {pa['has_spaces']}",
            f"Clasificación          : {pa['classification']}",
            f"Nota                   : {pa['security_note']}",
        ])

    lines.extend([
        "----------------------------------------",
        "Mnemonic",
        "----------------------------------------",
    ])

    if not hide_sensitive or not terminal_mode:
        lines.append(data["mnemonic"])
    else:
        word_count = len(data["mnemonic"].split())
        lines.append(f"[{word_count} palabras - OCULTO - ver archivo desencriptado]")

    lines.extend([
        f"\nMnemonic valid   : {data['mnemonic_valid']}",
        f"Passphrase used  : {data['passphrase_used']}",
    ])

    if not hide_sensitive or not terminal_mode:
        lines.extend([
            f"BIP39 seed hex   : {data['bip39_seed_hex']}",
            f"BIP32 root key   : {data['bip32_root_key']}",
        ])
    else:
        lines.extend([
            "BIP39 seed hex   : [OCULTO - ver archivo desencriptado]",
            "BIP32 root key   : [OCULTO - ver archivo desencriptado]",
        ])

    lines.append("----------------------------------------")

    gap = data.get("gap_limit", GAP_LIMIT)

    for name, item in data["derivations"].items():
        address_type = item.get("address_type", "")
        display_name = f"[{name}] ({address_type})" if address_type else f"[{name}]"
        
        lines.extend([
            display_name,
            f"Path template    : {item['path_template']}",
            f"GAP limit       : {gap}",
        ])

        if "xpub" in item:
            lines.append(f"Extended public key : {item['xpub']}")
        if "ypub" in item:
            lines.append(f"Extended public key : {item['ypub']}")
        if "zpub" in item:
            lines.append(f"Extended public key : {item['zpub']}")

        if terminal_mode:
            first = item["addresses"][0]
            if not hide_sensitive or not terminal_mode:
                lines.extend([
                    f"Address (0)      : {first['address']}",
                    f"Private key WIF   : {first['private_key_wif']}",
                    f"Public key hex    : {first['public_key_hex']}",
                ])
            else:
                lines.append(f"Address (0)      : {first['address']}")
                lines.append("Private key WIF   : [OCULTO - ver archivo desencriptado]")
                lines.append("Public key hex    : [OCULTO - ver archivo desencriptado]")
        else:
            for addr_info in item["addresses"]:
                lines.extend([
                    f"Index            : {addr_info['index']}",
                    f"Path             : {addr_info['path']}",
                    f"Address          : {addr_info['address']}",
                    f"Private key WIF   : {addr_info['private_key_wif']}",
                    f"Public key hex    : {addr_info['public_key_hex']}",
                ])

        lines.append("----------------------------------------")

    lines.extend([
        "ADVERTENCIA, este script:",
        "no puede certificar que una entropía manual ingresada por el usuario sea imprevisible.",
        "no puede certificar que el entorno operativo donde se ejecuta el script no esté comprometido.",
        "no puede certificar que un usuario no haya copiado mal la passphrase o la mnemonic.",
        "\nLa ejecución offline, un entorno confiable y una fuente de "
        "entropía adecuada son condiciones necesarias, no una garantía "
        "de seguridad.",
        "el script intenta limpiar el historial del proceso Python actual.",
        "\n- Use el script con prudencia.",
    ])

    return "\n".join(lines)


def print_report(data, show_all=False):
    print(format_report(data, terminal_mode=True, hide_sensitive=not show_all, show_all=show_all))


def export_seed_report(data, output_path, output_format, password):
    if output_format == "json":
        content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    else:
        content = format_report(data, terminal_mode=False, hide_sensitive=False) + "\n"

    final_path = generate_sequential_path(output_path)
    write_secure_file(final_path, content, encrypt=True, password=password)
    return final_path


def load_vectors(vectors_path):
    with open(vectors_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_bip39_test_vectors(vectors_path):
    vectors = load_vectors(vectors_path)
    if isinstance(vectors, dict):
        if "english" in vectors:
            vectors = vectors["english"]
        else:
            first_key = next(iter(vectors.keys()), None)
            if first_key and isinstance(vectors[first_key], list):
                vectors = vectors[first_key]
            else:
                raise ValueError("El archivo vectors.json no tiene el formato esperado.")

    for i, vector in enumerate(vectors, start=1):
        if isinstance(vector, list) and len(vector) == 3:
            entropy_hex, expected_mnemonic, expected_seed = vector
            entropy = bytes.fromhex(entropy_hex)
            mnemonic = entropy_to_mnemonic(entropy)
            if mnemonic != expected_mnemonic:
                raise AssertionError(f"Vector {i}: mnemonic no coincide.")
            seed = mnemonic_seed(mnemonic, "TREZOR").hex()
            if seed != expected_seed:
                raise AssertionError(f"Vector {i}: seed no coincide.")
            roundtrip = mnemonic_to_entropy(mnemonic)
            if roundtrip["entropy"].hex() != entropy_hex:
                raise AssertionError(f"Vector {i}: entropía no coincide en round-trip.")
        elif isinstance(vector, list) and len(vector) == 4:
            entropy_hex, expected_mnemonic, expected_seed, _ = vector
            entropy = bytes.fromhex(entropy_hex)
            mnemonic = entropy_to_mnemonic(entropy)
            if mnemonic != expected_mnemonic:
                raise AssertionError(f"Vector {i}: mnemonic no coincide.")
            seed = mnemonic_seed(mnemonic, "TREZOR").hex()
            if seed != expected_seed:
                raise AssertionError(f"Vector {i}: seed no coincide.")
            roundtrip = mnemonic_to_entropy(mnemonic)
            if roundtrip["entropy"].hex() != entropy_hex:
                raise AssertionError(f"Vector {i}: entropía no coincide en round-trip.")
        else:
            raise ValueError(f"Vector {i}: formato no soportado.")

    print(f"Test vectors BIP39: OK ({len(vectors)} casos)")


class SensitiveCLIAction(argparse.Action):
    """Registra opciones sensibles suministradas explícitamente."""

    def __call__(
        self,
        parser,
        namespace,
        values,
        option_string=None,
    ):
        supplied = set(
            getattr(namespace, "_sensitive_cli_options", ())
        )
        supplied.add(self.dest)

        setattr(
            namespace,
            "_sensitive_cli_options",
            supplied,
        )
        setattr(namespace, self.dest, values)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Offline BIP39 Seed Report: generación, validación y reporte "
            "de material BIP39/BIP32 sin conexión."
        ),
        allow_abbrev=False,
    )
    parser.add_argument("-w", "--words", type=int, choices=[12, 15, 18, 21, 24], default=None,
                        help="Genera una mnemonic nueva con el número de palabras indicado.")
    parser.add_argument(
        "--entropy-bin",
        default="",
        action=SensitiveCLIAction,
        help=(
            "Entropy binaria de prueba. Requiere "
            "--allow-insecure-cli-secrets."
        ),
    )
    parser.add_argument(
        "--entropy-hex",
        default="",
        action=SensitiveCLIAction,
        help=(
            "Entropy hexadecimal de prueba. Requiere "
            "--allow-insecure-cli-secrets."
        ),
    )
    parser.add_argument(
        "--mnemonic",
        default="",
        action=SensitiveCLIAction,
        help=(
            "Mnemonic de prueba por argumentos. Requiere "
            "--allow-insecure-cli-secrets."
        ),
    )
    parser.add_argument(
        "--mnemonic-incomplete",
        default="",
        action=SensitiveCLIAction,
        help=(
            "Mnemonic incompleta de prueba por argumentos. Requiere "
            "--allow-insecure-cli-secrets."
        ),
    )
    parser.add_argument(
        "-p",
        "--passphrase",
        default="",
        action=SensitiveCLIAction,
        help=(
            "Passphrase de prueba por argumentos. Requiere "
            "--allow-insecure-cli-secrets."
        ),
    )
    parser.add_argument(
        "--allow-insecure-cli-secrets",
        action="store_true",
        help=(
            "Permite opciones sensibles por argumentos exclusivamente "
            "para pruebas controladas con datos ficticios. "
            "No evita exposición en historial, procesos o registros."
        ),
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help=(
            "Modo interactivo: solicita secretos sin eco en una TTY. "
            "No protege un sistema comprometido ni secretos ya pasados por CLI."
        ),
    )
    parser.add_argument("--audit-passphrase", action="store_true",
                        help="Muestra una auditoría descriptiva de la passphrase.")
    parser.add_argument("--run-tests", action="store_true",
                        help="Ejecuta los test vectors BIP39 oficiales y termina.")
    parser.add_argument("--vectors-file", default=DEFAULT_VECTORS_FILE,
                        help="Archivo JSON de test vectors BIP39.")
    parser.add_argument("-n", "--network", choices=["mainnet", "testnet"], default=None,
                        help="Red Bitcoin: mainnet o testnet. Sin -n, se usa mainnet.")
    parser.add_argument("-f", "--format", choices=["txt", "json"], default="json")
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT_PATH,
        help=(
            "Ruta del reporte cifrado "
            "(predeterminado: output/bip39_seed_report.json)."
        ),
    )
    parser.add_argument("--show-all", action="store_true",
                        help="Muestra TODOS los datos en pantalla (modo educativo)")
    args = parser.parse_args()

    supplied_secret_options = set(
        getattr(args, "_sensitive_cli_options", ())
    )

    option_labels = {
        "entropy_bin": "--entropy-bin",
        "entropy_hex": "--entropy-hex",
        "mnemonic": "--mnemonic",
        "mnemonic_incomplete": "--mnemonic-incomplete",
        "passphrase": "--passphrase",
    }

    supplied_labels = ", ".join(
        option_labels[name]
        for name in sorted(supplied_secret_options)
    )

    if args.run_tests and supplied_secret_options:
        parser.error(
            "--run-tests no admite opciones sensibles por argumentos. "
            "Ejecuta los vectores por separado."
        )

    if (
        supplied_secret_options
        and not args.allow_insecure_cli_secrets
    ):
        parser.error(
            "Opciones sensibles por CLI bloqueadas: "
            + supplied_labels
            + ". Introduce los valores mediante el modo interactivo. "
            "Para pruebas con datos ficticios, utiliza "
            "--allow-insecure-cli-secrets."
    )

    if args.run_tests:
        run_bip39_test_vectors(args.vectors_file)
        return

    if supplied_secret_options:
        print(
            "ADVERTENCIA: se autorizó el uso de opciones sensibles "
            "por argumentos para pruebas: "
            + supplied_labels
            + ". Los valores pueden quedar en historial, procesos "
            "o registros. Usar -i no elimina esa exposición."
        )


    if not CRYPTO_AVAILABLE:
        print("\n❌ ERROR: La librería 'cryptography' es requerida pero no está instalada.")
        print("    Instala con: pip3 install cryptography")
        print("    El script NO puede continuar sin encriptación.\n")
        sys.exit(1)

    print("\n" + "="*60)
    print("VERIFICACIÓN DE INTEGRIDAD BIP39")
    print("="*60)
    ok_official = verify_against_bip39_official()
    
    if not ok_official:
        print(
            "\nOperación cancelada: falló la verificación "
            "local de la wordlist BIP39."
        )
        sys.exit(1)

    print("\n🔐 SEGURIDAD ACTIVADA")
    print("   - El archivo de salida será encriptado con AES-256-GCM")
    if not args.show_all:
        print("   - Los datos sensibles se ocultarán en pantalla")
    print("   - Debes recordar esta contraseña para abrir el archivo\n")

    try:
        encrypt_password = get_secure_input(
            "Contraseña para encriptar: "
        )
        confirm_password = get_secure_input(
            "Confirmar contraseña: "
        )

        if encrypt_password != confirm_password:
            print("\nLas contraseñas no coinciden. Operación cancelada.")
            sys.exit(1)

        if len(encrypt_password) < 8:
            print("\nADVERTENCIA: la contraseña tiene menos de 8 caracteres.")
            print(
                "La longitud por sí sola no certifica su fuerza. "
                "Utiliza una contraseña de cifrado imprevisible."
            )

            decision = timed_menu_choice(
                "¿Continuar de todos modos? [y/N]: ",
                choices={"y", "n", ""},
            )

            if decision != "y":
                print("\nOperación cancelada.")
                sys.exit(1)

    except InputTimeoutError as exc:
        print(f"\n{exc}")
        print("Operación cancelada antes de generar el reporte.")
        sys.exit(1)
    except (EOFError, KeyboardInterrupt):
        print("\nOperación cancelada durante la entrada de contraseña.")
        sys.exit(1)
    except RuntimeError as exc:
        print(f"\nError de entrada: {exc}")
        print("Operación cancelada antes de generar el reporte.")
        sys.exit(1)

    print()

    if args.interactive:
        print("\nMODO INTERACTIVO")
        print("Los secretos solicitados con getpass se introducen sin eco.")
        print("Esto no protege contra un sistema comprometido.\n")

    try:
        data = build_context(args, interactive=args.interactive)
    except InputTimeoutError as exc:
        print(f"\n{exc}")
        print("Operación cancelada; no se exportó ningún resultado.")
        sys.exit(1)
    except InputCancelledError as exc:
        print(f"\nOperación cancelada: {exc}")
        sys.exit(1)
    except (EOFError, KeyboardInterrupt):
        print("\nOperación cancelada por el usuario.")
        sys.exit(1)
    except (ValueError, RuntimeError) as exc:
        print(f"\nError: {exc}")
        print("No se exportó ningún resultado.")
        sys.exit(1)

    print_report(data, show_all=args.show_all)

    attempt_clear_history()

    try:
        final_path = export_seed_report(
            data,
            args.output,
            args.format,
            password=encrypt_password,
        )
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"\nNo se pudo completar la exportación: {exc}")
        print("No se confirmó la creación del reporte cifrado.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExportación interrumpida.")
        print("No se confirmó la creación del reporte cifrado.")
        sys.exit(1)


    print()
    print(f"✅ Reporte cifrado guardado: {final_path}")
    print("   ⚠️  Recuerda la contraseña para desencriptar.")
    print("   ⚠️  Si pierdes la contraseña, perderás acceso a los datos.")
    print("\n📋 Para desencriptar el archivo:")
    print("   Usa un script separado con la función decrypt_report_content()")
    print(
        "O usa python3 -c con getpass y decrypt_report_content "
        "para no exponer la contraseña en el historial."
    )

if __name__ == "__main__":
    main()
