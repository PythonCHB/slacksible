# Slacksible
Slack bot for Ansible remote execution with support for Ara run reporting.


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Below is what is recommended to have installed on your system prior to installation of this application.

```
* virtualenv
* pyenv
* Python 3.5.1
* Slack bot provisioned from a slack channel you own
* ARA database to interface
```
It is recommended that you use pyenv and virtualenv to setup a new environment for this applications packages to be installed in. This application was developed on the python version specified above.

### Installing

Inside your working directory of your virtualenv clone this repo:

```
git clone git@github.com:jmhthethird/slacksible.git
```

Install requirements.txt:

```
pip install -r requirements.txt
```

Rename sample.config.yml to config.yml:

```
mv configuration/sample.config.yml configuration/config.yml
```

Update config.yml to meet your needs:

```
Update log_dir to be the path to your logs
Update ara_db to be the path to your ara sqlite db provisioned
Update SLACKSIBLE_TOKEN to be the slack bot token you have provisioned.
Update bot_name to be the name of the slack bot you have provisioned.
```

At this point we should be ready to launch our app!

```
python3 bin/slacksible.py
```

If all goes well you should see the bot appear online in your slack channel and on the console you should see the input parameters specified to the bot in your config file!

```
$ python bin/slacksible.py
args: ()
kwargs:  {'log_dir': '/path/to/log/dir/',
 'ara_db': '~/.ara/ansible.sqlite',
 'bot_name': 'ansible_slack_bot',
 'verbose': False,
 'stderr_log': <logging.Logger object at 0x101be0748>,
 'SLACKSIBLE_TOKEN': '<token goes here>',
 'debug_log': <logging.Logger object at 0x101be0588>,
 'usage_log': <logging.Logger object at 0x101be0a20>,
 'log_dir_enable': False}
```


## Deployment

This system has not been tested for full production deployment.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/jmhthethird/slacksible/tags).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
