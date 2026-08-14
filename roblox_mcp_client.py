#!/usr/bin/env python3
"""
Roblox Studio MCP Client
Connects to Roblox Studio MCP Server untuk mengontrol Studio
"""

import subprocess
import json
import sys
import os
import time
import socket
from pathlib import Path

class RobloxMCPClient:
    def __init__(self):
        self.mcp_server_cmd = "cmd.exe"
        self.mcp_server_args = ["/d", "/s", "/c", "cd /d %LOCALAPPDATA%\\Roblox && .\\mcp.bat"]
        self.is_connected = False
        self.mcp_port = 50051
        self.mcp_host = "localhost"
        self.max_retries = 3
        self.retry_delay = 2
    
    def is_roblox_running(self):
        """Check apakah Roblox Studio running"""
        try:
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq RobloxStudioBeta.exe'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return 'RobloxStudioBeta.exe' in result.stdout
        except Exception as e:
            print(f"[✗] Error check Roblox: {e}")
            return False
    
    def is_mcp_port_open(self):
        """Check apakah MCP Server port terbuka"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.mcp_host, self.mcp_port))
            sock.close()
            return result == 0
        except Exception as e:
            print(f"[✗] Socket error: {e}")
            return False
    
    def start_mcp_server(self):
        """Coba start MCP Server"""
        try:
            print("[*] Mencoba start MCP Server...")
            # Jalankan mcp.bat di background
            subprocess.Popen(
                self.mcp_server_args,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("[*] MCP Server process dimulai, tunggu 3 detik...")
            time.sleep(3)
            return True
        except Exception as e:
            print(f"[✗] Error start MCP Server: {e}")
            return False
    
    def connect(self):
        """Sambungkan ke Roblox Studio MCP Server dengan retry logic"""
        print("[*] Memulai koneksi ke Roblox Studio...")
        
        # Step 1: Check Roblox Studio running
        if not self.is_roblox_running():
            print("[✗] Roblox Studio tidak running!")
            print("[*] Silakan buka Roblox Studio terlebih dahulu.")
            return False
        
        print("[✓] Roblox Studio terdeteksi RUNNING")
        
        # Step 2: Try connect ke MCP Server dengan retry
        for attempt in range(1, self.max_retries + 1):
            print(f"\n[*] Attempt {attempt}/{self.max_retries} - Cek MCP Server port {self.mcp_port}...")
            
            if self.is_mcp_port_open():
                print("[✓] MCP Server PORT TERBUKA - Koneksi BERHASIL!")
                self.is_connected = True
                return True
            
            if attempt < self.max_retries:
                print(f"[*] Port belum terbuka, tunggu {self.retry_delay} detik sebelum retry...")
                time.sleep(self.retry_delay)
        
        # Step 3: Jika semua attempt gagal, tawarkan untuk start MCP Server
        print("\n[✗] MCP Server tidak merespons di semua attempt")
        print("[!] Pastikan MCP Server sudah di-enable di Roblox Studio!")
        print("\nLangkah untuk enable MCP Server:")
        print("  1. Buka Roblox Studio")
        print("  2. Menu → Assistant Settings")
        print("  3. Toggle ON: 'Enable Studio as MCP server'")
        print("  4. Tunggu hingga muncul '2 clients connected'")
        print("  5. Coba connect lagi\n")
        
        return False
    
    def check_mcp_server(self):
        """Check status MCP Server dengan detail"""
        print("[*] Checking MCP Server status...")
        
        # Method 1: Check port
        if self.is_mcp_port_open():
            print(f"[✓] MCP Server AKTIF di {self.mcp_host}:{self.mcp_port}")
            self.is_connected = True
            return True
        
        # Method 2: Check via netstat
        try:
            result = subprocess.run(
                f'netstat -ano | findstr ":{self.mcp_port}"',
                capture_output=True,
                text=True,
                shell=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout:
                print(f"[✓] MCP Server process terdeteksi di port {self.mcp_port}")
                self.is_connected = True
                return True
        except Exception as e:
            print(f"[✗] Netstat check error: {e}")
        
        print("[✗] MCP Server tidak merespons")
        print("[!] Silakan enable MCP Server di Assistant Settings → Roblox Studio")
        return False
    
    def send_command(self, command: str, args: dict = None):
        """Kirim command ke Roblox Studio"""
        if not self.is_connected:
            print("[✗] Belum terkoneksi ke Roblox Studio")
            print("[*] Jalankan menu 1 (Connect) terlebih dahulu")
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
            print("[✓] Command terkirim!")
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
    
    def show_connection_status(self):
        """Tampilkan status koneksi saat ini"""
        print("\n" + "="*60)
        print("CONNECTION STATUS")
        print("="*60)
        print(f"Roblox Studio: {'✓ RUNNING' if self.is_roblox_running() else '✗ NOT RUNNING'}")
        print(f"MCP Server: {'✓ CONNECTED' if self.is_mcp_port_open() else '✗ NOT CONNECTED'}")
        print(f"Client Status: {'✓ CONNECTED' if self.is_connected else '✗ NOT CONNECTED'}")
        print("="*60 + "\n")


def main():
    print("=" * 60)
    print("ROBLOX STUDIO MCP CLIENT v2.0")
    print("Updated with better error handling & auto-retry")
    print("=" * 60)
    print()
    
    client = RobloxMCPClient()
    
    # Menu interaktif
    while True:
        print("\n[MENU]")
        print("1. Connect ke Roblox Studio")
        print("2. Check MCP Server Status")
        print("3. Show Connection Status")
        print("4. List Open Places")
        print("5. Save Place")
        print("6. Play")
        print("7. Stop")
        print("8. Run Lua Script")
        print("9. Disconnect")
        print("0. Exit")
        print("-" * 60)
        
        choice = input("Pilih menu (0-9): ").strip()
        
        if choice == "1":
            client.connect()
        
        elif choice == "2":
            client.check_mcp_server()
        
        elif choice == "3":
            client.show_connection_status()
        
        elif choice == "4":
            client.list_open_places()
        
        elif choice == "5":
            place_id = input("Masukkan Place ID (atau kosongkan): ").strip() or None
            client.save_place(place_id)
        
        elif choice == "6":
            client.play()
        
        elif choice == "7":
            client.stop()
        
        elif choice == "8":
            print("Masukkan Lua script (ketik 'END' di baris terakhir):")
            lines = []
            while True:
                line = input()
                if line == "END":
                    break
                lines.append(line)
            script = "\n".join(lines)
            if script:
                client.run_script(script)
            else:
                print("[✗] Script kosong!")
        
        elif choice == "9":
            client.disconnect()
        
        elif choice == "0":
            print("[*] Exiting...")
            break
        
        else:
            print("[✗] Input tidak valid, silakan pilih 0-9")


if __name__ == "__main__":
    main()
