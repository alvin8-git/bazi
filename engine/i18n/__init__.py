"""Language helpers for the engine's plain-language layers (Phase 2, Simplified Chinese).

T(id, en, lang, **slots) returns the English text it is given unless lang is "zh", in which case it returns the
approved Chinese string for `id`, formatted with the same slots. English output is therefore exactly what the
code built before. A zh id that is looked up but absent is recorded in MISSING and the English is returned.
"""
from __future__ import annotations

import re

from .zh import ZH
from .zh_extra import ZH_EXTRA   # rows added after the generated table; fold them into it at the next regeneration

MISSING: set[str] = set()
TRACE: list[str] | None = None   # tests set this to a list to record every id the code asks for
_CJK = "㐀-鿿　-〿＀-￯"
_SP = re.compile(rf"(?<=[{_CJK}]) +| +(?=[{_CJK}])")


def tidy(s: str) -> str:
    """Chinese typography: no space beside a Chinese character or full-width mark."""
    return _SP.sub("", s)


def _zh(id: str, en: str, **slots) -> str:
    z = ZH.get(id)
    if z is None:
        z = ZH_EXTRA.get(id)
    if z is None:
        MISSING.add(id)
        return en
    return finish(z.format(**slots) if "{" in z else z)


_RANGE = re.compile(r"(?<=\d)–(?=\d)")
_EMPTY = re.compile(r"[（(]\s*[）)]")


def finish(s: str) -> str:
    """The Chinese typography every spliced sentence gets: no space beside Chinese, 3–5 as 3～5, no empty brackets, Simplified."""
    return simp(tidy(_EMPTY.sub("", _RANGE.sub("～", s))))


_T2S: dict | None = None


def simp(s: str) -> str:
    """Traditional to Simplified for the engine's own data terms (生氣, 劫煞, 驛馬) spliced into a Chinese sentence."""
    global _T2S
    if _T2S is None:
        from ..htmlreport import _T2S as table      # the same table the report and web/app.js use
        _T2S = table
    return "".join(_T2S.get(c, c) for c in s)


def T(id: str, en: str, lang: str = "en", **slots) -> str:
    if TRACE is not None:
        TRACE.append(id)
    return en if lang != "zh" else _zh(id, en, **slots)


_LAT = re.compile(r"[A-Za-z]{2,}")
_TBL: dict[str, object] = {}


def _walk(path: str, val):
    """Copy of a module table with every English leaf looked up by its id (ids follow the inventory's flatten rule)."""
    if isinstance(val, dict):
        return {k: _walk(f"{path}.{re.sub(r'\s+', '_', str(k))}", v) for k, v in val.items()}
    if isinstance(val, (list, tuple)):
        out = []
        for i, v in enumerate(val):
            if isinstance(v, (list, tuple)) and v and isinstance(v[0], str) and not _LAT.search(v[0]):
                out.append(_walk(f"{path}.{v[0]}", v))
            else:
                out.append(_walk(f"{path}.{i}", v))
        return tuple(out) if isinstance(val, tuple) else out
    if isinstance(val, str) and _LAT.search(val):
        z = ZH.get(path)                 # table leaves are returned as they are: some are templates for .format() at the use site
        if z is None:
            MISSING.add(path)
            return val
        return tidy(z)
    return val


def L(prefix: str, table, lang: str = "en"):
    """The module table `prefix` (e.g. "bazi_report.ELEMENT_READING") in `lang`; English returns the table itself."""
    if lang != "zh":
        return table
    t = _TBL.get(prefix)
    if t is None:
        t = _TBL[prefix] = _walk(prefix, table)
    return t


def jn(xs, lang: str = "en", en: str = ", ", zh: str = "、") -> str:
    """English `en`.join, or the Chinese separator for a list the reader sees as items."""
    return (zh if lang == "zh" else en).join(str(x) for x in xs)


def zh_join(xs) -> str:
    """A、B和C (no Oxford comma)."""
    xs = [str(x) for x in xs]
    return "" if not xs else xs[0] if len(xs) == 1 else "、".join(xs[:-1]) + "和" + xs[-1]


def num_word(n, lang: str = "en", en_words: dict | None = None):
    """Number word for 0 to 10, digits beyond (English table is the caller's; Chinese comes from story.NUM.*)."""
    if lang == "zh":
        return T(f"story.NUM.{n}", str(n), lang) if isinstance(n, int) and 0 <= n <= 10 else str(n)
    return (en_words or {}).get(n, n)


def an(word: str) -> str:
    return ("an " if word[:1].lower() in "aeiou" else "a ") + word


def ELEM(lang: str = "en"):
    """wuxing.ELEMENT_EN in `lang` (Wood/Fire/... in English, 木/火/... in Chinese)."""
    from ..wuxing import ELEMENT_EN
    return L("wuxing.ELEMENT_EN", ELEMENT_EN, lang)


def and_l(xs, lang: str = "en", en: str = " and ") -> str:
    """"A and B" in English (the caller's joiner), "A和B" / "A、B和C" in Chinese."""
    xs = [str(x) for x in xs]
    return zh_join(xs) if lang == "zh" else en.join(xs)


def cap(s: str, lang: str = "en") -> str:
    """Capitalise the first letter in English; Chinese has no capitals."""
    return s if lang == "zh" else s[:1].upper() + s[1:]


def dot(lang: str = "en") -> str:
    """Sentence-final stop: "." in English, "。" in Chinese."""
    return "。" if lang == "zh" else "."


def zs(s: str, lang: str = "en") -> str:
    """Simplify a display string the code assembled from the engine's traditional-script data terms (zh only)."""
    return simp(s) if lang == "zh" else s
