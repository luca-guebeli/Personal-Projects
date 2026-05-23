import csv
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path


FREESECT = 0xFFFFFFFF
ENDOFCHAIN = 0xFFFFFFFE


def parse_cfb(src: Path, outdir: Path) -> dict:
    data = src.read_bytes()
    if data[:8] != bytes.fromhex("D0 CF 11 E0 A1 B1 1A E1"):
        raise ValueError("Input is not an OLE compound file")

    def u16(off: int) -> int:
        return struct.unpack_from("<H", data, off)[0]

    def u32(off: int) -> int:
        return struct.unpack_from("<I", data, off)[0]

    sector_size = 1 << u16(30)
    mini_sector_size = 1 << u16(32)
    num_fat = u32(44)
    first_dir = u32(48)
    mini_cutoff = u32(56)
    first_minifat = u32(60)
    first_difat = u32(68)
    num_difat = u32(72)

    def sector(sid: int) -> bytes:
        start = 512 + sid * sector_size
        return data[start : start + sector_size]

    fat_sector_ids = []
    for i in range(109):
        sid = u32(76 + i * 4)
        if sid not in (FREESECT, ENDOFCHAIN):
            fat_sector_ids.append(sid)

    next_difat = first_difat
    seen = set()
    for _ in range(num_difat):
        if next_difat in (FREESECT, ENDOFCHAIN) or next_difat in seen:
            break
        seen.add(next_difat)
        sec = sector(next_difat)
        entries = sector_size // 4 - 1
        for i in range(entries):
            sid = struct.unpack_from("<I", sec, i * 4)[0]
            if sid not in (FREESECT, ENDOFCHAIN):
                fat_sector_ids.append(sid)
        next_difat = struct.unpack_from("<I", sec, entries * 4)[0]

    fat = []
    for sid in fat_sector_ids:
        sec = sector(sid)
        fat.extend(struct.unpack_from("<" + "I" * (sector_size // 4), sec, 0))

    def chain(start: int, maxlen: int = 100000) -> list[int]:
        res = []
        sid = start
        while sid not in (FREESECT, ENDOFCHAIN) and sid < len(fat) and len(res) < maxlen:
            res.append(sid)
            sid = fat[sid]
        return res

    def read_regular_stream(start: int, size: int) -> bytes:
        if start in (FREESECT, ENDOFCHAIN):
            return b""
        blob = b"".join(sector(sid) for sid in chain(start))
        return blob[:size]

    dir_chain = chain(first_dir)
    dir_bytes = read_regular_stream(first_dir, len(dir_chain) * sector_size)
    entries = []
    for idx in range(0, len(dir_bytes) // 128):
        ent = dir_bytes[idx * 128 : (idx + 1) * 128]
        name_len = struct.unpack_from("<H", ent, 64)[0]
        rawname = ent[: max(0, name_len - 2)]
        try:
            name = rawname.decode("utf-16le")
        except UnicodeDecodeError:
            name = ""
        typ = ent[66]
        start = struct.unpack_from("<I", ent, 116)[0]
        size = struct.unpack_from("<Q", ent, 120)[0]
        if name or typ:
            entries.append({"idx": idx, "name": name, "type": typ, "start": start, "size": size})

    root = next((e for e in entries if e["type"] == 5), None)
    mini_stream = read_regular_stream(root["start"], root["size"]) if root else b""

    minifat = []
    if first_minifat not in (FREESECT, ENDOFCHAIN):
        for sid in chain(first_minifat):
            sec = sector(sid)
            minifat.extend(struct.unpack_from("<" + "I" * (sector_size // 4), sec, 0))

    def read_mini_stream(start: int, size: int) -> bytes:
        if start in (FREESECT, ENDOFCHAIN):
            return b""
        parts = []
        sid = start
        while sid not in (FREESECT, ENDOFCHAIN) and sid < len(minifat):
            off = sid * mini_sector_size
            parts.append(mini_stream[off : off + mini_sector_size])
            sid = minifat[sid]
        return b"".join(parts)[:size]

    streams_dir = outdir / "streams"
    streams_dir.mkdir(parents=True, exist_ok=True)

    stream_infos = []
    for entry in entries:
        if entry["type"] != 2:
            continue
        if entry["size"] < mini_cutoff and minifat:
            content = read_mini_stream(entry["start"], entry["size"])
        else:
            content = read_regular_stream(entry["start"], entry["size"])
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", entry["name"]) or f"stream_{entry['idx']}"
        path = streams_dir / f"{entry['idx']:03d}_{safe}.bin"
        path.write_bytes(content)
        sample = content[:180].decode("latin1", errors="replace").replace("\x00", ".")
        stream_infos.append({**entry, "file": str(path.resolve()), "sample": sample})

    return {
        "sector_size": sector_size,
        "mini_sector_size": mini_sector_size,
        "num_fat": num_fat,
        "first_dir": first_dir,
        "mini_cutoff": mini_cutoff,
        "streams": stream_infos,
    }


def parse_records(outdir: Path) -> list[dict]:
    file_header = next((outdir / "streams").glob("*_FileHeader.bin"))
    blob = file_header.read_bytes()
    lines = []
    offset = 0
    while offset + 4 <= len(blob):
        length = struct.unpack_from("<I", blob, offset)[0]
        offset += 4
        if length == 0:
            continue
        if length > len(blob) - offset:
            break
        payload = blob[offset : offset + length]
        offset += length
        line = payload.decode("latin1", errors="replace").replace("\x00", "").strip()
        if "|" in line:
            line = line[line.find("|") :]
            lines.append(line)

    records = []
    for line in lines:
        rec = {"_raw": line}
        for part in line.split("|"):
            if not part or "=" not in part:
                continue
            key, value = part.split("=", 1)
            rec[key] = value
        records.append(rec)

    (outdir / "records.txt").write_text("\n".join(lines), encoding="utf-8")
    (outdir / "records.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    return records


def write_summaries(src: Path, outdir: Path, cfb: dict, records: list[dict]) -> dict:
    components = []
    for rec in records:
        if rec.get("RECORD") == "1":
            components.append(
                {
                    "object_id": rec.get("IndexInSheet", ""),
                    "lib": rec.get("LibReference", ""),
                    "desc": rec.get("Description", ""),
                    "x": rec.get("Location.X", ""),
                    "y": rec.get("Location.Y", ""),
                    "designator": rec.get("Designator", "") or rec.get("PartDesignator", ""),
                    "comment": rec.get("Comment", ""),
                    "manufacturer": rec.get("Manufacturer", ""),
                    "mpn": rec.get("Manufacturer Part Number", "") or rec.get("ManufacturerPartNumber", ""),
                    "pin_count": rec.get("PinCount", ""),
                }
            )

    with (outdir / "components.csv").open("w", newline="", encoding="utf-8") as cf:
        writer = csv.DictWriter(
            cf,
            fieldnames=[
                "object_id",
                "lib",
                "desc",
                "x",
                "y",
                "designator",
                "comment",
                "manufacturer",
                "mpn",
                "pin_count",
            ],
        )
        writer.writeheader()
        writer.writerows(components)

    label_records = [r for r in records if r.get("RECORD") == "25"]
    label_counter = Counter(r.get("Text", "") for r in label_records)
    key_patterns = [
        "SYS_3.3V",
        "SYS_3V3",
        "LCD_",
        "DISP_TOUCH_RST",
        "TOUCH_INT",
        "I2C_",
        "SCANNER",
        "MCU_SCAN",
        "HMI",
        "LED_",
        "BUZZER",
        "USB_D",
        "BOOT",
        "MCU_EN",
    ]
    key = []
    for name, count in sorted(label_counter.items()):
        if any(pattern in name for pattern in key_patterns):
            coords = [
                (r.get("Location.X"), r.get("Location.Y"))
                for r in label_records
                if r.get("Text") == name
            ]
            key.append({"net": name, "count": count, "coords": coords})
    (outdir / "net_label_summary.json").write_text(json.dumps(key, indent=2), encoding="utf-8")

    stream_summary = {
        "header": {
            "sector_size": cfb["sector_size"],
            "mini_sector_size": cfb["mini_sector_size"],
            "num_fat": cfb["num_fat"],
            "first_dir": cfb["first_dir"],
            "mini_cutoff": cfb["mini_cutoff"],
            "num_streams": len(cfb["streams"]),
        },
        "streams": cfb["streams"],
    }
    (outdir / "streams.json").write_text(json.dumps(stream_summary, indent=2), encoding="utf-8")

    summary = {
        "source": str(src.resolve()),
        "source_size": src.stat().st_size,
        "records": len(records),
        "net_labels": len(label_records),
        "components": len(components),
        "outdir": str(outdir.resolve()),
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: extract_altium_schdoc.py <input.SchDoc> <outdir>")
    src = Path(sys.argv[1])
    outdir = Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)
    cfb = parse_cfb(src, outdir)
    records = parse_records(outdir)
    print(json.dumps(write_summaries(src, outdir, cfb, records), indent=2))


if __name__ == "__main__":
    main()
