import asyncio
import random
import logging
from typing import Dict, Any

class MockPrinter:
    def __init__(self, ip: str = "mock", api_key: str = "mock"):
        self.ip = ip
        self.api_key = api_key
        self.state = "Printing"
        self.progress = 45
        self.time_remaining = 1200
        self.temp_nozzle = 215.0
        self.target_nozzle = 215.0
        self.temp_bed = 60.0
        self.target_bed = 60.0
        self.temp_chamber = 35.0
        
        logging.info("Initialized MockPrinter")

    async def get_info(self) -> Dict[str, Any]:
        return {
            "name": "Mock Prusa MK4",
            "model": "MK4",
            "firmware": "5.1.0-mock",
            "state": self.state
        }

    async def get_status(self) -> Dict[str, Any]:
        # Simulate slight temperature fluctuations
        sim_nozzle = self.target_nozzle + random.uniform(-0.5, 0.5) if self.target_nozzle > 0 else 25.0
        sim_bed = self.target_bed + random.uniform(-0.2, 0.2) if self.target_bed > 0 else 22.0
        
        # Simulate progress if printing
        if self.state == "Printing":
            self.progress = min(100, self.progress + 0.1)
            self.time_remaining = max(0, self.time_remaining - 1)
            if self.progress >= 100:
                self.state = "Finished"
                
        return {
            "state": self.state,
            "temp_nozzle": round(sim_nozzle, 1),
            "target_nozzle": self.target_nozzle,
            "temp_bed": round(sim_bed, 1),
            "target_bed": self.target_bed,
            "temp_chamber": round(self.temp_chamber, 1),
            "target_chamber": 0,
            "fan_speed": 100 if self.state == "Printing" else 0,
            "progress": int(self.progress),
            "time_remaining": int(self.time_remaining),
            "print_time": 3600 - int(self.time_remaining)
        }

    async def pause_print(self) -> Dict[str, Any]:
        self.state = "Paused"
        return {"status": "success", "message": "Mock print paused"}

    async def resume_print(self) -> Dict[str, Any]:
        self.state = "Printing"
        return {"status": "success", "message": "Mock print resumed"}

    async def stop_print(self) -> Dict[str, Any]:
        self.state = "Ready"
        self.progress = 0
        self.time_remaining = 0
        return {"status": "success", "message": "Mock print stopped"}

    async def upload_file(self, file_path: str, target_filename: str = None, storage: str = "usb") -> Dict[str, Any]:
        return {"status": "success", "message": f"Simulated upload of {target_filename}"}
