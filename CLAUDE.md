The [MET Office API](https://datahub.metoffice.gov.uk/) works like so:

    curl -X GET "https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/hourly?latitude=51.55138&longitude=-2.55933"  -H "accept: application/json" -H "apikey: $MET_OFFICE_API_KEY"

Run `actionlint` to check the Github action workflow.
