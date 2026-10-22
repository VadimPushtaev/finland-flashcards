import { useEffect, useRef, useState } from 'react';
import type Hls from 'hls.js';

export type VideoSource = {
  url: string;
  credits_url: string | null;
  format?: 'hls';
  audio_tracks?: { language: string; label: string; url: string }[];
};

export function VideoPlayer({ source, title }: { source: VideoSource; title: string }) {
  const video = useRef<HTMLVideoElement>(null);
  const position = useRef({ time: 0, playing: false, rate: 1 });
  const [language, setLanguage] = useState('sv');
  const [error, setError] = useState('');
  const [ready, setReady] = useState(false);
  const tracks = source.audio_tracks || [];
  const url = tracks.find(track => track.language === language)?.url || source.url;

  useEffect(() => {
    const element = video.current!;
    const saved = { ...position.current };
    let hls: Hls | undefined;
    let cancelled = false;
    setError('');
    setReady(false);
    const restore = () => {
      element.currentTime = saved.time;
      element.playbackRate = saved.rate;
    };
    const resume = () => {
      if (saved.playing) element.play().catch(() => { if (!cancelled) setError('Tryck på spela för att fortsätta.'); });
    };
    const start = () => { if (hls && !hls.loadingEnabled) hls.startLoad(element.currentTime || saved.time); };
    const failed = () => { if (!cancelled) setError('Videon kunde inte spelas upp. Försök ladda om sidan.'); };
    element.addEventListener('loadedmetadata', restore, { once: true });
    const nativePlayback = () => {
      element.addEventListener('error', failed);
      element.preload = saved.time > 0 ? 'metadata' : 'none';
      element.src = url;
      element.load();
      setReady(true);
      resume();
    };
    if (source.format !== 'hls') {
      nativePlayback();
    } else {
      import('hls.js').then(({ default: Hls }) => {
        if (cancelled) return;
        if (Hls.isSupported()) {
          hls = new Hls({ autoStartLoad: false });
          element.addEventListener('play', start, { once: true });
          hls.on(Hls.Events.MEDIA_ATTACHED, () => hls!.loadSource(url));
          hls.on(Hls.Events.MANIFEST_PARSED, () => {
            setReady(true);
            if (saved.time > 0) hls!.startLoad(saved.time);
            resume();
          });
          hls.on(Hls.Events.ERROR, (_, data) => { if (data.fatal) failed(); });
          hls.attachMedia(element);
        } else if (element.canPlayType('application/vnd.apple.mpegurl')) {
          nativePlayback();
        } else {
          setError('Den här webbläsaren stöder inte videons format. Prova en annan webbläsare.');
        }
      }).catch(() => { if (!cancelled) failed(); });
    }
    return () => {
      cancelled = true;
      position.current = element.readyState > 0
        ? { time: element.currentTime, playing: !element.paused, rate: element.playbackRate }
        : saved;
      element.removeEventListener('loadedmetadata', restore);
      element.removeEventListener('error', failed);
      element.removeEventListener('play', start);
      hls?.destroy();
      element.pause();
      element.removeAttribute('src');
      element.load();
    };
  }, [url, source.format]);

  return <figure className="section-video">
    {tracks.length > 1 && <label className="video-language">Ljudspråk
      <select className="form-select form-select-sm" value={language} disabled={!ready} onChange={event => setLanguage(event.target.value)}>
        {tracks.map(track => <option key={track.language} value={track.language}>{track.label}</option>)}
      </select>
    </label>}
    <video ref={video} controls={ready} aria-busy={!ready} playsInline preload="none" aria-label={`Video: ${title}`} />
    {error && <p role="alert">{error}</p>}
    <figcaption><span>Video · {title}</span>{source.credits_url && <a href={source.credits_url} target="_blank" rel="noreferrer">Videons källor och upphov</a>}</figcaption>
  </figure>;
}
