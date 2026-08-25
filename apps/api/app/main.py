"""
Market AI — FastAPI Application Entry Point
Production-ready backend with REST APIs, WebSockets, background tick simulation, and DB init.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from apps.api.app.core.config import settings
from apps.api.app.core.event_bus import manager
from apps.api.app.db.session import init_db
from apps.api.app.api.endpoints.market import router as market_router
from apps.api.app.api.endpoints.derivatives import router as derivatives_router
from apps.api.app.api.endpoints.strategies import router as strategies_router
from apps.api.app.api.endpoints.paper_trading import router as paper_router
from apps.api.app.api.endpoints.tournaments import router as tournament_router
from packages.market_data.development_provider import DevelopmentMarketDataProvider
from packages.market_calendar.calendar import IST_TIMEZONE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("market_ai.api")

provider = DevelopmentMarketDataProvider()


async def background_market_ticker():
    """Background task to broadcast real-time ticks to connected browser terminals."""
    symbols = ["NIFTY 50", "BANK NIFTY", "SENSEX", "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "INDIA VIX"]
    while True:
        try:
            if manager.active_connections:
                # Pick 2-3 symbols to tick per second
                for sym in symbols[:4]:
                    quote = await provider.get_quote(sym)
                    msg = {
                        "event_type": "TICK",
                        "symbol": quote.symbol,
                        "price": quote.last_price,
                        "change": quote.change,
                        "percent_change": quote.percent_change,
                        "volume": quote.volume,
                        "timestamp": datetime.now(IST_TIMEZONE).isoformat(),
                    }
                    await manager.broadcast(msg)
            await asyncio.sleep(1.5)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in ticker broadcast: {e}")
            await asyncio.sleep(2.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables
    logger.info("Initializing Market AI database...")
    await init_db()
    logger.info("Database initialized successfully.")
    
    # Start background ticker task
    ticker_task = asyncio.create_task(background_market_ticker())
    logger.info("Background live ticker task started.")
    
    yield
    
    # Shutdown
    ticker_task.cancel()
    try:
        await ticker_task
    except asyncio.CancelledError:
        pass
    logger.info("Market AI API shutdown complete.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(market_router, prefix=settings.API_V1_STR)
app.include_router(derivatives_router, prefix=settings.API_V1_STR)
app.include_router(strategies_router, prefix=settings.API_V1_STR)
app.include_router(paper_router, prefix=settings.API_V1_STR)
app.include_router(tournament_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "platform": "Market AI — Indian Market Intelligence Platform",
        "status": "ONLINE",
        "timestamp": datetime.now(IST_TIMEZONE).isoformat(),
        "docs_url": "/docs",
    }


@app.websocket("/api/v1/ws/ticker")
async def websocket_ticker_endpoint(websocket: WebSocket):
    """Real-time streaming WebSocket endpoint for browser terminals."""
    await manager.connect(websocket)
    try:
        # Send initial welcome message
        await websocket.send_json({
            "event_type": "CONNECTED",
            "message": "Connected to Market AI Live Indian Market Feed",
            "timestamp": datetime.now(IST_TIMEZONE).isoformat(),
        })
        while True:
            # Keep connection alive; accept any client commands/subscriptions
            data = await websocket.receive_text()
            # Echo heartbeat if received
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket client error: {e}")
        manager.disconnect(websocket)
