import httpx
import logging
from typing import Dict, Any, Optional

class PrusaPrinter:
    def __init__(self, ip: str, api_key: str):
        self.ip = ip
        self.api_key = api_key
        self.base_url = f"http://{ip}"
        self.headers = {"X-Api-Key": api_key}
    
    async def get_info(self) -> Dict[str, Any]:
        """
        Retrieves basic printer information from PrusaLink.
        """
        async with httpx.AsyncClient() as client:
            try:
                # Get version/info
                response = await client.get(f"{self.base_url}/api/version", headers=self.headers, timeout=5.0)
                response.raise_for_status()
                version_data = response.json()
                
                # Get status for printer name/type if not in version
                status_response = await client.get(f"{self.base_url}/api/v1/status", headers=self.headers, timeout=5.0)
                status_response.raise_for_status()
                status_data = status_response.json()
                
                printer_data = status_data.get("printer", {})
                
                return {
                    "name": version_data.get("hostname", "Unknown Prusa"), # Use hostname as name
                    "model": version_data.get("text", "Unknown Model"), # "PrusaLink" or similar
                    "serial": version_data.get("serial", "Unknown"), # Might fail if not provided
                    "firmware": version_data.get("server", "Unknown"), # PrusaLink version as firmware proxy
                    "state": printer_data.get("state", "Unknown")
                }
            except httpx.HTTPError as e:
                logging.error(f"HTTP Error getting printer info: {e}")
                raise
            except Exception as e:
                logging.error(f"Failed to get printer info: {e}")
                raise

    async def get_status(self) -> Dict[str, Any]:
        """
        Retrieves current printer status (temps, job, etc).
        """
        async with httpx.AsyncClient() as client:
            try:
                # Get Status (Telemetery)
                status_resp = await client.get(f"{self.base_url}/api/v1/status", headers=self.headers, timeout=5.0)
                status_resp.raise_for_status()
                status_data = status_resp.json()
                
                # Get Job Info
                job_resp = await client.get(f"{self.base_url}/api/v1/job", headers=self.headers, timeout=5.0)
                if job_resp.status_code == 204:
                     job_data = {} # No job running
                else:
                    job_resp.raise_for_status()
                    job_data = job_resp.json()
                
                # PrusaLink often returns flat keys like "temp_nozzle" inside "printer" object
                printer_data = status_data.get("printer", {})
                
                return {
                    "state": printer_data.get("state", "Unknown"),
                    "temp_nozzle": printer_data.get("temp_nozzle", 0),
                    "target_nozzle": printer_data.get("target_nozzle", 0),
                    "temp_bed": printer_data.get("temp_bed", 0),
                    "target_bed": printer_data.get("target_bed", 0),
                    "fan_speed": printer_data.get("fan_hotend", 0), 
                    "progress": job_data.get("progress", 0),
                    "time_remaining": job_data.get("time_remaining", 0),
                    "print_time": job_data.get("time_printing", 0)
                }
            except httpx.HTTPError as e:
                logging.error(f"HTTP Error getting printer status: {e}")
                raise
            except Exception as e:
                logging.error(f"Failed to get printer status: {e}")
                raise
