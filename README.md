# goal-bot

A Twitter bot that posts highlights when goals are scored in the NHL.

See the bot in action: [@nhl_goal_bot](https://twitter.com/nhl_goal_bot)

## How to run unit tests

```shell
> make test
```

## How to get test coverage report

```shell
> make coverage
```

## How to lint source files

```shell
> make lint
```

## How to perform static analysis

```shell
> make analyze
```

## How to build the docker container

```shell
> make build
```

## How to deploy the docker container

```shell
> make deploy
```

Production deploys happen automatically: pushing to `main` runs the GitHub
Actions pipeline, which zips the repository and deploys it to Elastic Beanstalk.
Elastic Beanstalk builds the image on the instance using `docker-compose.yml`.
Credentials (`BEARER_TOKEN`, `CONSUMER_KEY`, `CONSUMER_SECRET`, `ACCESS_TOKEN`,
`ACCESS_TOKEN_SECRET`, `HANDLE`, `PASSWORD`) are set as environment properties
in the Elastic Beanstalk console; `config/` is excluded from the image.

The compose file enables the health watchdog, which exits the process if the
command queue stops responding, and `restart: unless-stopped` brings it back up.
