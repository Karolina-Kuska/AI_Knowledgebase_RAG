from src.rag.vectorstore import get_chroma
import json, argparse, sys

def _first_level(x):
    if isinstance(x, list) and x and isinstance(x[0], list):
        return x[0]
    return x or []

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--peek", type=int, default=5)
    ap.add_argument("--export", type=str, default="")
    args = ap.parse_args()

    vs = get_chroma()
    coll = vs._collection

    print(f"Collections: {[coll.name]}")
    print(f"Count: {coll.count()}\n")

    sample = coll.peek(limit=args.peek)
    docs  = _first_level(sample.get("documents", []))
    metas = _first_level(sample.get("metadatas", []))
    ids   = _first_level(sample.get("ids", []))

    print("-- SAMPLE --")
    for i, (doc, meta) in enumerate(zip(docs, metas), 1):
        if isinstance(meta, str):
            meta_str = meta
            title = source = chunk_id = ""
        elif isinstance(meta, dict):
            meta_str = ""
            title = meta.get("title") or ""
            source = meta.get("source") or ""
            chunk_id = meta.get("chunk_id") or ""
        else:
            meta_str = repr(meta)
            title = source = chunk_id = ""

        print(f"[{i}] {chunk_id} | {title} | {source}")
        print((doc or "")[:200].replace("\n", " "), "\n")
        if meta_str:
            print(f"meta(raw): {meta_str}\n")

    if args.export:
        all_data = coll.get(include=["documents","metadatas","ids"])
        docs_all  = _first_level(all_data.get("documents", []))
        metas_all = _first_level(all_data.get("metadatas", []))
        ids_all   = _first_level(all_data.get("ids", []))
        with open(args.export, "w", encoding="utf-8") as f:
            for id_, doc, meta in zip(ids_all, docs_all, metas_all):
                f.write(json.dumps({"id": id_, "text": doc, "meta": meta}, ensure_ascii=False) + "\n")
        print(f"\nExport OK → {args.export}")

if __name__ == "__main__":
    sys.exit(main())
