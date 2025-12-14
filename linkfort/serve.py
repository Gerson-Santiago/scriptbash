import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 7777
Handler = http.server.SimpleHTTPRequestHandler

def serve():
    # Garante que estamos no diretório do script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    url = f"http://localhost:{PORT}/dashboard.html"
    
    print("\n" + "="*50)
    print(f"🚀  LINKFORT DASHBOARD SERVER")
    print("="*50)
    print(f"📡  Servindo em: {url}")
    print("⌨️   Pressione Ctrl+C para parar o servidor.")
    print("="*50 + "\n")
    
    # Tenta abrir o navegador
    try:
        webbrowser.open(url)
    except Exception:
        print(f"⚠️  Não foi possível abrir o navegador automaticamente. Acesse: {url}")

    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 98:
            print(f"❌  Erro: A porta {PORT} já está em uso.")
            print("    Tente fechar outros processos python ou mude a porta.")
        else:
            raise
    except KeyboardInterrupt:
        print("\n🛑  Servidor parando... Até logo!")
        sys.exit(0)

if __name__ == "__main__":
    serve()
