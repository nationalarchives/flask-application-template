# TNA Python Flask Application

## Quickstart

```sh
# Build and start the container
docker compose up -d

# Run tests
docker compose exec app poetry run python -m pytest

# Format and lint code
docker compose exec app format
```

## Environment variables

In addition to the [base Docker image variables](https://github.com/nationalarchives/docker/blob/main/docker/tna-python/README.md#environment-variables), this application has support for:

| Variable                 | Purpose                                                   | Default             |
| ------------------------ | --------------------------------------------------------- | ------------------- |
| `CONFIG`                 | The configuration to use                                  | `config.Production` |
| `DEBUG`                  | If true, allow debugging[^1]                              | `False`             |
| `PROXY_DEPTH`            | The depth of the proxy in front of the application[^2]    | `0`                 |
| `COOKIE_DOMAIN`          | The domain to save cookie preferences against             | _none_              |
| `COOKIE_PREFERENCES_URL` | The URL for changing cookie preferences                   | _none_              |
| `CSP_IMG_SRC`            | A comma separated list of CSP rules for `img-src`         | `'self'`            |
| `CSP_SCRIPT_SRC`         | A comma separated list of CSP rules for `script-src`      | `'self'`            |
| `CSP_STYLE_SRC`          | A comma separated list of CSP rules for `style-src`       | `'self'`            |
| `CSP_FONT_SRC`           | A comma separated list of CSP rules for `font-src`        | `'self'`            |
| `CSP_CONNECT_SRC`        | A comma separated list of CSP rules for `connect-src`     | `'self'`            |
| `CSP_MEDIA_SRC`          | A comma separated list of CSP rules for `media-src`       | `'self'`            |
| `CSP_WORKER_SRC`         | A comma separated list of CSP rules for `worker-src`      | `'self'`            |
| `CSP_FRAME_SRC`          | A comma separated list of CSP rules for `frame-src`       | `'self'`            |
| `CSP_FRAME_ANCESTORS`    | A comma separated list of CSP rules for `frame-accestors` | `'self'`            |
| `CSP_REPORT_URI`         | The URL to report CSP violations to                       | _none_              |
| `FORCE_HTTPS`            | Redirect requests to HTTPS as part of the CSP             | _none_              |
| `GA4_ID`                 | The Google Analytics 4 ID                                 | _none_              |

[^1] [Debugging in Flask](https://flask.palletsprojects.com/en/2.3.x/debugging/)
[^2] [ProxyFix middleware](https://flask.palletsprojects.com/en/stable/deploying/proxy_fix/) - **Ensure all proxy headers are correctly set in the proxy**
