from __future__ import annotations

import json
import os

import uvicorn


def main() -> None:
    config_path = os.getenv("CONFIG_PATH", "config/server_config.json")
    with open(config_path) as f:
        config = json.load(f)
    uvicorn.run(
        "poseidon.main:app",
        host=config.get("host", "0.0.0.0"),
        port=int(config.get("port", 8000)),
        reload=True,
    )


if __name__ == "__main__":
    main()
