# IAM REST API

Et sikkert REST API bygget med FastAPI, som viser de to delene av identitets- og tilgangsstyring: **autentisering** (å bevise hvem du er med JWT) og **autorisasjon** (å styre hva du har lov til med rollebasert tilgangskontroll).

## Hva det gjør

- Brukere logger inn med brukernavn og passord og får et signert **JWT-tilgangstoken**
- Passord lagres aldri i klartekst, de hashes med **bcrypt**
- Alle beskyttede endepunkter krever et gyldig token som ikke har utløpt
- Endepunktene håndhever **minste privilegium** gjennom roller: en vanlig `user` slipper ikke inn på ruter som bare er for `admin`
- Tokenene er tidsbegrenset og signaturen verifiseres, så et token som er tuklet med eller har utløpt, blir avvist

## Endepunkter

| Metode | Sti | Tilgang | Beskrivelse |
|--------|------|--------|-------------|
| `POST` | `/auth/register` | Åpen | Opprett en ny konto |
| `POST` | `/auth/login` | Åpen | Bytt brukernavn og passord mot et JWT |
| `GET`  | `/users/me` | Alle innloggede brukere | Les din egen profil |
| `GET`  | `/users` | Bare admin | List opp alle kontoer |
| `DELETE` | `/users/{username}` | Bare admin | Slett en konto (ikke din egen) |
| `GET`  | `/` | Åpen | Helsesjekk |

## Slik fungerer tilgangskontrollen

To FastAPI-avhengigheter gjør jobben:

- **`get_current_user`** dekoder bearer-tokenet, verifiserer signatur og utløpstid, og henter brukeren det gjelder. Dette er *autentiserings*porten: uten gyldig token, ingen adgang.
- **`require_role(Role.admin)`** bygger videre på dette og sjekker rollen som ligger i tokenet. Dette er *autorisasjons*porten: den returnerer **403 Forbidden** når en innlogget bruker mangler riktig rolle.

Rollen ligger inne i det signerte tokenet, så klienten kan ikke endre den uten å ødelegge signaturen.

## Prosjektstruktur

```
app/
  config.py          # innstillinger (hemmelig nøkkel, levetid for token)
  models.py          # Pydantic-skjemaer og Role-enumen
  auth.py            # hashing av passord + opprett/dekod JWT
  database.py        # brukerlager i minnet (kan byttes ut med en ekte database)
  security.py        # avhengighetene get_current_user + require_role
  routers/
    auth_router.py   # /auth/register, /auth/login
    users_router.py  # /users/me, /users, /users/{username}
  main.py            # startpunkt for appen
tests/
  test_api.py        # 10 tester som dekker autentisering + RBAC
```

## Kjøre det

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Åpne deretter `http://127.0.0.1:8000/docs` for det interaktive Swagger-grensesnittet.

### Ferdige kontoer

| Brukernavn | Passord | Rolle |
|----------|----------|------|
| `admin` | `admin12345` | admin |
| `alice` | `alice12345` | user |

### Prøv raskt

```bash
# Logg inn og hent et token
curl -X POST http://127.0.0.1:8000/auth/login \
  -d "username=admin&password=admin12345"

# Bruk tokenet på et endepunkt som bare er for admin
curl http://127.0.0.1:8000/users \
  -H "Authorization: Bearer <lim-inn-token-her>"
```

## Tester

```bash
pytest -q
```

Dekker vellykket innlogging, feil passord, manglende token, token som er tuklet med, at en vanlig bruker blir stoppet fra admin-ruter (403), admin-tilgang, registrering, dupliserte brukernavn og regler for sletting.

## Sikkerhetsmerknader

- `SECRET_KEY` har en plassholderverdi for lokal bruk. I produksjon må den komme fra en miljøvariabel eller et hemmelighetshvelv (for eksempel Azure Key Vault), og aldri sjekkes inn i kildekoden.
- Brukerlageret i minnet og de ferdige kontoene er for demonstrasjon. En ekte løsning ville brukt en database og ikke hatt standardpassord.
- Innloggingen gir samme generelle feilmelding for feil brukernavn og feil passord, slik at den ikke avslører om en konto finnes (brukeropptelling).

## Teknologi

Python · FastAPI · PyJWT · passlib/bcrypt · pytest
