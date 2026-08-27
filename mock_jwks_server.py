"""
mock_jwks_server.py — Simule le endpoint JWKS de Supabase localement, avec
une VRAIE paire de clés EC (P-256) et une VRAIE signature ES256. Ne teste
pas "un faux JWT" : teste le même mécanisme cryptographique exact que
Supabase utilise (asymétrique, JWKS, kid), juste avec une clé générée
localement plutôt que celle de Supabase — nécessaire car mon bac à sable
ne peut pas atteindre supabase.co (limite réseau déjà documentée, ADR-033).
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from cryptography.hazmat.primitives.asymmetric import ec
import jwt
from jwt.algorithms import ECAlgorithm

KID = "test-key-1"

_private_key = ec.generate_private_key(ec.SECP256R1())
_public_key = _private_key.public_key()

_alg = ECAlgorithm(ECAlgorithm.SHA256)
_jwk = json.loads(_alg.to_jwk(_public_key))
_jwk["kid"] = KID
_jwk["use"] = "sig"
_jwk["alg"] = "ES256"
JWKS = {"keys": [_jwk]}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/auth/v1/.well-known/jwks.json":
            body = json.dumps(JWKS).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args):
        pass  # silence les logs HTTP par défaut


def demarrer_serveur(port=8765):
    server = HTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def creer_token(payload: dict) -> str:
    """Signe un token exactement comme Supabase le ferait pour un projet
    migré vers les clés asymétriques : ES256, avec le kid dans l'en-tête."""
    return jwt.encode(payload, _private_key, algorithm="ES256", headers={"kid": KID})
