import os.path
import os
import pyodbc
import sqlalchemy
from urllib.parse import quote_plus
from cryptography.fernet import Fernet

def connect_to_database(host=None, database=None, username=None, password=None, driver = 'pyodbc', dialect='mssql', driver2='ODBC Driver 18 for SQL Server', mode='read', fast_execution=True):
	# Load credentials if not provided
	data_warehouse_credentials = {'username':'python','password':retrieve_password('dw_python'),'host':'fcazdwprod02','database':'data'}
	
	if host is None:
		host = data_warehouse_credentials['host']
	if database is None:
		database = data_warehouse_credentials['database']
	if username is None:
		username = data_warehouse_credentials['username']
	if password is None:
		password = data_warehouse_credentials['password']

	# Disable connection pooling in pyodbc
	pyodbc.pooling = False

	if mode == 'read':
		# Use pyodbc directly for read connections
		conn = pyodbc.connect(
			f'Driver={{ODBC Driver 18 for SQL Server}};'
			f'Server={host};Database={database};'
			f'UID={username};PWD={password}'
		)
	elif mode == 'write':
		# Construct the connection string explicitly without using odbc_connect
		connection_url = f'{dialect}+pyodbc://{username}:{password}@{host}/{database}?driver={quote_plus(driver2)}&TrustServerCertificate=yes'
		
		# Create SQLAlchemy engine for write mode
		engine = sqlalchemy.create_engine(connection_url, fast_executemany=fast_execution)
		conn = engine.connect()

	return conn

def save_password(password: str, name: str):
	"""
	Encrypt and save a password to a file.
	
	:param password: The password to encrypt.
	:param file_path: The path where the encrypted password will be stored.
	"""
	# Retrieve the key from environment variable
	key = os.getenv("FERNET")
	if not key:
		raise ValueError("FERNET environment variable not set!")

	cipher = Fernet(key.encode())

	# Encrypt the password
	encrypted_password = cipher.encrypt(password.encode())

	# Save encrypted password to file
	file_path = f"{name}.enc"
	with open(file_path, "wb") as f:
		f.write(encrypted_password)

	print(f"Password saved securely to {file_path}")

def retrieve_password(name: str) -> str:
	"""
	Retrieve and decrypt a password from a file.
	
	:param file_path: The path to the file storing the encrypted password.
	:return: The decrypted password.
	"""
	# Retrieve the key from environment variable
	key = os.getenv("FERNET")
	if not key:
		raise ValueError("FERNET environment variable not set!")

	cipher = Fernet(key.encode())

	file_path = f"{name}.enc"

	# Read encrypted password
	with open(file_path, "rb") as f:
		encrypted_password = f.read()

	# Decrypt password
	password = cipher.decrypt(encrypted_password).decode()

	return password


conn = connect_to_database(mode='write')

print(conn)