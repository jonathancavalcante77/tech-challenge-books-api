import subprocess
import time
import requests
import sys
import os

# Configuration
API_URL = "http://127.0.0.1:8000"
LOG_FILE = "smoke_test.log"

def log(message):
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode("ascii", "ignore").decode("ascii"))
        
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def run_tests():
    # Clear log file
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"Smoke Test Started at {time.ctime()}\n")
        f.write("="*50 + "\n")

    log("[INFO] Iniciando servidor Uvicorn...")
    # Start process
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    failed = False
    
    try:
        # Wait for server to start
        max_retries = 15
        server_up = False
        for i in range(max_retries):
            try:
                requests.get(f"{API_URL}/api/v1/health")
                server_up = True
                break
            except requests.ConnectionError:
                time.sleep(1)
                log(f"[WAIT] Aguardando servidor... ({i+1}/{max_retries})")
        
        if not server_up:
            log("[ERROR] Servidor nao iniciou a tempo.")
            return 1

        log("[INFO] Servidor Online. Iniciando bateria de testes...")

        # 1. Testes Públicos (Core)
        log("\n--- [1] Testando Endpoints Públicos ---")
        public_tests = [
            {"url": "/api/v1/health", "expected": 200},
            {"url": "/api/v1/books?limit=1", "expected": 200},
            {"url": "/api/v1/stats/overview", "expected": 200},
            {"url": "/api/v1/books/top-rated?limit=3", "expected": 200},
            {"url": "/api/v1/books/99999", "expected": 404}
        ]
        
        for case in public_tests:
            if not check_endpoint(case["url"], case["expected"]):
                failed = True

        # 2. Testes de Autenticação (JWT)
        log("\n--- [2] Testando Autenticação (JWT) ---")
        token = None
        
        # 2.1 Login Falha
        log("Testando Login Inválido...")
        res = requests.post(f"{API_URL}/api/v1/auth/login", json={"username": "wrong", "password": "pass"})
        if res.status_code == 401:
            log("[OK] Login Inválido recusado corretamente (401)")
        else:
            log(f"[FAIL] Falha: Login inválido retornou {res.status_code}")
            failed = True
            
        # 2.2 Login Sucesso
        log("Testando Login Admin...")
        res = requests.post(f"{API_URL}/api/v1/auth/login", json={"username": "admin", "password": "secret"})
        if res.status_code == 200:
            token = res.json().get("access_token")
            log("[OK] Login Admin com sucesso. Token obtido.")
        else:
            log(f"[FAIL] Falha no login admin: {res.status_code} - {res.text}")
            failed = True
            
        # 3. Testes Protegidos
        if token:
            log("\n--- [3] Testando Endpoints Protegidos ---")
            headers = {"Authorization": f"Bearer {token}"}
            
            # 3.1 Trigger Scraping
            log("Disparando Scraping (Protegido)...")
            res = requests.post(f"{API_URL}/api/v1/scraping/trigger", headers=headers)
            if res.status_code == 200:
                log("[OK] Scraping disparado com sucesso.")
            else:
                log(f"[FAIL] Falha no scraping trigger: {res.status_code} - {res.text}")
                failed = True
                
            # 3.2 Refresh Token
            log("Testando Refresh Token...")
            res = requests.post(f"{API_URL}/api/v1/auth/refresh", headers=headers)
            if res.status_code == 200:
                log("[OK] Token renovado com sucesso.")
            else:
                log(f"[FAIL] Falha no refresh token: {res.status_code}")
                failed = True
        else:
            log("[WARN] Plando testes protegidos pois não há token.")
            failed = True

        # 4. Testes ML (Bônus)
        log("\n--- [4] Testando Endpoints ML ---")
        
        # 4.1 Features
        if check_endpoint("/api/v1/ml/features", 200):
            pass # Check function logs success/fail
        else:
            failed = True
            
        # 4.2 Predictions
        log("Testando Predição (Mock)...")
        pred_payload = {"price": 60.0, "rating": 5}
        res = requests.post(f"{API_URL}/api/v1/ml/predictions", json=pred_payload)
        if res.status_code == 200:
            data = res.json()
            if "predicted_category" in data:
                log(f"[OK] Predição retornou: {data['predicted_category']}")
            else:
                log("[FAIL] Predição retornou JSON inválido.")
                failed = True
        else:
            log(f"[FAIL] Falha na predição: {res.status_code}")
            failed = True

    except Exception as e:
        log(f"[ERROR] Erro crítico no script: {e}")
        failed = True
    finally:
        log("\n[INFO] Encerrando servidor...")
        process.terminate()
        process.wait()
    
    if failed:
        log("\nRESULTADO FINAL: [FAIL]")
        return 1
    else:
        log("\nRESULTADO FINAL: [SUCCESS] - Todos os sistemas operacionais.")
        return 0

def check_endpoint(endpoint, expected_code):
    try:
        url = f"{API_URL}{endpoint}"
        response = requests.get(url)
        status = response.status_code
        
        if status == expected_code:
            log(f"[OK] {endpoint}: OK ({status})")
            return True
        else:
            log(f"[FAIL] {endpoint}: Falha (Recebido: {status}, Esperado: {expected_code})")
            return False
    except Exception as e:
        log(f"[ERROR] {endpoint}: Erro de conexão ({e})")
        return False

if __name__ == "__main__":
    sys.exit(run_tests())
