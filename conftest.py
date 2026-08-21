# Empty on purpose: pytest uses a conftest.py's location to decide what
# goes on sys.path, so having one here (rather than only under tests/)
# is what makes "from sizedur import ..." resolve without an install step.
