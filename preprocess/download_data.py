import os, subprocess, json
import pandas as pd
import argparse

_BASE_URL = "https://reazonspeech.s3.abci.ai/"
_AUDIO_V2 = "v2/{:03x}.tar"

_DATASETS = {
    "tiny":      {"tsv": 'v2-tsv/tiny.tsv',   "audio": _AUDIO_V2, "nfiles": 1},
    "small":     {"tsv": 'v2-tsv/small.tsv',  "audio": _AUDIO_V2, "nfiles": 12},
    "medium":    {"tsv": 'v2-tsv/medium.tsv', "audio": _AUDIO_V2, "nfiles": 116},
    "large":     {"tsv": 'v2-tsv/large.tsv',  "audio": _AUDIO_V2, "nfiles": 579},
    "all":       {"tsv": 'v2-tsv/all.tsv',    "audio": _AUDIO_V2, "nfiles": 4096},
}

def download_tsv(split, base_dir):
    command = f"wget {_BASE_URL}{_DATASETS[split]['tsv']} -P {base_dir}"
    subprocess.run(command, shell=True)
    file_path = os.path.join(base_dir, f"{split}.tsv")
    return file_path

def download_audio(split, base_dir):
    n_files = _DATASETS[split]["nfiles"]
    tar_dir = os.path.join(base_dir, "tar")
    flac_dir = os.path.join(base_dir, "flac")
    for i in range(n_files):
        # Download tar files to {base_dir}/tar/
        command = f"wget {_BASE_URL}{_DATASETS[split]['audio'].format(i)} -P {tar_dir}"
        subprocess.run(command, shell=True)
        
        # Extract tar files to {base_dir}/flac/
        if not os.path.exists(flac_dir):
            os.mkdir(os.path.join(flac_dir))
        command = f"tar xf {tar_dir}/{i:03x}.tar -C {flac_dir}"
        print(f"Extracting {i:03x}.tar...", end="\r", flush=True)
        subprocess.run(command, shell=True)
    
def flac2wav(base_dir):
    flac_dir = os.path.join(base_dir, "flac")
    wav_dir = os.path.join(base_dir, "wav")
    
    assert os.path.exists(flac_dir), f"{flac_dir} does not exist"
    
    if not os.path.exists(wav_dir):
        os.mkdir(wav_dir)
    
    for folder in os.listdir(flac_dir):
        if not os.path.exists(os.path.join(wav_dir, folder)):
            os.mkdir(os.path.join(wav_dir, folder))
        
        files = os.listdir(os.path.join(flac_dir, folder))
        num_files = len(files)
        for i, flac_file in enumerate(files):
            flac_name = os.path.join(flac_dir, folder, flac_file)
            wav_name = os.path.join(wav_dir, folder, flac_file.replace(".flac", ".wav"))
            command = f"ffmpeg -hide_banner -loglevel error -y -i {flac_name} {wav_name}"
            subprocess.run(command, shell=True)
            print(f"Processing {i+1}/{num_files} files in {folder}...", end="\r", flush=True)
        print(f"Finished processing {folder}")

def update_tsv(split, base_dir):
    file_path = os.path.join(base_dir, f"{split}.tsv")
    df = pd.read_csv(file_path, sep="\t", header=None, names=["path", "text"])
    df["path"] = os.path.join("wav",df["path"].str.replace(".flac", ".wav"))
    df.to_csv(file_path, sep="\t", header=False, index=False)

def main(split, base_dir, no_download, no_conversion):
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    if not no_download:
        download_tsv(split, base_dir)
        download_audio(split, base_dir)
    if not no_conversion:
        flac2wav(base_dir)
        update_tsv(split, base_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", type=str, default="tiny")
    parser.add_argument("--base_dir", type=str, default="../datasets")
    parser.add_argument("--no_download", action="store_true", default=False)
    parser.add_argument("--no_conversion", action="store_true", default=False)
    args = parser.parse_args()
    main(**vars(args))