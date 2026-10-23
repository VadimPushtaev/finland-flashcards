---
name: generate-homebrew-videos
description: Generate or revise requested Homebrew subchapter videos in finland-flashcards using the studio directing rules, local narration, source-backed scripts, assets, rendering, and verification. Also supports alternate Russian audio for existing videos. Use for video production, not unrelated player UI changes.
---

# Generate Homebrew videos

Produce the requested episodes through verified exports, following the repository's current studio workflow. This skill orchestrates existing tools; it does not replace the directing guide or authorize publishing, deployment, commits, or cloud synthesis.

## Locate the production context

Use the current finland-flashcards checkout; if invoked elsewhere, look in `/home/vadim/finland-flashcards`. Confirm `studio/` and `data/homebrew/manifest.yaml` exist. Read repository instructions and these live documents before production:

- `studio/DIRECTING.md`: series direction; the authority for creative requirements.
- `studio/WORKFLOW.md`: stages, review boundaries, inventory updates, revisions.
- `studio/DECISIONS.md`: settled choices versus provisional defaults.
- `studio/README.md` and `studio/episodes.yaml`: production organization and requested episode identities.

Read `studio/SCRIPTING.md` for script work, `studio/ASSETS.md` and `studio/TTS.md` for assets/narration, and `studio/RENDERING.md` for exports. Consult the episode's existing script, brief, assets, and review evidence before changing it. These live files take precedence over command examples here if tooling changes; explicit user instructions take precedence over local conventions.

Resolve requested chapter/subchapter numbers or titles through the inventory and anthology manifest to stable section IDs. Do not infer them from filenames or assume old readiness counts are current. Inspect existing exports and work in progress so a request for remaining videos does not regenerate finished ones. Keep the scope to the requested episodes and languages.

## Required parallel-agent workflow

Use parallel agents extensively for production. For a multi-episode request, the coordinator must delegate independent episodes or small episode batches to workers, keeping available agent slots occupied while useful independent work remains. Shell subprocesses alone do not satisfy this requirement. For a single episode, delegate independent asset research, script/source review, or export review where these can proceed without conflicting edits. If agent tools are unavailable or higher-priority instructions prohibit delegation, explain the limitation and continue the work that is possible.

The coordinator first resolves the requested stable IDs, checks existing work and running jobs, and establishes shared direction, chapter palette, runtime and output conventions. Start independent script planning or asset research while shared runtime setup proceeds; do not make all workers wait for unrelated setup. Reserve a coordinator slot and use the remaining permitted slots for workers. Reassign finished workers to remaining episodes instead of producing the rest serially. Workers may further delegate within available limits, but must not duplicate ownership or oversubscribe the machine.

Give each worker a concrete assignment containing:

- Exact section IDs, source/translation paths, and existing milestones to resume.
- The requirement to read this skill and the applicable live studio documents.
- Exclusive writable episode directories, media directories, episode-specific download manifests, and canonical output filenames.
- Shared palette/voice conventions, acceptance checks, resource limits, and any unresolved prerequisites.
- A handoff requirement: artifacts, durations, checks performed, source/export hashes, unresolved issues, proposed milestone changes, and whether audiovisual review actually occurred.

Workers own their assigned episodes through scripts, assets, narration, rendering and verification when dependencies permit. They must not edit another worker's files. The coordinator owns shared files such as `studio/episodes.yaml`, directing/decision documents, shared tools and lockfiles, ignore rules, and the video index. Workers report requested shared changes to the coordinator; assign a shared-tool fix to one owner at a time. Prepare shared model downloads and environment installs once, then let workers consume them read-only. Before resuming an interrupted batch, identify running processes and existing outputs so new workers do not launch duplicate synthesis or rendering jobs.

Coordinate distinct background photographs and music centrally: workers propose sources and the coordinator reserves them by source identity before production. Different crops, excerpts, or download filenames do not make the same source distinct. Preserve episode-specific creative judgment rather than cloning one scene plan across the chapter.

Parallelize reasoning, source checks, asset research and script preparation aggressively. Bound heavy TTS, ASR and encoding jobs by observed CPU, RAM and disk capacity; account for each tool's own threads. Keep other workers doing useful preparation/review while heavy-job capacity is occupied. Do not launch one unrestricted encoder or model instance per episode just because agent slots are available.

As episodes finish, have an available worker independently review another worker's source fidelity, credits, representative frames and verification evidence. Reviewers report findings without concurrently editing the producer's files; the episode owner fixes defects. The coordinator inspects handoffs, reconciles inventory/index updates, verifies every requested section has an export or an explicit blocker, and runs the chapter audit once the chapter is ready. Agent reports do not substitute for actual checks or whole-video user acceptance. Keep work uncommitted until the existing workflow's acceptance and authorization requirements are met.

## Prepare exact source-backed scripts

Read the selected source section and translation records. Require current reviewed Russian text for both body and headings; use the source and translation schemas under `data/homebrew/` when checking fingerprints. If missing/stale translations block a requested episode, record the issue and continue independent ready episodes. Do not fabricate approved translations or silently export Swedish-only text. Follow the existing translation workflow if translation work is in the user's scope.

For a new episode, from the repository root:

```sh
poetry run python studio/tools/script.py init SECTION_ID
```

For existing episodes, resume rather than rerunning initialization. If source fingerprints changed, reconcile affected IDs/text deliberately, log the revision, and invalidate affected audio/timing/render records without discarding unaffected curation.

