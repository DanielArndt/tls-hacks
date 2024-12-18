import json
import logging
from pathlib import Path

import sh

from .utils import run_cmd

HOME_DIR = Path.home()
FILE_DIR = Path(__file__).resolve().parent
MULTIPASS_DIR = FILE_DIR.parent
VM_SHARE_DIR = MULTIPASS_DIR / "vm-share"

ROOT_UID = 0
ROOT_GID = 0
LOCAL_USER_UID = 1000
LOCAL_USER_GID = 1000
MP_USER_UID = 1001
MP_USER_GID = 1001


class MultipassCtl:
    def __init__(self, instance_name) -> None:
        self.instance_name = instance_name

    def exists(self):
        try:
            sh.multipass.info(self.instance_name)
            return True
        except sh.ErrorReturnCode:
            return False

    def launch(self):
        mp_launch_command = f"""multipass launch \
            --cloud-init {HOME_DIR}/git/canonical/tls/tls-hacks/cloud-init/dev.yaml \
            --memory 8G \
            --cpus 4 \
            --disk 80G \
            --timeout 6000 \
            --name {self.instance_name} \
            file://{HOME_DIR}/git/canonical/tls/tls-hacks/image/output-qemu/packer-qemu
        """
        run_cmd(mp_launch_command)

    def launch_if_not_exists(self):
        if not self.exists():
            self.launch()

    def add_mounts(self):
        if not self.has_mount("/home/ubuntu/canonical"):
            self.mount(f"{HOME_DIR}/git/canonical", "/home/ubuntu/canonical")
        if not self.has_mount("/home/ubuntu/vm-share"):
            self.mount(f"{VM_SHARE_DIR}", "/home/ubuntu/vm-share")

    def mount_canonical(self):
        run_cmd(
            f"multipass mount {HOME_DIR}/git/canonical {self.instance_name}:/home/ubuntu/canonical"
        )

    def mount_vm_share(self):
        run_cmd(
            f"multipass mount {VM_SHARE_DIR} {self.instance_name}:/home/ubuntu/vm-share"
        )

    def mount(self, source, destination):
        mount_mappings = [
            # f"-u {ROOT_UID}:{ROOT_UID}",
            # f"-g {ROOT_GID}:{ROOT_GID}",
            f"-u {LOCAL_USER_UID}:{MP_USER_UID}",
            f"-g {LOCAL_USER_GID}:{MP_USER_GID}",
        ]
        run_cmd(f"multipass mount --type native {" ".join(mount_mappings)} {source} {self.instance_name}:{destination}")

    def link_files(self):
        # First, link the .zshrc file
        run_cmd(
            "multipass exec dev -- 'ln' '-fs' '/home/ubuntu/vm-share/home/.zshrc' '/home/ubuntu/.zshrc'"
        )
        # But, we'd rather have a read-only bind mount, so let's chuck that on top.
        run_cmd(
            "multipass exec dev -- sudo mount --bind -o ro /home/ubuntu/vm-share/home/.zshrc /home/ubuntu/.zshrc"
        )

    def transfer_files(self):
        run_cmd(
            f"multipass transfer {HOME_DIR}/.tmux.conf {self.instance_name}:/home/ubuntu/"
        )

    def add_ssh_key(self):
        pubkey = sh.cat(f"{HOME_DIR}/.ssh/id_ed25519.pub").rstrip()
        if not self.is_pubkey_in_authorized_keys(pubkey):
            logging.info("Pubkey not found in authorized_keys, adding it")
            run_cmd(
                f"multipass exec {self.instance_name} -- bash -c 'echo {pubkey} >> /home/ubuntu/.ssh/authorized_keys'"
            )

    def is_pubkey_in_authorized_keys(self, pubkey):
        try:
            sh.multipass.exec(
                self.instance_name,
                "--",
                "bash",
                "-c",
                f'grep "{pubkey}" /home/ubuntu/.ssh/authorized_keys',
            )
        except sh.ErrorReturnCode as e:
            return False
        return True

    def has_mount(self, destination):
        info_output = sh.multipass.info(self.instance_name, format="json")
        info = json.loads(info_output)["info"]
        mounts = info[self.instance_name]["mounts"]
        if destination in mounts:
            return True
        else:
            return False
