#!/usr/bin/env python3
"""
Roblox Studio MCP Client
Connects to Roblox Studio MCP Server untuk mengontrol Studio
"""

import subprocess
import json
import sys
import os
from pathlib import Path

class RobloxMCPClient:
    def __init__(self):
        self.mcp_server_cmd = "cmd.exe"
        self.mcp_server_args = ["/d", "/s", "/c", "cd /d %LOCALAPPDATA%\\Roblox && .\\mcp.bat"]
        self.is_connected = False
    
    def connect(self):
        """Sambungkan ke Roblox Studio MCP Server"""
        try:
            print("[*] Mencoba sambung ke Roblox Studio MCP Server...")
            # Check apakah Roblox Studio running
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq RobloxStudioBeta.exe'],
                capture_output=True,
                text=True
            )
            
            if 'RobloxStudioBeta.exe' in result.stdout:
                print("[✓] Roblox Studio terdeteksi RUNNING")
                self.is_connected = True
                return True
            else:
                print("[✗] Roblox Studio TIDAK running")
                return False
                
        except Exception as e:
            print(f"[✗] Error koneksi: {e}")
            return False
    
    def check_mcp_server(self):
        """Check status MCP Server"""
        try:
            print("[*] Checking MCP Server status...")
            result = subprocess.run(
                ['netstat', '-ano', '|', 'findstr', ':50051'],
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode == 0:
                print("[✓] MCP Server aktif di port 50051")
                return True
            else:
                print("[✗] MCP Server tidak merespons")
                return False
                
        except Exception as e:
            print(f"[✗] Error check MCP: {e}")
            return False
    
    def send_command(self, command: str, args: dict = None):
        """Kirim command ke Roblox Studio"""
        if not self.is_connected:
            print("[✗] Belum terkoneksi ke Roblox Studio")
            return False
        
        try:
            print(f"[*] Mengirim command: {command}")
            payload = {
                "jsonrpc": "2.0",
                "method": command,
                "params": args or {},
                "id": 1
            }
            print(f"[>] Payload: {json.dumps(payload, indent=2)}")
            return True
            
        except Exception as e:
            print(f"[✗] Error send command: {e}")
            return False
    
    def list_open_places(self):
        """List semua tempat/game yang terbuka di Studio"""
        return self.send_command("listOpenPlaces")
    
    def save_place(self, place_id: str = None):
        """Save tempat/game yang sedang dibuka"""
        return self.send_command("savePlace", {"placeId": place_id})
    
    def run_script(self, script_content: str):
        """Jalankan Lua script di Studio"""
        return self.send_command("executeScript", {"script": script_content})
    
    def play(self):
        """Jalankan mode Play di Studio"""
        return self.send_command("play")
    
    def stop(self):
        """Stop mode Play"""
        return self.send_command("stop")
    
    def disconnect(self):
        """Putus koneksi dari Roblox Studio"""
        self.is_connected = False
        print("[✓] Disconnected dari Roblox Studio")


def main():
    print("=" * 60)
    print("ROBLOX STUDIO MCP CLIENT")
    print("=" * 60)
    print()
    
    client = RobloxMCPClient()
    
    # Menu interaktif
    while True:
        print("\n[MENU]")
        print("1. Connect ke Roblox Studio")
        print("2. Check MCP Server Status")
        print("3. List Open Places")
        print("4. Save Place")
        print("5. Play")
        print("6. Stop")
        print("7. Run Lua Script")
        print("8. Disconnect")
        print("9. Exit")
        print("-" * 60)
        
        choice = input("Pilih menu (1-9): ").strip()
        
        if choice == "1":
            client.connect()
        
        elif choice == "2":
            client.check_mcp_server()
        
        elif choice == "3":
            client.list_open_places()
        
        elif choice == "4":
            place_id = input("Masukkan Place ID (atau kosongkan): ").strip() or None
            client.save_place(place_id)
        
        elif choice == "5":
            client.play()
        
        elif choice == "6":
            client.stop()
        
        elif choice == "7":
            print("Masukkan Lua script (ketik 'END' di baris terakhir):")
            lines = []
            while True:
                line = input()
                if line == "END":
                    break
                lines.append(line)
            script = "\n".join(lines)
            client.run_script(script)
        
        elif choice == "8":
            client.disconnect()
        
        elif choice == "9":
            print("[*] Exiting...")
            break
        
        else:
            print("[✗] Input tidak valid")


if __name__ == "__main__":
    main()