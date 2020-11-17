# xr_fetcher

Fetches latest USD to MXN exchange rate information from [Diario Oficial de la Federación](https://www.banxico.org.mx/tipcamb/tipCamMIAction.do), [Fixer](https://fixer.io/), and [Banxico](https://www.banxico.org.mx/SieAPIRest/service/v1/doc/consultaDatosSerieOp).

## Features
- Single endpoint to fetch data from multiple sources
- Status reporting per data source
- Application based access integrated through oauth2
- Application based rate limiting
- Live, interactive, documentation

## Prerequirements
- Docker ^19.03
- Python ^3.9 (Optional)

## Quickstart

## Docker setup
```
```

## Host setup
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.
./manage.py migrate
./manage.py createsuperuser
```
