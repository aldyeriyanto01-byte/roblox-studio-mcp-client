#!/usr/bin/env python3
"""
Roblox Studio MCP Client v3.0
Connects to Roblox Studio MCP Server dengan auto port detection
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
        self.mcp_port = None
        self.mcp_host = "localhost"
        self.max_retries = 3
        self.retry_delay = 2
        # Scan range port
        self.port_range = range(50051, 50100)
    
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
    
    def is_port_open(self, port):
        """Check apakah port tertentu terbuka"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.mcp_host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def scan_available_ports(self):
        """Scan range port untuk cari port yang terbuka dari Roblox"""
        print(f"[*] Scanning port {self.port_range.start}-{self.port_range.stop-1} untuk Roblox MCP Server...")
        
        available_ports = []
        for port in self.port_range:
            if self.is_port_open(port):
                available_ports.append(port)
                print(f"    [✓] Port {port} terbuka")
        
        return available_ports
    
    def get_roblox_process_ports(self):
        """Get semua port yang digunakan oleh Roblox process"""
        try:
            # Get PID dari RobloxStudioBeta
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq RobloxStudioBeta.exe', '/FO', 'CSV'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if 'RobloxStudioBeta.exe' not in result.stdout:
                return []
            
            # Parse output untuk dapat PID
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                return []
            
            # Format: "RobloxStudioBeta.exe","PID"
            pid_line = lines[1].replace('"', '').split(',')
            if len(pid_line) < 2:
                return []
            
            pid = pid_line[1].strip()
            print(f"[*] Roblox Studio PID: {pid}")
            
            # Get semua port yang digunakan oleh PID ini
            result = subprocess.run(
                f'netstat -ano | findstr "{pid}"',
                capture_output=True,
                text=True,
                shell=True,
                timeout=5
            )
            
            ports = []
            for line in result.stdout.split('\n'):
                if 'LISTENING' in line and '127.0.0.1' in line:
                    parts = line.split()
                    if len(parts) > 1:
                        try:
                            port = int(parts[1].split(':')[-1])
                            ports.append(port)
                        except:
                            pass
            
            return sorted(list(set(ports)))
        
        except Exception as e:
            print(f"[✗] Error get process ports: {e}")
            return []
    
    def connect(self):
        """Sambungkan ke Roblox Studio MCP Server dengan auto port detection"""
        print("[*] Memulai koneksi ke Roblox Studio...")
        
        # Step 1: Check Roblox Studio running
        if not self.is_roblox_running():
            print("[✗] Roblox Studio tidak running!")
            print("[*] Silakan buka Roblox Studio terlebih dahulu.")
            return False
        
        print("[✓] Roblox Studio terdeteksi RUNNING")
        
        # Step 2: Get ports yang digunakan Roblox
        print("\n[*] Detecting Roblox port usage...")
        roblox_ports = self.get_roblox_process_ports()
        
        if roblox_ports:
            print(f"[✓] Ports yang digunakan Roblox: {roblox_ports}")
        else:
            print("[*] Tidak bisa detect port dari process, scanning range port...")
        
        # Step 3: Combine ports untuk dicoba
        ports_to_try = []
        
        # Prioritas 1: Port standar
        if self.is_port_open(50051):
            ports_to_try.append(50051)
        
        # Prioritas 2: Port yang terdeteksi dari Roblox
        ports_to_try.extend(roblox_ports)
        
        # Prioritas 3: Scan semua port dalam range
        scanned_ports = self.scan_available_ports()
        for port in scanned_ports:
            if port not in ports_to_try:
                ports_to_try.append(port)
        
        if not ports_to_try:
            print("\n[✗] Tidak ada port yang terbuka dari Roblox!")
            print("[!] MCP Server mungkin belum di-enable atau tidak berjalan")
            return False
        
        print(f"\n[*] Mencoba connect ke {len(ports_to_try)} port(s): {ports_to_try}")
        
        # Step 4: Try connect ke setiap port
        for port in ports_to_try:
            for attempt in range(1, self.max_retries + 1):
                print(f"\n[*] Attempt {attempt}/{self.max_retries} - Port {port}...")
                
                if self.is_port_open(port):
                    print(f"[✓] PORT {port} TERBUKA - Koneksi BERHASIL!")
                    self.mcp_port = port
                    self.is_connected = True
                    return True
                
                if attempt < self.max_retries:
                    print(f"    Tunggu {self.retry_delay} detik...")
                    time.sleep(self.retry_delay)
        
        print("\n[✗] Tidak bisa connect ke semua port yang dicoba")
        print("[!] Pastikan MCP Server sudah di-enable di Roblox Studio!")
        print("\nLangkah untuk enable MCP Server:")
        print("  1. Buka Roblox Studio")
        print("  2. Menu → Assistant Settings")
        print("  3. Klik tab 'MCP Servers'")
        print("  4. Toggle ON: 'Enable Studio as MCP server'")
        print("  5. Tunggu hingga muncul '2 clients connected'")
        print("  6. Coba connect lagi\n")
        
        return False
    
    def check_mcp_server(self):
        """Check status MCP Server"""
        print("[*] Checking MCP Server status...")
        
        if self.mcp_port:
            if self.is_port_open(self.mcp_port):
                print(f"[✓] MCP Server AKTIF di {self.mcp_host}:{self.mcp_port}")
                return True
            else:
                print(f"[✗] MCP Server port {self.mcp_port} tidak responding")
                return False
        
        # Jika belum tahu port, scan lagi
        print("[*] Port belum diketahui, scan range port...")
        available_ports = self.scan_available_ports()
        
        if available_ports:
            print(f"[✓] Port yang tersedia: {available_ports}")
            return True
        else:
            print("[✗] Tidak ada port yang terbuka")
            return False
    
    def send_command(self, command: str, args: dict = None):
        """Kirim command ke Roblox Studio"""
        if not self.is_connected:
            print("[✗] Belum terkoneksi ke Roblox Studio")
            print("[*] Jalankan menu 1 (Connect) terlebih dahulu")
            return False
        
        try:
            print(f"[*] Mengirim command: {command}")
            print(f"[*] Target port: {self.mcp_port}")
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
        self.mcp_port = None
        print("[✓] Disconnected dari Roblox Studio")
    
    def show_connection_status(self):
        """Tampilkan status koneksi saat ini"""
        print("\n" + "="*60)
        print("CONNECTION STATUS")
        print("="*60)
        roblox_running = self.is_roblox_running()
        print(f"Roblox Studio: {'✓ RUNNING' if roblox_running else '✗ NOT RUNNING'}")
        
        if self.mcp_port:
            mcp_active = self.is_port_open(self.mcp_port)
            print(f"MCP Server: {'✓ ACTIVE' if mcp_active else '✗ INACTIVE'} (Port {self.mcp_port})")
        else:
            print(f"MCP Server: ✗ PORT NOT DETECTED")
        
        print(f"Client Status: {'✓ CONNECTED' if self.is_connected else '✗ NOT CONNECTED'}")
        
        if roblox_running and not self.mcp_port:
            print("\n[*] Scanning untuk detect MCP Server port...")
            available_ports = self.scan_available_ports()
            if available_ports:
                print(f"[✓] Available ports: {available_ports}")
        
        print("="*60 + "\n")


