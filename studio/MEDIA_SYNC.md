# Media storage and SSH sync

Generated video and audio live on the local machine and an SSH host, outside Git.
Git keeps scripts, asset manifests, credits, generation metrics and review records.
The video index links local files; GitHub does not host those binaries.

Install `rsync` and OpenSSH locally, and `rsync` and Python 3.9+ on the server.
Configure authentication, host keys and optional ports in your SSH config first
(for example, test `ssh hetzner`). From any directory, run the script from your
checkout; its local repository root is determined from the script's location.

```sh
# Upload; defaults to /root/finland-flashcards on the SSH host.
poetry run python studio/tools/sync_media.py --host hetzner

# Restore media into a fresh clone or recover a missing local copy.
poetry run python studio/tools/sync_media.py --host hetzner --pull

# Any SSH alias or user@host and any absolute destination directory.
poetry run python studio/tools/sync_media.py --host user@example.com \
  --remote-dir /srv/finland-flashcards

# Inspect changes or verify both copies without modifying the destination.
poetry run python studio/tools/sync_media.py --host hetzner --dry-run
poetry run python studio/tools/sync_media.py --host hetzner --verify-only
```

`--pull` also supports `--dry-run` and `--verify-only`. Use an SSH config alias
for an IPv6 address or a nonstandard port. Authentication is noninteractive.

The script transfers only canonical `videos/homebrew/*.mp4`, language `.m4a`
audio sidecars, and selected narration WAVs named by
`studio/media/hb-c*/narration*/metrics.json`, including retained raw Russian takes.
Credits, metrics, scripts and other metadata belong to Git and are never uploaded
or restored by this script. Selection uses explicit media paths, without querying
Git or checking ignore rules. Render records and credits identify expected exports;
missing exports or selected takes fail before upload. Downloads, models, images,
music caches, render scratch and discarded auditions are excluded. The transfer
preserves repository-relative paths. A destination does not need a Git checkout.

Every selected file is checked with SHA-256. After success, each side gets an
ignored `.media-sync.json` receipt. A restore uses the server's last successful
receipt and verifies its source files before copying. Files outside that receipt
are not restored. The receipt also prevents a later upload silently omitting
previously synced files. For an intentional inventory reduction, review the
omissions and remove the local receipt before uploading; receiver-only files
still remain. Do not edit receipts to bypass checksum failures.

New receipts use version 2 and contain only binaries. Version 1 receipts remain
readable: their known credits/metrics entries are discarded in memory, while all
binary entries and checksums are retained. The next successful sync writes a
version 2 receipt. Metadata already copied by older versions is left untouched;
sync never cleans up or overwrites those files. A standalone media storage copy
contains binaries and the sync receipt; obtain its matching metadata through Git.

Both directions replace same-path files from the source but **never delete
receiver-only files**. They use rsync temporary files and retained partial data;
rerun the same command after an interrupted transfer. A failed transfer does not
publish a success receipt, and a failed checksum check exits nonzero. Sync is not
a versioned backup: replacing a file on both machines replaces both copies.
Run one sync at a time, with generation/editing paused for the selected files.

On a fresh checkout, pull media before building the study Docker image. The
Docker build still includes local exports and packages alternate audio normally.
Sync does not build, restart, deploy, or change `.env` or application databases.
To upload assets and deploy the local Git commit in one command, use
`poetry run python deploy_over_ssh.py --host hetzner`; see
[deployment instructions](../study/README.md#deploy-over-ssh).
The default `/root/finland-flashcards` storage copy is distinct from the existing
`/opt/finland-flashcards` deployment described in [study/README.md](../study/README.md).

After the one-time history migration, existing clones must adopt the rewritten
history or be replaced with fresh clones; merging old branches can reintroduce
media history. Restore local media with `--pull` after cloning. Historical media
hashes in production records remain provenance, even when the corresponding old
binary versions are no longer stored.
