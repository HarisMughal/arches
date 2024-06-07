import json
import os
import site
import sys
from contextlib import contextmanager

import django
from django.apps import apps, AppConfig
from django.conf import global_settings, settings


@contextmanager
def move_to_end_of_sys_path(*paths):
    _orig_sys_path = sys.path[:]
    for path in paths:
        if path in sys.path:
            sys.path.remove(path)
            sys.path.append(path)
    try:
        yield
    finally:
        sys.path = _orig_sys_path


def arches_applications():
    from arches import settings as core_settings

    return [
        mod.name for mod in arches_applications_modules(core_settings.INSTALLED_APPS)
    ]


def arches_applications_modules(installed_apps):
    from arches import settings as core_settings

    arches_applications_modules = []

    for app in installed_apps or []:
        if app in core_settings.INSTALLED_APPS:
            continue
        try:
            config = AppConfig.create(app)
        except ImportError:
            # Something not pip-installed (the project) might not be importable yet.
            continue
        if getattr(config, "is_arches_application", False):
            arches_applications_modules.append(config.module)
            break

    return arches_applications_modules


def build_staticfiles_dirs(
    root_dir, app_root=None, installed_apps=None, additional_directories=None
):
    """
    Builds the STATICFILES_DIRS tuple with respect to ordering projects,
    packages, additional directories.

    Arguments

    root_dir -- string, os-safe absolute path to arches-core root directory
    app_root -- string, os-safe absolute path to application directory
    installed_apps -- from django settings, to check for arches applications
    additional_directories -- list of os-safe absolute paths
    """
    directories = []

    if additional_directories:
        for additional_directory in additional_directories:
            directories.append(additional_directory)

    if app_root:
        directories.append(os.path.join(app_root, "media", "build"))
        directories.append(os.path.join(app_root, "media"))
        directories.append(
            ("node_modules", os.path.join(app_root, "..", "node_modules"))
        )

    for module in arches_applications_modules(installed_apps):
        directories.append(os.path.join(module.__path__[0], "media"))

    directories.append(os.path.join(root_dir, "app", "media", "build"))
    directories.append(os.path.join(root_dir, "app", "media"))
    directories.append(("node_modules", os.path.join(root_dir, "..", "node_modules")))

    return tuple(directories)


def build_templates_config(
    root_dir,
    debug,
    app_root=None,
    installed_apps=None,
    additional_directories=None,
    context_processors=None,
):
    """
    Builds a template config dictionary

    Arguments

    root_dir -- string, os-safe absolute path to arches-core root directory
    debug -- boolean representing the DEBUG value derived from settings
    app_root -- string, os-safe absolute path to application directory
    installed_apps -- from django settings, to check for arches applications
    additional_directories -- list of os-safe absolute paths
    context_processors -- list of strings representing desired context processors
    """
    directories = []

    if additional_directories:
        for additional_directory in additional_directories:
            directories.append(additional_directory)

    if app_root:
        directories.append(os.path.join(app_root, "templates"))

    for module in arches_applications_modules(installed_apps):
        directories.append(os.path.join(module.__path__[0], "templates"))

    directories.append(os.path.join(root_dir, "app", "templates"))

    return [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": directories,
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": (
                    context_processors
                    if context_processors
                    else [
                        "django.contrib.auth.context_processors.auth",
                        "django.template.context_processors.debug",
                        "django.template.context_processors.i18n",
                        "django.template.context_processors.media",
                        "django.template.context_processors.static",
                        "django.template.context_processors.tz",
                        "django.template.context_processors.request",
                        "django.contrib.messages.context_processors.messages",
                        "arches.app.utils.context_processors.livereload",
                        "arches.app.utils.context_processors.map_info",
                        "arches.app.utils.context_processors.app_settings",
                    ]
                ),
                "debug": debug,
            },
        },
    ]


def transmit_webpack_django_config(**kwargs):
    is_core = kwargs["APP_NAME"] == "Arches"
    our_settings = {k: v for k, v in kwargs.items() if k.isupper()}

    # We're currently executing APP_NAME's settings.py,
    # we don't need to try to install it, too.
    if not is_core:
        our_settings["INSTALLED_APPS"] = list(our_settings["INSTALLED_APPS"])
        our_settings["INSTALLED_APPS"].remove(kwargs["APP_NAME"])
    settings.configure(default_settings=global_settings, **our_settings)

    # Without this `import celery` might resolve to arches.celery or project.celery
    if is_core:
        with move_to_end_of_sys_path(os.path.realpath(kwargs["ROOT_DIR"])):
            django.setup()
    else:
        with move_to_end_of_sys_path(os.path.realpath(kwargs["APP_ROOT"])):
            django.setup()

    arches_applications_paths = {
        config.name: config.module.__path__[0]
        for config in apps.get_app_configs()
        if getattr(config, "is_arches_application", False)
    }

    sys.stdout.write(
        json.dumps(
            {
                "APP_ROOT": os.path.realpath(kwargs["APP_ROOT"]),
                "ARCHES_APPLICATIONS": list(arches_applications_paths),
                "ARCHES_APPLICATIONS_PATHS": arches_applications_paths,
                "SITE_PACKAGES_DIRECTORY": site.getsitepackages()[0],
                "PUBLIC_SERVER_ADDRESS": kwargs["PUBLIC_SERVER_ADDRESS"],
                "ROOT_DIR": os.path.realpath(kwargs["ROOT_DIR"]),
                "STATIC_URL": kwargs["STATIC_URL"],
                "WEBPACK_DEVELOPMENT_SERVER_PORT": kwargs[
                    "WEBPACK_DEVELOPMENT_SERVER_PORT"
                ],
            }
        )
    )
    sys.stdout.flush()
