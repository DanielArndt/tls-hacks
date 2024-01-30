#!/usr/bin/env pipenv-shebang
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from common.multipass import MultipassCtl

HOME_DIR = Path.home()
MULTIPASS_INSTANCE_NAME = "dev"

last_checkpoint: Optional[datetime] = None
first_checkpoint: Optional[datetime] = None


def checkpoint(label=None, since_first=False) -> None:
    """Display the time passed since the last time checkpoint was called

    Args:
        label: A label to display before the checkpoint message
        since_first: If True, display the time since the first checkpoint was called
    """

    global first_checkpoint
    global last_checkpoint

    now = datetime.now()
    if not first_checkpoint:
        first_checkpoint = now
        last_checkpoint = now
        logging.info(f"Recording start at {first_checkpoint}")
        return
    if not last_checkpoint:
        last_checkpoint = now
        return
    time_diff = now - first_checkpoint if since_first else now - last_checkpoint
    if since_first:
        msg = f"Time since first checkpoint: {time_diff}"
    else:
        msg = f"Time since last checkpoint: {time_diff}"
    if label:
        logging.info("%s: %s", label, msg)
    else:
        logging.info(msg)
    last_checkpoint = now


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
    )
    checkpoint()
    multipass_instance = MultipassCtl(MULTIPASS_INSTANCE_NAME)
    if not multipass_instance.exists():
        multipass_instance.launch()
        checkpoint("multipass instance launched")
    # These should all be idempotent, so no problem running them again and again.
    multipass_instance.add_mounts()
    multipass_instance.transfer_files()
    multipass_instance.link_files()
    multipass_instance.add_ssh_key()
    checkpoint("finished", since_first=True)


if __name__ == "__main__":
    main()
