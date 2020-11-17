DESCRIPTION="""
Fetches latest USD to MXN exchange rate information from [Diario Oficial de la Federación](https://www.banxico.org.mx/tipcamb/tipCamMIAction.do), [Fixer](https://fixer.io/), and [Banxico](https://www.banxico.org.mx/SieAPIRest/service/v1/doc/consultaDatosSerieOp). For more information visit the [github repository](https://github.com/jrlangford/xr-fetcher) for this project.

## Features
- Single endpoint to fetch data from multiple sources
- Status reporting per data source
- Application based access integrated through oauth2
- Application based rate limiting
- Live, interactive, documentation

## Usage
In order to get started we will go through the necessary steps to make this browsable API interactive.

**Register a new app**
- Visit the app registration url **https://xr-fetcher.jrlprojects.com/o/applications** in a different tab in your browser and log in with your admin credentials
- Click the button to create a new application
- Give your app a unique name, we may call this one **Swagger UI**
- Select Client Type: **Public**, indicating our frontend can be inspected by clients
- Select Authorization grant type: **Client credentials**, indicating the type of flow we will use to handle authorization
- Add a dummy Redirect Uri such as the following: **https://xr-fetcher.jrlprojects.com/doesnotexist**
- Click **Save** and keep note of the **Client ID** and **Client Secret** that were generated.

**Authenticate with your app credentials**
- Click the **Authorize** button on the bottom right of this instructions section
- Paste the **CLient ID** and **Client Secret**
- Select the **Read scope**
- **Authorize** your app

This step generated a token that is automatically available in this browser tab to perform requests.

Now go to the interactive section and test the main endpoint.
"""