Edit `studio/episodes/SECTION_ID/script.yaml`, using the current template and a completed episode as structural examples. Preserve exact source wording, stored sentence order, IDs, reviewed Russian text, provenance, and credits. Include every body sentence and list fragment once. The bilingual heading is unspoken. Put pronunciation expansions in speech-only overrides; never change display text or anthology content to accommodate synthesis.

Record episode-wide choices and sentence treatments in the script, including scenes, highlights, asset requests with honest fallbacks, pauses, and rendering configuration. Do not copy another episode's creative choices blindly. In particular, follow the current distinct chapter palette and distinct per-subchapter background/music requirements. Use accurate useful foreground imagery; omit captions when their foreground image is absent. Plan manually aligned bilingual segments when a sentence cannot fit legibly.

```sh
poetry run python studio/tools/script.py review SECTION_ID --ready
poetry run python studio/tools/script.py validate SECTION_ID --ready
```

Keep brief and inventory milestones synchronized. Passing validation means script readiness, not user approval. Continue authorized production without inventing stage-by-stage confirmation requirements.

## Prepare and verify assets and narration

Use root Poetry for source/script validation and the isolated media runtime documented in `ASSETS.md` for synthesis, image preparation, and rendering. Restore pinned dependencies/models with the current manifests; check available fonts and hardware rather than assuming historical macOS paths work on this host.

Resolve requested visuals and music with source URLs, creator, license, relevance/identity evidence, exact local paths and checksums. Keep raw sources unchanged and pin downloads. Use or adapt an episode-specific preparation helper when needed; shared map/asset helpers are not automatically suitable for every chapter. Validate generated labels and geography visually. Update creative choices in the script and file/provenance details in `assets.yaml`.

Use the current local Swedish production voice from `studio/TTS.md`. The existing production command shape is:

```sh
studio/runtime/.venv/bin/python studio/tools/audition.py supertonic \
  --voice F1 --speed .95 --section SECTION_ID --all \
  --output studio/media/SECTION_ID/narration
studio/runtime/.venv/bin/python studio/tools/check_audio.py \
  studio/media/SECTION_ID/narration --language sv --pattern 'hb-*.wav' --resume
```

Generate one WAV per source sentence, recording actual synthesis inputs, model/settings, hashes and measured durations. Build final timing from audio, not an arbitrary target length. Targeted retakes go to a separate folder: `audition.py --indices` writes subset metrics, so it must not overwrite the retained full narration set. Merge selected takes and metrics, then refresh affected asset hashes and mixes.

Check all sentences for audio integrity and diagnostic transcript differences. ASR cannot establish listening quality, accent, or correct pronunciation. Record uncertain names/numbers and unavailable listening checks honestly; carry these into whole-video review rather than imposing a separate user audio approval gate. Do not repeatedly resynthesize without a specific diagnostic or user-requested correction.

## Render, inspect, and deliver

Run from the repository root, substituting the resolved stable section ID:

```sh
studio/runtime/.venv/bin/python studio/tools/validate_assets.py SECTION_ID
studio/runtime/.venv/bin/python studio/tools/render.py SECTION_ID --stills-only
# Inspect frames and correct layout/asset problems before the full render.
studio/runtime/.venv/bin/python studio/tools/render.py SECTION_ID
studio/runtime/.venv/bin/python studio/tools/verify_render.py SECTION_ID --save-frames
poetry run python studio/tools/script.py review SECTION_ID --ready
poetry run python studio/tools/script.py validate SECTION_ID --ready
```

Inspect representative exported frames at laptop and phone size, especially long text, numbers, imagery, and credits. Verify full decode, streams/duration, sentence/timeline coverage, current audio mix, and continuous background motion across scene boundaries. Fix demonstrated failures and rerun affected checks. If tooling needs changes, run relevant source tests in `studio/tests` and media tests in `studio/runtime/tests` using their respective environments.

Keep canonical MP4 and matching credits in `videos/homebrew/`, using `studio/tools/outputs.py` and inventory subchapter order for filenames. Update production records and the video index; preserve selected narration WAVs and reproducible manifests, adding precise ignore exceptions when needed. Only remove superseded exports or temporary auditions according to current workflow and user authorization. For a fully rendered chapter, run `poetry run python studio/tools/audit_chapter.py CHAPTER_ID`.

Deliver links, durations and a concise account of checks and unresolved review items. Keep status `preview_ready` until whole-video review/acceptance actually occurs; never claim listening, device checks or user approval that did not happen. Keep production uncommitted until final-video acceptance and commit authorization as required by `WORKFLOW.md`, unless explicitly superseded by the user's instructions. If committing is authorized, refresh the combined deck with `make`, summarize the staged scope and follow the repository commit policy. Push only when authorized.

## Alternate Russian audio or audio-only revisions

When the request is only narration for an existing video, preserve its visual stream. Read the Russian alternate-audio section of `studio/TTS.md`, the episode's `render.json`, and existing `russian-narration.yaml`. The first episode is a working example, not proof that every episode already has the required configuration.

Use the separate `studio/runtime/narration` Poetry environment and pinned Russian model manifest. Prepare an episode-specific narration configuration against reviewed translations and the existing timeline before invoking `russian_narration.py SECTION_ID`. Use `--replace` only for an authorized replacement. Follow the current timing limits; never truncate sentences to fit. Keep speech-only stress hints and abbreviation expansions separate from displayed text. Validate audio duration, sentence order, scene fit and hashes, including the unchanged original video hash.

Export a `.ru.m4a` sidecar and matching production/credit records instead of duplicating the video. Existing study packaging supports shared-video HLS; an audio request alone does not authorize changing the player or deploying it. Other audio-only mix revisions follow `RENDERING.md`, preserving and verifying the original video stream.
