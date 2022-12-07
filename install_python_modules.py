import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install('ecdsa')
install('numpy')
install('sqlalchemy')
install('requests')
install('pyaes')
install('pycryptodomex')