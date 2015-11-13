# Installation

## System dependencies

On Ubuntu 14.04 :

  python 3.4
  libx11-dev

## Local setup

On Ubuntu 14.04

1. Install the latest docker

  To install the latest docker-engine, follow the steps documented on the docker website:

  https://docs.docker.com/installation/ubuntulinux/

2. Add your user to the docker group

  ```
  $ sudo usermod -a -G docker $USER
  ```

3. Install docker-compose

  ```
  # curl -L https://github.com/docker/compose/releases/download/1.5.0rc2/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
  # chmod +x /usr/local/bin/docker-compose
  ```

  Ref: https://docs.docker.com/compose/install/

4. Clone the git repository

  <pre>
  $ git clone https://github.com/erudit/zenon
  </pre>

5. Create a 'settings_env.py' file

  The settings_env.py file overrides the general settings with environment specific settings.The settings.py contains all the required settings to setup a local environment.

  <pre>
  $ touch erudit/erudit/settings_env.py
  </pre>

6. Build the images

  At this point, you have everything necessary to build

  ```
  $ docker-compose up
  ```

7. Apply the migrations

  ```
  $ docker-compose run python erudit/manage.py migrate auth
  $ docker-compose run python erudit/manage.py migrate
  ```

8. Create a superuser

  ```
  $ docker-compose run python erudit/manage.py createsuperuser
  ```

# Deploying updates

```
$ ansible-playbook playbook.yml -i hosts -t update -l local --ask-vault-pass
```

Where `local` is the the target environment.

# Running the tests

You can run the tests with:

```
$ tox
```
