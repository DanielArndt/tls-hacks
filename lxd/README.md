# LXD Dev Env Setup

## Mount dir into VM

```bash
lxc config device add dev canonical disk source=/home/darndt/git/canonical/ path=/root/canonical
lxc config device add dev vm-share disk source=/home/darndt/git/canonical/tls/tls-hacks/multipass/vm-share path=/root/vm-share
```

## Map the IDs of both user and group to root

```bash
lxc config set dev raw.idmap "both 1000 0"
```


```bash
mount --bind -o ro vm-share/home/.zshrc .zshrc
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
git clone https://github.com/zsh-users/zsh-autosuggestions.git ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting

wget -P ~/.oh-my-zsh/themes/ https://raw.githubusercontent.com/Abuelodelanada/charm-dev-utils/main/zsh_themes/juju.zsh-theme

snap install juju
snap install lxd
snap install microk8s --channel 1.31-strict/stable
snap install vault
```

Bootstrap Juju

```bash
microk8s.enable hostpath-storage
juju bootstrap lxd lxd
juju bootstrap microk8s k8s
```

```bash
apt install pipx
pipx install tox
pipx inject tox tox-uv
pipx install pipenv
pipx install pipenv-shebang
```

```bash
curl https://pyenv.run | bash
sudo apt update
sudo apt install build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev curl git \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

```bash
curl -sS https://webinstall.dev/k9s | bash
mkdir -p $HOME/.kube
microk8s config > $HOME/.kube/config
```

```bash
echo "net.ipv6.conf.all.disable_ipv6=1" | tee -a /etc/sysctl.conf
echo "net.ipv6.conf.default.disable_ipv6=1" | tee -a /etc/sysctl.conf
echo "net.ipv6.conf.lo.disable_ipv6=1" | tee -a /etc/sysctl.conf
```
