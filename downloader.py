import os
import sys
import requests
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─────────────────────────────────────────────
#  API ANAHTARLARI – buraya kendi key'lerini gir
# ─────────────────────────────────────────────
PEXELS_API_KEY  = "Api_Key_Buraya"   # https://www.pexels.com/api/
PIXABAY_API_KEY = "Api_Key_Buraya"  # https://pixabay.com/api/docs/


def pexels_search(query: str, max_results: int = 100) -> list[dict]:
    """Pexels API'den video listesi çeker."""
    if PEXELS_API_KEY == "PEXELS_API_KEY_BURAYA":
        print("[UYARI] Pexels API key girilmemiş, atlanıyor.")
        return []

    videos = []
    per_page = min(max_results, 80)  # Pexels max 80/istek
    page = 1
    headers = {"Authorization": PEXELS_API_KEY}

    while len(videos) < max_results:
        url = "https://api.pexels.com/videos/search"
        params = {"query": query, "per_page": per_page, "page": page}
        try:
            r = requests.get(url, headers=headers, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
            items = data.get("videos", [])
            if not items:
                break
            for v in items:
                # En yüksek kaliteli video dosyasını seç
                files = sorted(
                    v.get("video_files", []),
                    key=lambda f: f.get("width", 0),
                    reverse=True,
                )
                if files:
                    videos.append({
                        "source": "pexels",
                        "id": v["id"],
                        "url": files[0]["link"],
                        "ext": "mp4",
                    })
            page += 1
            if len(items) < per_page:
                break
        except Exception as e:
            print(f"[Pexels] Hata: {e}")
            break

    return videos[:max_results]


def pixabay_search(query: str, max_results: int = 100) -> list[dict]:
    """Pixabay API'den video listesi çeker."""
    if PIXABAY_API_KEY == "PIXABAY_API_KEY_BURAYA":
        print("[UYARI] Pixabay API key girilmemiş, atlanıyor.")
        return []

    videos = []
    per_page = min(max_results, 200)  # Pixabay max 200/istek
    page = 1

    while len(videos) < max_results:
        url = "https://pixabay.com/api/videos/"
        params = {
            "key": PIXABAY_API_KEY,
            "q": query,
            "per_page": per_page,
            "page": page,
            "video_type": "film",
        }
        try:
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
            items = data.get("hits", [])
            if not items:
                break
            for v in items:
                # large > medium > small > tiny
                vfiles = v.get("videos", {})
                chosen = None
                for quality in ("large", "medium", "small", "tiny"):
                    if vfiles.get(quality, {}).get("url"):
                        chosen = vfiles[quality]["url"]
                        break
                if chosen:
                    videos.append({
                        "source": "pixabay",
                        "id": v["id"],
                        "url": chosen,
                        "ext": "mp4",
                    })
            page += 1
            if len(items) < per_page:
                break
        except Exception as e:
            print(f"[Pixabay] Hata: {e}")
            break

    return videos[:max_results]


def download_video(video: dict, folder: Path) -> str:
    """Tek bir videoyu indirir, dosya adını döner."""
    fname = f"{video['source']}_{video['id']}.{video['ext']}"
    fpath = folder / fname

    if fpath.exists():
        return f"[VAR]  {fname}"

    try:
        with requests.get(video["url"], stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(fpath, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 256):
                    f.write(chunk)
        return f"[OK]   {fname}"
    except Exception as e:
        return f"[HATA] {fname} – {e}"


def main():
    parser = argparse.ArgumentParser(
        description="Pexels & Pixabay'den video indir"
    )
    parser.add_argument("query", help="Arama konusu (örn: 'nature', 'city')")
    parser.add_argument(
        "-n", "--count", type=int, default=100,
        help="Her platformdan kaç video indirilsin (varsayılan: 100)"
    )
    parser.add_argument(
        "-o", "--output", default="indirilenler",
        help="İndirme klasörü (varsayılan: indirilenler)"
    )
    parser.add_argument(
        "--source", choices=["pexels", "pixabay", "her ikisi"],
        default="her ikisi",
        help="Platform seçimi (varsayılan: her ikisi)"
    )
    parser.add_argument(
        "-t", "--threads", type=int, default=4,
        help="Paralel indirme sayısı (varsayılan: 4)"
    )
    args = parser.parse_args()

    out_folder = Path(args.output)
    out_folder.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 İndirme klasörü: {out_folder.resolve()}")
    print(f"🔍 Konu: '{args.query}'  |  Adet: {args.count}  |  Platform: {args.source}\n")

    all_videos: list[dict] = []

    if args.source in ("pexels", "her ikisi"):
        print("⏳ Pexels'ten video listesi alınıyor…")
        pexels = pexels_search(args.query, args.count)
        print(f"   → {len(pexels)} video bulundu.")
        all_videos.extend(pexels)

    if args.source in ("pixabay", "her ikisi"):
        print("⏳ Pixabay'den video listesi alınıyor…")
        pixabay = pixabay_search(args.query, args.count)
        print(f"   → {len(pixabay)} video bulundu.")
        all_videos.extend(pixabay)

    if not all_videos:
        print("\n❌ Hiç video bulunamadı. API key'lerini kontrol et.")
        sys.exit(1)

    print(f"\n⬇️  Toplam {len(all_videos)} video indiriliyor ({args.threads} paralel)…\n")

    with ThreadPoolExecutor(max_workers=args.threads) as pool:
        futures = {pool.submit(download_video, v, out_folder): v for v in all_videos}
        done = 0
        for future in as_completed(futures):
            done += 1
            msg = future.result()
            print(f"  [{done}/{len(all_videos)}] {msg}")

    print(f"\n✅ Tamamlandı! Videolar '{out_folder}' klasöründe.")


if __name__ == "__main__":
    main()
