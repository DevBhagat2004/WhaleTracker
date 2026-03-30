# api.py
# FastAPI backend — imports your files directly, exposes endpoints to frontend
# Run with: uvicorn api:app --reload --port 8000

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import asyncio
import json
import time
import requests

# ── YOUR FILES ──────────────────────────────────
import user        # user.userData(wallet)      → position count
import positions   # positions.userData(wallet) → full position list
import single      # single.getMarket(slug)     → market metadata
                   # single.getTop(market, ...) → raw trades
                   # single.getWhales(...)      → filtered trades
import compare     # compare.correlate(wallets) → correlation map
import addusers    # addusers.add(wallets)      → wallet set (used in compare)
# ────────────────────────────────────────────────

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GAMMA_API     = "https://gamma-api.polymarket.com"
DATA_API      = "https://data-api.polymarket.com"
POLL_INTERVAL = 30  # seconds between stream polls




# ══════════════════════════════════════════════════
# SCENE 1 — WHALE FEED
# Frontend sends: slug (required), min_amount, max_pos, trade_limit
# Uses: single.getMarket(), single.getWhales()
# ══════════════════════════════════════════════════

@app.get("/api/trades")
def api_trades(
    slug:        str = Query(...),       # required — one specific market
    min_amount:  int = Query(10000),
    max_pos:     int = Query(21),
    trade_limit: int = Query(100),
):
    market = single.getMarket(slug)

    if not market:
        return JSONResponse(content={"error": f"Market not found: {slug}"}, status_code=404)

    trades = single.getWhales(market, min_amount, trade_limit, max_pos)

    for t in trades:
        t["marketSlug"]  = market[0].get("slug", slug)
        t["marketTitle"] = market[0].get("question", slug)

    return JSONResponse(content=trades)


# ══════════════════════════════════════════════════
# SCENE 2 — WALLET PROFILER
# Frontend sends: wallet address
# Uses: positions.userData()
# ══════════════════════════════════════════════════

@app.get("/api/positions")
def api_positions(wallet: str = Query(...)):
    """
    positions.py → userData(wallet)
    Returns full open positions for a wallet.
    """
    data = positions.userData(wallet)
    return JSONResponse(content=data if data else [])


# ══════════════════════════════════════════════════
# SCENE 3 — CORRELATION MAP
# Frontend sends: comma-separated wallet addresses
# Uses: addusers.add(), compare.correlate()
# ══════════════════════════════════════════════════

@app.get("/api/compare")
def api_compare(wallets: str = Query(...)):
    """
    addusers.add(wallet_list) → parses wallets
    compare.correlate(wallets) → builds correlation map
    Returns sorted list of shared positions.
    """
    wallet_list = [w.strip() for w in wallets.split(",") if w.strip()]

    # addusers.py — frontend mode (pass list, skip CLI input)
    wallet_set = addusers.add(wallet_list)

    # compare.py — shared logic between CLI and frontend
    result = compare.correlate(wallet_set)

    return JSONResponse(content=result)


# ══════════════════════════════════════════════════
# LIVE STREAM — Server-Sent Events
# single.py while loop → pushed to browser in real time
# Frontend connects once, receives new trades as they appear
# ══════════════════════════════════════════════════

@app.get("/api/stream")
async def api_stream(
    slug:       str = Query(...),        # required — one specific market
    min_amount: int = Query(10000),
    max_pos:    int = Query(21),
):
    """
    single.py main() loop — but streamed to browser via SSE instead of printed.
    """
    async def generator():
        seen         = set()
        wallet_cache = {}

        while True:
            market = single.getMarket(slug)
            markets = [market] if market else []

            for market_wrap in markets:
                # single.py — getWhales() does the filtering
                trades = single.getWhales(market_wrap, min_amount, 100, max_pos)

                for t in trades:
                    tx = t.get("transactionHash", "")
                    if tx in seen:
                        continue
                    seen.add(tx)

                    w = t.get("proxyWallet", "")
                    if w not in wallet_cache:
                        wallet_cache[w] = user.userData(w)
                    t["positionCount"] = wallet_cache[w]
                    t["marketSlug"]    = market_wrap[0].get("slug", "")
                    t["marketTitle"]   = market_wrap[0].get("question", "")

                    yield f"data: {json.dumps(t)}\n\n"
                    await asyncio.sleep(0)

                await asyncio.sleep(0.2)

            if len(wallet_cache) > 500:
                wallet_cache.clear()

            await asyncio.sleep(POLL_INTERVAL)

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/health")
def health():
    return {"status": "ok", "time": int(time.time())}