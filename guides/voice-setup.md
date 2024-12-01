## Run the following commands:

---

```bash
sudo apt-get install python3 python3-pip python3-venv libsndfile1
sudo apt-get update
sudo apt-get install festival festvox-don festlex-cmu festvox-us-slt-hts
```

> Custom Voice Manual Installation
```bash
cd ~
```

```bash
wget http://www.festvox.org/packed/festival/2.5/voices/festvox_cmu_us_slt_arctic_hts.tar.gz
```

```bash
sudo tar -xvzf festvox_cmu_us_slt_arctic_hts.tar.gz -C /usr/share/festival/voices/english/
```

```bash
ls /usr/share/festival/voices/english/
```