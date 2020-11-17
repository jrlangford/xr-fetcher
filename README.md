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

## Usage

### Quickstart
- Copy .quick.env and set your **FIXER_API_ACCESS_KEY**(<https://fixer.io/>) and **BANXICO_TOKEN**(<https://www.banxico.org.mx/SieAPIRest/service/v1/>) in the new file
- Run the helper script passing your new file as an argument `./launch_container.sh <env>`

The helper script builds the docker image, launches it, and creates user **admin** with password **adminpass** for testing purposes. This setup is not suitable for public deployment.

### Env files
Most variables are self explanatory and have a direct mapping to Django variables, those that don't are listed below.

**ALLOWED_HOSTS**- String, required: A comma separated list of patterns that match allowed hosts  
**DBENGINE**- String, required: Either django.db.backends.postgresql or django.db.backends.sqlite3  
**FIXER_API_ACCESS_KEY**- String, required: Your API Key from <https://fixer.io/>, requires a key with permission to set [base currency](https://fixer.io/documentation)  
**BANXICO_TOKEN**- String, required: Your API Token from <https://www.banxico.org.mx/SieAPIRest/service/v1/>  

Please note that most variables in the env files should not contain double quotes to allow docker to read them properly.

### Docker setup
**Build the image**  
```
docker build -t xr_fetcher:latest .
```

**Run the image**  

Generate a custom env file from `.example.env`.  

Run the docker image
```
docker run -d --env-file <your-env-file> -p 8000:8000 --name xr_fetcher xr_fetcher:latest
```
You may need to customize the previous commands to adjust them to your particular setup.

**Run migrations**  

The docker image is configured to run python on a virtual environment, remember to load the environment before running django specific commands.

Start a shell in the container
```
docker run -it xr_fetcher /bin/sh
```
The shell will start in the container's working directory, which contains the project's files.

Load the environment
```
source .venv/bin/activate
```

Apply migrations
```
./manage.py migrate
```

**Create superuser**
```
./manage.py createsuperuser
```

Now you are ready to start using the service.

### API documentation
Please visit the interactive documentation at <https://xr-fetcher.jrlprojects.com/>



