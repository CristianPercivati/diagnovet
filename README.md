# DiagnoVet

## Guide for local installation and usage:

Using the PowerShell terminal in VSCode, navigate to the project:

1. From *api/*: `pip install -r requirements.txt`
2. From *frontend/*: `npm install`
3. Start the API from *api/app/*: `fastapi run main.py`
4. Start the NextJS app from *frontend/*: `npm run dev (no prod yet!)`

Be sure to correctly configure these files with your routes:

### - api/.env:

- For SQL:

```
SQL_ENGINE = yourSQLhost
DB = dbname
USER = youruser
PASSWORD = if required, using win auth here 
```

- For Firestore:

```
FIRESTORE_PROJECT_ID=yourfirestoreprojectid
FIRESTORE_CREDENTIALS=yourcredentials
```
- Routes:

```
API_BASE_URL = yoururl <- localhost if running locally
API_PORT = yourport <- 8000
```

### - frontend/src/app/config.js:

```
API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "yoururl:port"; <- localhost if running locally
N8N_BASE_URL = process.env.NEXT_PUBLIC_N8N_BASE_URL || "yoururl:port"; <- 3000
```
