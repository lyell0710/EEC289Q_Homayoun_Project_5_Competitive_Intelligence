#!/usr/bin/env python3
import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class Evidence:
    evidence_id: str
    doc_id: str
    quote: str


class CompetitiveIntelligenceAgent:
    def __init__(self) -> None:
        self._evidence_counter = 0
        self._evidence_map: List[Evidence] = []
        self._evidence_index: Dict[Tuple[str, str], str] = {}

    def _next_evidence(self, doc_id: str, quote: str) -> str:
        self._evidence_counter += 1
        evidence_id = f"e{self._evidence_counter}"
        self._evidence_map.append(Evidence(evidence_id=evidence_id, doc_id=doc_id, quote=quote.strip()))
        return evidence_id

    def _get_or_create_evidence(self, doc_id: str, quote: str) -> str:
        key = (doc_id, quote.strip())
        if key in self._evidence_index:
            return self._evidence_index[key]
        evidence_id = self._next_evidence(doc_id, quote)
        self._evidence_index[key] = evidence_id
        return evidence_id

    @staticmethod
    def _parse_date(value: str) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return None

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        pieces = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
        return [p.strip() for p in pieces if p.strip()]

    @staticmethod
    def _looks_marketing(sentence: str) -> bool:
        low_value_terms = [
            "best-in-class",
            "next-gen",
            "world-class",
            "revolutionary",
            "future of",
            "easiest platform",
        ]
        s = sentence.lower()
        return any(t in s for t in low_value_terms)

    @staticmethod
    def _extract_segment_labels(sentence: str) -> List[str]:
        labels = []
        s = sentence.lower()
        if "smb" in s:
            labels.append("SMB")
        if "mid-market" in s:
            labels.append("Mid-market")
        if "enterprise" in s:
            labels.append("Enterprise")
        if "hospital" in s or "clinic" in s:
            labels.append("Healthcare providers")
        if "200+" in s and "beds" in s:
            labels.append("Large hospitals (200+ beds)")
        return labels

    @staticmethod
    def _append_unique(items: List[Dict], key: str, value: str, evidence_id: str, extra: Dict = None) -> None:
        for item in items:
            if item.get(key) == value:
                if evidence_id not in item["evidence_ids"]:
                    item["evidence_ids"].append(evidence_id)
                return
        payload = {key: value, "evidence_ids": [evidence_id]}
        if extra:
            payload.update(extra)
        items.append(payload)

    def analyze(self, payload: Dict) -> Dict:
        target = payload.get("target", "").strip()
        documents = payload.get("documents", [])

        differentiators: List[Dict] = []
        pricing_signals: List[Dict] = []
        target_segments: List[Dict] = []
        weaknesses: List[Dict] = []

        doc_prices: Dict[str, Set[str]] = {}
        api_claims: List[Tuple[str, str, str]] = []
        doc_dates: Dict[str, Optional[datetime]] = {}

        for doc in documents:
            doc_id = doc.get("doc_id", "unknown_doc")
            content = doc.get("content", "")
            doc_dates[doc_id] = self._parse_date(doc.get("date", ""))
            doc_prices.setdefault(doc_id, set())
            for sentence in self._split_sentences(content):
                s_low = sentence.lower()
                if self._looks_marketing(sentence):
                    continue

                has_pricing = bool(re.search(r"\$\s?\d+|\bpricing\b|\bplan\b|\bper user\b|\bper seat\b|\bcontact sales\b", s_low))
                has_segment = bool(re.search(r"\bsmb\b|\bmid-market\b|\benterprise\b|\bhospital\b|\bclinic\b|\bregional\b|\b200\+\s?beds\b", s_low))
                has_diff = bool(re.search(r"\bintegrat|\bapi\b|\bsso\b|\baudit log\b|\bdeployment\b|\bonly\b|\bincludes\b", s_low))
                has_weakness = bool(re.search(r"\bonly\b|\blimited\b|\brequires\b|\btakes\s+\d|\bcontact sales\b|\bno\b", s_low))
                if not (has_pricing or has_segment or has_diff or has_weakness):
                    continue

                eid = self._get_or_create_evidence(doc_id, sentence)

                if has_pricing:
                    pricing_type = "unknown"
                    if "per seat" in s_low or "per user" in s_low or "/seat" in s_low or "/user" in s_low:
                        pricing_type = "seat_based"
                    elif "tier" in s_low or "starter" in s_low or "growth" in s_low:
                        pricing_type = "tiered"
                    elif "contact sales" in s_low or "contract" in s_low:
                        pricing_type = "contract"

                    self._append_unique(
                        pricing_signals,
                        key="claim",
                        value=sentence,
                        evidence_id=eid,
                        extra={"pricing_type": pricing_type},
                    )

                    for price in re.findall(r"\$\s?\d+", sentence):
                        doc_prices[doc_id].add(price.replace(" ", ""))

                if has_segment:
                    segment_labels = self._extract_segment_labels(sentence)
                    for segment in segment_labels:
                        self._append_unique(target_segments, key="segment", value=segment, evidence_id=eid)

                if has_diff:
                    self._append_unique(
                        differentiators,
                        key="claim",
                        value=sentence,
                        evidence_id=eid,
                        extra={"signal_strength": "medium"},
                    )
                    if "api" in s_low:
                        api_claims.append((sentence, doc_id, eid))

                if has_weakness:
                    self._append_unique(weaknesses, key="weakness", value=sentence, evidence_id=eid)

        conflicts: List[Dict] = []

        doc_min_prices: Dict[str, int] = {}
        for doc_id, prices in doc_prices.items():
            numeric_prices = [int(p.replace("$", "")) for p in prices]
            if numeric_prices:
                doc_min_prices[doc_id] = min(numeric_prices)

        if len(doc_min_prices) >= 2 and len(set(doc_min_prices.values())) > 1:
            claims = []
            for doc_id, min_price in doc_min_prices.items():
                matching = [e.evidence_id for e in self._evidence_map if e.doc_id == doc_id and f"${min_price}" in e.quote]
                if matching:
                    claims.append({"statement": f"{doc_id} lists minimum entry price ${min_price}", "evidence_ids": [matching[0]]})
            resolution_status = "unresolved"
            resolution_rationale = "Different documents imply different entry prices."
            dated_docs = [(doc_id, d) for doc_id, d in doc_dates.items() if d is not None and doc_id in doc_min_prices]
            if len(dated_docs) >= 2:
                newest_doc_id, newest_date = max(dated_docs, key=lambda x: x[1])
                oldest_doc_id, oldest_date = min(dated_docs, key=lambda x: x[1])
                if newest_doc_id != oldest_doc_id and newest_date > oldest_date:
                    resolution_status = "partially_resolved"
                    resolution_rationale = (
                        f"Newer source ({newest_doc_id}, {newest_date.date()}) may reflect updated pricing, "
                        "but historical claim is retained as conflict."
                    )
            conflicts.append(
                {
                    "topic": "pricing",
                    "claims": claims,
                    "resolution_status": resolution_status,
                    "resolution_rationale": resolution_rationale,
                }
            )

        if len(api_claims) >= 2:
            api_texts = {c[0].lower() for c in api_claims}
            if any("only" in t for t in api_texts) and any("includes" in t or "available" in t for t in api_texts):
                claims = [{"statement": c[0], "evidence_ids": [c[2]]} for c in api_claims]
                conflicts.append(
                    {
                        "topic": "api_access_scope",
                        "claims": claims,
                        "resolution_status": "unresolved",
                        "resolution_rationale": "API access is described with potentially conflicting scope.",
                    }
                )

        if not differentiators:
            differentiators = []
        if not pricing_signals:
            pricing_signals = []
        if not target_segments:
            target_segments = []
        if not weaknesses:
            weaknesses = []

        confidence = "low"
        signal_count = len(differentiators) + len(pricing_signals) + len(target_segments)
        if signal_count >= 8:
            confidence = "high"
        elif signal_count >= 3:
            confidence = "medium"

        positioning_summary = "Insufficient evidence"
        if signal_count > 0:
            positioning_summary = (
                f"{target} appears positioned based on extracted signals in pricing, features, and target-customer language."
            )

        return {
            "target": target,
            "positioning_summary": positioning_summary,
            "key_differentiators": differentiators,
            "pricing_signals": pricing_signals,
            "target_segments": target_segments,
            "identified_weaknesses": weaknesses,
            "conflicts": conflicts,
            "evidence_map": [
                {"evidence_id": e.evidence_id, "doc_id": e.doc_id, "quote": e.quote} for e in self._evidence_map
            ],
            "confidence": {
                "overall": confidence,
                "notes": "Rule-based baseline; improve with stronger semantic extraction in Week 3.",
            },
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Competitive Intelligence Agent on input JSON.")
    parser.add_argument("--input", required=True, help="Path to input JSON containing target + documents")
    parser.add_argument("--output", required=True, help="Path to output JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    agent = CompetitiveIntelligenceAgent()
    result = agent.analyze(payload)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote structured report to: {output_path}")


if __name__ == "__main__":
    main()
