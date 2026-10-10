"""Where things live. Every calibration tool imports this module first.

  REPO     the repository root, which is the skill itself (SKILL.md, scripts/, references/)
  SCRIPTS  the skill's scripts, put on sys.path so that the tools measure with the shipped code
  DATA     scripts/data, where the calibration, the marker words and the lexicons are written
  WS       the working directory for corpora, text sets and measurements: calibration/workspace
           (ignored by git) unless SCIHUMANIZER_WORKSPACE names another directory
"""
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TOOLS))
SCRIPTS = os.path.join(REPO, "scripts")
DATA = os.path.join(SCRIPTS, "data")
WS = os.path.abspath(os.environ.get("SCIHUMANIZER_WORKSPACE") or os.path.join(REPO, "calibration", "workspace"))

if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)


def contact():
    """Address sent in the User-Agent of the fetch tools, so that a site can reach whoever runs them."""
    who = os.environ.get("SCIHUMANIZER_CONTACT", "").strip()
    if not who:
        sys.exit("Set SCIHUMANIZER_CONTACT to an e-mail address or a URL before fetching: the sources ask\n"
                 "automated clients to say who they are.")
    return who
