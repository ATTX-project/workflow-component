from wf_api.app import create
import click
import multiprocessing
import gunicorn.app.base
from gunicorn.six import iteritems


@click.command()
@click.option('--host', default='127.0.0.1', help='host wfAPI host.')
@click.option('--port', default=4301, help='wfAPI server port.')
@click.option('--workers', default=2, help='wfAPI server workers.')
@click.option('--log', default='logs/server.log', help='log file for app.')
def cli(host, port, log, workers):
    """Run the server with options."""
    options = {
        'bind': '{0}:{1}'.format(host, port),
        'workers': workers,
        'daemon': 'True',
        'errorlog': log
    }
    WFApplication(create(), options).run()


class WFApplication(gunicorn.app.base.BaseApplication):
    """Create Standalone Application WF-API."""

    def __init__(self, app, options=None):
        """The init."""
        self.options = options or {}
        self.application = app
        super(WFApplication, self).__init__()

    def load_config(self):
        """Load configuration."""
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        """Load configuration."""
        return self.application


# Unless really needed to scale use this function. Otherwise 2 workers suffice.
def number_of_workers():
    """Establish the numberb or workers based on cpu_count."""
    return (multiprocessing.cpu_count() * 2) + 1


def main():
    """Main function."""
    cli()


if __name__ == '__main__':
    main()
