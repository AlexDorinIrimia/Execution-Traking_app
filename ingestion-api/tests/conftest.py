import sys
import os

# When pytest is run from ingestion-api/, Python does not automatically find
# the app/ package because it sits in a subdirectory.
# This conftest.py adds ingestion-api/ to sys.path so that
# `import app.app` and `import app.db` resolve correctly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
