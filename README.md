# Roblox Studio Controller v4.0

Kontrol Roblox Studio menggunakan **REST API** dengan secure credential management.

## 🚀 Fitur

- ✅ Secure API Key storage (.env file)
- ✅ List all universes/games
- ✅ Get universe dan place information
- ✅ Update place configuration
- ✅ Publish scripts to places
- ✅ Interactive CLI menu

## 📋 Requirements

```bash
pip install -r requirements.txt
```

Dependencies:
- `requests` - HTTP library untuk API calls
- `python-dotenv` - Load environment variables dari .env

## 🔐 Setup

### 1. Dapatkan API Key

1. Buka https://create.roblox.com/dashboard/credentials
2. Login dengan akun Roblox Developer
3. Buat **API Key** baru
4. Copy API Key tersebut

### 2. Dapatkan User ID

- User ID bisa dilihat di URL profile Anda
- Format: https://www.roblox.com/users/{USER_ID}/profile

### 3. Run Script & Setup

```bash
python roblox_mcp_client.py
```

Saat pertama kali run, script akan:
1. Mendeteksi bahwa credentials belum ada
2. Menanyakan untuk setup
3. Minta API Key dan User ID
4. Simpan ke file `.env` (git-ignored, aman)
5. Verify credentials

## 📝 Usage

```bash
python roblox_mcp_client.py
```

### Menu Options

1. **Setup Credentials** - Setup atau update API Key + User ID
2. **Show Authentication Status** - Lihat status login
3. **List All Universes** - Lihat semua game Anda
4. **Get Universe Info** - Detail game tertentu
5. **Get Places in Universe** - Lihat semua place/level
6. **Update Place Config** - Update konfigurasi place
7. **Publish Script to Place** - Upload script Lua ke place
8. **Exit**

## 🔒 Security

- ✅ API Key disimpan di `.env` (tidak di-commit)
- ✅ `.gitignore` melindungi file sensitif
- ✅ Jangan pernah share API Key di public
- ✅ Jika API Key leak, revoke segera di dashboard

## ⚠️ Important

- **JANGAN commit `.env` file** - Sudah di-gitignore
- **JANGAN share API Key** - Itu credential sensitif
- Jika leak, **REVOKE segera** di https://create.roblox.com/dashboard/credentials

## 📚 API Endpoints

Script ini menggunakan Roblox REST API v1:
- `GET /universes` - List universes
- `GET /universes/{id}` - Universe info
- `GET /universes/{id}/places` - List places
- `PATCH /universes/{id}/places/{id}` - Update place
- `POST /universes/{id}/places/{id}/publish` - Publish script

## 🐛 Troubleshooting

### "API Key invalid"
- Pastikan API Key benar
- Cek di https://create.roblox.com/dashboard/credentials
- Revoke dan buat API Key baru

### "No universes found"
- Pastikan User ID benar
- Pastikan akun punya minimal 1 universe/game

### "Connection timeout"
- Cek internet connection
- Roblox API server mungkin down
- Coba lagi dalam beberapa menit

## 📄 License

MIT License - Free to use

---

**Created by:** aldyeriyanto01-byte  
**Version:** 4.0  
**Updated:** 2026-08-14
