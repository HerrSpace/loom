
cd ~
pyvenv-3.4 venv
source venv/bin/activate
pip install -r requirements.txt
sopel
# Do what you must
loginctl enable-linger $USER
mkdir ~/.config/systemd/
ln -s ~/loom/systemd/ ~/.config/systemd/user
