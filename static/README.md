# static
This folder contains the static assets used by the backend. Usually this folder will stay empty. But, for good purposes it exists and if at some time static assts need to be added, they can be added in src and be compiled into dist.

## src
This folder contains the raw files, for example .scss files.

## dist
This folder contains the compiled files, for example .css files or images. 

This folder is also the folder that will be copied to tmp/static/ when python manage.py collectstatic is run.

## production
If any files in dist were changed while developing you need to run python manage.py collectstatic in order to copy the changed files. 

And you need to push the tmp/static/ folder to production.
