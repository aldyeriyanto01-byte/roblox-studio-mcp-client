#!/usr/bin/env python3
"""
Roblox Studio Controller v4.0
Uses Roblox REST API dengan secure API Key handling
"""

import requests
import json
import sys
import os
import time
from pathlib import Path
from dotenv import load_dotenv, set_key

class RobloxAPIClient:
    def __init__(self):
        # Load dari .env file
        load_dotenv()
        self.api_key = os.getenv('ROBLOX_API_KEY')
        self.user_id = os.getenv('ROBLOX_USER_ID')
        self.base_url = "https://apis.roblox.com"
        self.create_url = "https://create.roblox.com/v1"
        self.is_authenticated = False
        self.env_file = Path(".env")
        
        if self.api_key and self.user_id:
            self.is_authenticated = self.verify_credentials()
    
    def setup_credentials(self):
        """Setup API Key dan User ID untuk pertama kali"""
        print("\n" + "="*60)
        print("ROBLOX API KEY SETUP")
        print("="*60)
        print("\n[*] Untuk mendapatkan API Key:")
        print("    1. Buka https://create.roblox.com/dashboard/credentials")
        print("    2. Login dengan akun Roblox Developer")
        print("    3. Buat API Key baru")
        print("    4. Copy dan paste di bawah")
        print("\n⚠️  API Key akan disimpan di file .env (JANGAN di-commit!)\n")
        
        api_key = input("Masukkan Roblox API Key: ").strip()
        if not api_key:
            print("[✗] API Key kosong!")
            return False
        
        user_id = input("Masukkan Roblox User ID (bisa cek di profile URL): ").strip()
        if not user_id:
            print("[✗] User ID kosong!")
            return False
        
        # Save ke .env file
        try:
            set_key(self.env_file, "ROBLOX_API_KEY", api_key)
            set_key(self.env_file, "ROBLOX_USER_ID", user_id)
            print("\n[✓] Credentials disimpan di .env file")
            
            self.api_key = api_key
            self.user_id = user_id
            
            if self.verify_credentials():
                print("[✓] Credentials valid!")
                return True
            else:
                print("[✗] Credentials tidak valid, coba lagi")
                return False
                
        except Exception as e:
            print(f"[✗] Error save credentials: {e}")
            return False
    
    def verify_credentials(self):
        """Verify apakah API Key valid"""
        try:
            print("[*] Verifying credentials...")
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.create_url}/universes",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                print("[✓] API Key valid!")
                self.is_authenticated = True
                return True
            else:
                print(f"[✗] API Key invalid (Status: {response.status_code})")
                return False
                
        except Exception as e:
            print(f"[✗] Error verify credentials: {e}")
            return False
    
    def get_universes(self):
        """Get semua universes/games milik user"""
        if not self.is_authenticated:
            print("[✗] Belum authenticated! Setup credentials dulu (Menu 1)")
            return []
        
        try:
            print("[*] Fetching universes...")
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.create_url}/universes",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                universes = data.get('data', [])
                
                if universes:
                    print(f"\n[✓] Found {len(universes)} universe(s):\n")
                    for idx, uni in enumerate(universes, 1):
                        print(f"  {idx}. {uni.get('name', 'Unknown')}")
                        print(f"     ID: {uni.get('id')}")
                        print(f"     Description: {uni.get('description', 'N/A')}")
                        print()
                    return universes
                else:
                    print("[*] Tidak ada universes ditemukan")
                    return []
            else:
                print(f"[✗] Error: {response.status_code}")
                print(f"    {response.text}")
                return []
                
        except Exception as e:
            print(f"[✗] Error get universes: {e}")
            return []
    
    def get_universe_info(self, universe_id):
        """Get info tentang universe tertentu"""
        if not self.is_authenticated:
            print("[✗] Belum authenticated!")
            return None
        
        try:
            print(f"[*] Fetching universe {universe_id} info...")
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.create_url}/universes/{universe_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n[✓] Universe Info:")
                print(f"    Name: {data.get('name')}")
                print(f"    ID: {data.get('id')}")
                print(f"    Description: {data.get('description')}")
                print(f"    Status: {data.get('status')}")
                print()
                return data
            else:
                print(f"[✗] Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[✗] Error get universe info: {e}")
            return None
    
    def get_places(self, universe_id):
        """Get semua places dalam universe"""
        if not self.is_authenticated:
            print("[✗] Belum authenticated!")
            return []
        
        try:
            print(f"[*] Fetching places untuk universe {universe_id}...")
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.create_url}/universes/{universe_id}/places",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                places = data.get('data', [])
                
                if places:
                    print(f"\n[✓] Found {len(places)} place(s):\n")
                    for idx, place in enumerate(places, 1):
                        print(f"  {idx}. {place.get('name', 'Unknown')}")
                        print(f"     ID: {place.get('id')}")
                        print()
                    return places
                else:
                    print("[*] Tidak ada places ditemukan")
                    return []
            else:
                print(f"[✗] Error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[✗] Error get places: {e}")
            return []
    
    def update_place_config(self, universe_id, place_id, config):
        """Update konfigurasi place"""
        if not self.is_authenticated:
            print("[✗] Belum authenticated!")
            return False
        
        try:
            print(f"[*] Updating place {place_id} config...")
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.patch(
                f"{self.create_url}/universes/{universe_id}/places/{place_id}",
                headers=headers,
                json=config,
                timeout=10
            )
            
            if response.status_code == 200:
                print("[✓] Place config updated!")
                return True
            else:
                print(f"[✗] Error: {response.status_code}")
                print(f"    {response.text}")
                return False
                
        except Exception as e:
            print(f"[✗] Error update place config: {e}")
            return False
    
    def publish_place(self, universe_id, place_id, lua_script_path):
        """Publish/update script ke place"""
        if not self.is_authenticated:
            print("[✗] Belum authenticated!")
            return False
        
        try:
            # Read script file
            with open(lua_script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            print(f"[*] Publishing script ke place {place_id}...")
            print(f"    Script size: {len(script_content)} bytes")
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "script": script_content
            }
            
            response = requests.post(
                f"{self.create_url}/universes/{universe_id}/places/{place_id}/publish",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                print("[✓] Script published!")
                return True
            else:
                print(f"[✗] Error: {response.status_code}")
                print(f"    {response.text}")
                return False
                
        except FileNotFoundError:
            print(f"[✗] Script file not found: {lua_script_path}")
            return False
        except Exception as e:
            print(f"[✗] Error publish place: {e}")
            return False
    
    def show_status(self):
        """Show authentication status"""
        print("\n" + "="*60)
        print("AUTHENTICATION STATUS")
        print("="*60)
        
        if self.api_key and self.user_id:
            print(f"✓ API Key: {self.api_key[:20]}...")
            print(f"✓ User ID: {self.user_id}")
            print(f"✓ Status: {'AUTHENTICATED' if self.is_authenticated else 'NOT VERIFIED'}")
        else:
            print("✗ No credentials found")
            print("  Run Menu 1 (Setup Credentials) first")
        
        print("="*60 + "\n")


def main():
    print("=" * 60)
    print("ROBLOX STUDIO CONTROLLER v4.0")
    print("REST API Integration with Secure Credentials")
    print("=" * 60)
    print()
    
    client = RobloxAPIClient()
    
    # Cek apakah .env exist, jika tidak prompt setup
    if not client.is_authenticated:
        print("[!] Credentials tidak ditemukan")
        choice = input("Setup credentials sekarang? (y/n): ").strip().lower()
        if choice == 'y':
            if not client.setup_credentials():
                print("[✗] Setup gagal, exit")
                sys.exit(1)
        else:
            print("[*] Skipping setup, anda bisa setup nanti dari menu")
    
    # Menu interaktif
    while True:
        print("\n[MENU]")
        print("1. Setup Credentials (API Key + User ID)")
        print("2. Show Authentication Status")
        print("3. List All Universes")
        print("4. Get Universe Info")
        print("5. Get Places in Universe")
        print("6. Update Place Config")
        print("7. Publish Script to Place")
        print("0. Exit")
        print("-" * 60)
        
        choice = input("Pilih menu (0-7): ").strip()
        
        if choice == "1":
            if client.setup_credentials():
                print("[✓] Setup berhasil!")
            else:
                print("[✗] Setup gagal")
        
        elif choice == "2":
            client.show_status()
        
        elif choice == "3":
            universes = client.get_universes()
        
        elif choice == "4":
            universe_id = input("Masukkan Universe ID: ").strip()
            if universe_id.isdigit():
                client.get_universe_info(universe_id)
            else:
                print("[✗] Invalid Universe ID")
        
        elif choice == "5":
            universe_id = input("Masukkan Universe ID: ").strip()
            if universe_id.isdigit():
                places = client.get_places(universe_id)
            else:
                print("[✗] Invalid Universe ID")
        
        elif choice == "6":
            universe_id = input("Masukkan Universe ID: ").strip()
            place_id = input("Masukkan Place ID: ").strip()
            
            if universe_id.isdigit() and place_id.isdigit():
                print("\nUpdate config (JSON format, or press Enter to skip):")
                print("Contoh: {\"description\": \"New description\"}")
                config_str = input("Config: ").strip()
                
                if config_str:
                    try:
                        config = json.loads(config_str)
                        client.update_place_config(universe_id, place_id, config)
                    except json.JSONDecodeError:
                        print("[✗] Invalid JSON format")
                else:
                    print("[*] Skipped")
            else:
                print("[✗] Invalid IDs")
        
        elif choice == "7":
            universe_id = input("Masukkan Universe ID: ").strip()
            place_id = input("Masukkan Place ID: ").strip()
            script_path = input("Masukkan path ke Lua script file: ").strip()
            
            if universe_id.isdigit() and place_id.isdigit():
                client.publish_place(universe_id, place_id, script_path)
            else:
                print("[✗] Invalid IDs")
        
        elif choice == "0":
            print("[*] Exiting...")
            break
        
        else:
            print("[✗] Input tidak valid, silakan pilih 0-7")


if __name__ == "__main__":
    main()
