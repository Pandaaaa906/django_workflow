from distutils.core import setup

setup(
    name='django_workflow',
    version='0.1',
    packages=['example_app', 'example_app.migrations', 'workflow', 'workflow.models', 'workflow.contrib',
              'workflow.migrations', 'django_workflow_test'],
    url='https://github.com/Pandaaaa906/django_workflow/',
    license='',
    author='panda.ye',
    author_email='ye.pandaaaa906@gmail.com',
    description='', requires=['django']
)
