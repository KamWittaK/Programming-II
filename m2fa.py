import pyotp
import qrcode

# Generate a random secret key
secret_key = pyotp.random_base32()

# Create a TOTP object
totp = pyotp.TOTP(secret_key)

# Generate the QR code URL
qr_url = totp.provisioning_uri(name='Kameron', issuer_name='CTrack')

# Generate QR code
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(qr_url)
qr.make(fit=True)

# Create an image from the QR Code instance
img = qr.make_image(fill='black', back_color='white')

# Save the image
img.save('authenticator_qr.png')

print("QR Code generated and saved as 'authenticator_qr.png'")
print("Secret Key:", secret_key)
