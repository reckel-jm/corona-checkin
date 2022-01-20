pip install -r requirements.txt
git clone https://github.com/HQJaTu/vacdec.git
pip install -r vacdec/requirements.txt
python vacdec/fetch-signing-certificates.py
mv certs vacdec/certs
echo "Setup Complete. The program should be usuable now."