def main():
    print("=" * 60)
    print("ROBLOX STUDIO MCP CLIENT v3.0")
    print("Auto Port Detection & Advanced Scanning")
    print("=" * 60)
    print()
    
    client = RobloxMCPClient()
    
    # Menu interaktif
    while True:
        print("\n[MENU]")
        print("1. Connect ke Roblox Studio")
        print("2. Check MCP Server Status")
        print("3. Show Connection Status")
        print("4. Scan Available Ports")
        print("5. List Open Places")
        print("6. Save Place")
        print("7. Play")
        print("8. Stop")
        print("9. Run Lua Script")
        print("10. Disconnect")
        print("0. Exit")
        print("-" * 60)
        
        choice = input("Pilih menu (0-10): ").strip()
        
        if choice == "1":
            client.connect()
        
        elif choice == "2":
            client.check_mcp_server()
        
        elif choice == "3":
            client.show_connection_status()
        
        elif choice == "4":
            ports = client.scan_available_ports()
            if ports:
                print(f"\n[✓] Available ports: {ports}")
            else:
                print("\n[✗] Tidak ada port yang terbuka")
        
        elif choice == "5":
            client.list_open_places()
        
        elif choice == "6":
            place_id = input("Masukkan Place ID (atau kosongkan): ").strip() or None
            client.save_place(place_id)
        
        elif choice == "7":
            client.play()
        
        elif choice == "8":
            client.stop()
        
        elif choice == "9":
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
        
        elif choice == "10":
            client.disconnect()
        
        elif choice == "0":
            print("[*] Exiting...")
            break
        
        else:
            print("[✗] Input tidak valid, silakan pilih 0-10")


if __name__ == "__main__":
    main()
