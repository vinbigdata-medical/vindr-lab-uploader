<img src="./LogoVinDrLab.png" width="256"/>

# VinDr Lab / DICOM Uploader

DICOM Uploader is a part of the VinDr Lab project. Like Robin alongside with Batman (main API), it modifies and transfers the DICOM (an image saved in the Digital Imaging and Communications in Medicine format) files to database.

## What does this project do?

As metioned above, this collaborates with the API, helps you to upload the DICOM files, configures them with some additional information. You can ask us that: Why do we need another side-kick service that performs the same as an API? To be clear, Golang now has some limitations on working with DICOM file, on the other hand, Pythonb has dark-and-mysterious tools which can do these things for us.

## Project tree

```
.
├── config/ // configuration files and permission definitions
├── connection/ // connector to orther services
├── dbal/ // access layer to database
├── middleware/ // authentication for incoming request
├── restapi/ // main process part
├── tests // test files
├── app.py // you can make app run from here
├── docker-compose.yml
├── Dockerfile
├── README.md
└── utils/ // utilities for project
```

## Installation

**Option 1: Kubernetes**

Go to deployment project and follow the instruction

**Option 2: Docker**

You can execute the <code>docker-compose.yml</code> file as follow:

```bash
docker-compose down
docker-compose up -d --remove-orphans
```

**Option 3: Bare handed**

Just run the <code>run.sh</code> file

## Configuration

Following the Installation, the application has two ways to absorb its configurations. Once is from the <code>config.production.toml</code> file that comes with the app. Or you can override it by passing through environment variables in Docker.
As you can see, the configuration file has the following form:

```
[development]
ORTHANC_API_URI = "YOUR_ORTHANC_URI"
REDIS_URI = "YOUR_REDIS_URI"
REDIS_CACHE_TIME = 10
ES_STUDIES_INDEX_PREFIX = "YOUR_STUDY_INDEX"
ES_PROJECTS_INDEX_PREFIX = "YOUR_PROJECT_INDEX"
ELASTICSEARCH_HOST = "YOUR_ES_URI"
VINDR_LAB_URI = "YOUR_API_URI"
VINDR_LAB_API_KEY = "YOUR_SECRET_API_KEY"
ID_GENERATOR_URI = "YOUR_IDGEN_URI"
```

Please note that, the conversion from environmental variables to API configuration items itself like: <code>APP_KEYCLOAK\_\_ADMIN_USERNAME</code> equals to <code>keycloak.admin_username</code> with APP is the prefix you defined

## Others

**More information**

For a fully documented explanation, please visit the official document.
